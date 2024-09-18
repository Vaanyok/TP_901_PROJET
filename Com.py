import random
from time import sleep
from typing import Callable

from pyeventbus3.pyeventbus3 import *

from Message import Message, MessageTo
from Token import Token, TokenState
from SyncingMessage import SyncingMessage
from BroadcastMessage import BroadcastMessage

class Com(Thread):


    nbProcessCreated = 0

    def __init__(self, name: str, nbProcess: int):
        Thread.__init__(self)

        self.nbProcess = nbProcess
        self.myId = Process.nbProcessCreated
        Process.nbProcessCreated += 1
        self.name = name

        PyBus.Instance().register(self, self)

        self.alive = True
        self.horloge = 0
        self.token_state = TokenState.Null
        self.nbSync = 0
        self.isSyncing = False
        self.start()



    def stop(self):
        self.alive = False
        self.join()

    def sendMessage(self, message: Message):
        self.horloge += 1
        message.horloge = self.horloge
        print(Message)
        print("Je suis", self.name, " ---Message :", message.getObject())
        PyBus.Instance().post(message)

    #@subscribe(threadMode=Mode.PARALLEL, onEvent=sendMessage)
    def receiveMessage(self, message: Message):
        print("Je suis", self.name, " j'ai reçu ---Message :", message.getObject())
        self.horloge = max(self.horloge, message.horloge) + 1

    def sendAll(self, obj: any):
        self.sendMessage(Message(obj))

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Message)
    def process(self, event: Message):
        self.receiveMessage(event)

    def broadcast(self, obj: any):
        self.sendMessage(BroadcastMessage(obj, self.name))

    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event: BroadcastMessage):
        if event.from_process != self.name:
            self.receiveMessage(event)

    def sendTo(self, dest: str, obj: any):
        self.sendMessage(MessageTo(obj, self.name, dest))

    @subscribe(threadMode=Mode.PARALLEL, onEvent=MessageTo)
    def onReceive(self, event: MessageTo):
        if event.to_process == self.name:
            self.receiveMessage(event)

    def releaseToken(self):
        if self.token_state == TokenState.SC:
            self.token_state = TokenState.Release
        token = Token()
        token.from_process = self.myId
        token.to_process = mod(self.myId + 1, Process.nbProcessCreated)
        token.nbSync = self.nbSync
        self.sendMessage(token)
        self.token_state = TokenState.Null

    def requestToken(self):
        self.token_state = TokenState.Requested
        while self.token_state == TokenState.Requested:
            if not self.alive:
                return
        self.token_state = TokenState.SC

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Token)
    def onToken(self, event: Token):
        if event.to_process == self.myId:
            self.receiveMessage(event)
            if not self.alive:
                return
            if self.token_state == TokenState.Requested:
                self.token_state = TokenState.SC
                return
            if self.isSyncing:
                self.isSyncing = False
                self.nbSync = mod(event.nbSync + 1, Process.nbProcessCreated)
                if self.nbSync == 0:
                    self.sendMessage(SyncingMessage(self.myId))
            self.releaseToken()

    def doCriticalAction(self, funcToCall: Callable, args: list):
        self.requestToken()
        if self.alive:
            funcToCall(*args)
            self.releaseToken()

    def criticalActionWarning(self, msg: str):
        print("[Critical Action], Token used by", self.name, " ---Message :", msg)

    def synchronize(self):
        self.isSyncing = True
        while self.isSyncing:
            if not self.alive:
                return
        while self.nbSync != 0:
            if not self.alive:
                return

    @subscribe(threadMode=Mode.PARALLEL, onEvent=SyncingMessage)
    def onSyncing(self, event: SyncingMessage):
        if event.from_process != self.myId:
            self.receiveMessage(event)
            self.nbSync = 0

    def broadcastSync()
    def stop(self):
        self.alive = False

    def waitStopped(self):
        self.join()
