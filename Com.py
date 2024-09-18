import random
from time import sleep
from threading import Thread
from pyeventbus3.pyeventbus3 import *

from Message import Message, MessageTo
from Token import Token, TokenState
from SyncingMessage import SyncingMessage
from BroadcastMessage import BroadcastMessage


class Com(Thread):
    # Fonction modulaire
    @staticmethod
    def mod(x: int, y: int) -> int:
        return ((x % y) + y) % y

    # Fonction pour obtenir le suivant dans l'anneau
    @staticmethod
    def next(x: int, y: int) -> int:
        return (x + 1) % y
        
    nbProcessCreated = 0

    def __init__(self, name: str, nbProcess: int):
        Thread.__init__(self)
        self.nbProcess = nbProcess
        self.myId = Com.nbProcessCreated
        Com.nbProcessCreated += 1
        self.name = name

        PyBus.Instance().register(self, self)

        self.alive = True
        self.horloge = 0
        self.token_state = TokenState.Null
        self.nbSync = 0
        self.isSyncing = False
        self.mailbox = []

        self.start()  # Démarrer le thread

    def stop(self):
        self.alive = False
        self.join()

    def inc_clock(self, message: Message):
        self.horloge = max(self.horloge, message.horloge) + 1

    def sendMessage(self, message: Message):
        self.horloge += 1
        print(f"Je suis {self.name} --- Message : {message.getPayload()}")
        PyBus.Instance().post(message)

    def receiveMessage(self, message: Message):
        print(f"Je suis {self.name}, j'ai reçu *Message : {message.getPayload()} [Added to mailbox]")
        self.mailbox.append(message)
        self.inc_clock(message)

    def sendAll(self, payload: any):
        self.sendMessage(Message(payload))

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Message)
    def process(self, event: Message):
        self.receiveMessage(event)

    def broadcast(self, payload: any):
        self.sendMessage(BroadcastMessage(payload, self.name))

    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event: BroadcastMessage):
        if event.from_process != self.name:
            self.receiveMessage(event)

    def sendTo(self, dest: str, payload: any):
        self.sendMessage(MessageTo(payload, self.name, dest))

    @subscribe(threadMode=Mode.PARALLEL, onEvent=MessageTo)
    def onReceive(self, event: MessageTo):
        if event.to_process == self.name:
            self.receiveMessage(event)

    # Section critique
    def releaseSC(self):
        self.token_state = TokenState.Release

    def requestSC(self):
        while self.token_state != TokenState.SC:
            sleep(1)
        self.token_state = TokenState.Requested

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Token)
    def manageToken(self, event: Token):
        if event.to_process == self.myId:
            self.receiveMessage(event)
            if not self.alive:
                return
            if self.token_state == TokenState.Requested:
                self.token_state = TokenState.SC
                return
            self.token_state = TokenState.Null
            self.sendTokentoNext()

    def sendTokentoNext(self):
        nextId = Com.next(self.myId, self.nbProcess)
        self.sendMessage(Token(nextId))

    def synchronize(self):
        PyBus.Instance().post(SyncingMessage(self.myId))

    @subscribe(threadMode=Mode.PARALLEL, onEvent=SyncingMessage)
    def onSyncing(self, event: SyncingMessage):
        if event.from_process != self.myId:
            self.receiveMessage(event)
            self.nbSync = 0

    def broadcastSync(self, payload: any, From: int):
        if self.myId == From:
            self.broadcast(payload)
            self.synchronize()
        else:
            while not self.mailbox:
                sleep(1)
            print("Message synchronisé reçu")
            self.synchronize()

    def waitStopped(self):
        self.join()
