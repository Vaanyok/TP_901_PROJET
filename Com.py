import random
from time import sleep
from threading import Thread
from pyeventbus3.pyeventbus3 import *

from Message import Message, MessageTo
from Token import Token, TokenState, TokenManager
from SyncingMessage import SyncingMessage
from BroadcastMessage import BroadcastMessage

class Com(Thread):


    def __init__(self, name: str, nbProcess: int):
        super().__init__()
        self.nbProcess = nbProcess
    
        self.name = name

        PyBus.Instance().register(self, self)

        self.alive = True
        self.horloge = 0  
        self.token_state = TokenState.Null  
        self.mailbox = []  

        # if(self.name=="P0"):
        #     self.token_manager = TokenManager(self)

        self.start()

    @staticmethod
    def next(x: int, y: int) -> int:
        return (x + 1) % y



    def inc_clock(self, message: Message):
        self.horloge = max(self.horloge, message.horloge) + 1


    def stop(self):
        # self.token_manager.stop()
        self.alive = False
        self.join()



    #SEND
    def sendMessage(self, message: Message):
        if not isinstance(message, Token):
            self.horloge += 1
        print(f"{self.name} --- Envoi du message : {message.getPayload()}")
        print(message)
        PyBus.Instance().post(message)  

    def sendAll(self, payload: any):
        self.sendMessage(Message(payload))

    def sendTo(self, dest: str, payload: any):
        self.sendMessage(MessageTo(payload, self.name, dest))


    #RECEIVE
    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event: BroadcastMessage):
        print(event.from_process, self.name)
        if event.from_process != self.name:
            self.receiveMessage(event)

    def receiveMessage(self, message: Message):
        if not isinstance(message, Token):
            print(f"{self.name}, j'ai reçu le message : {message.getPayload()} [Ajouté à la boîte aux lettres]")
            self.mailbox.append(message)
            self.inc_clock(message)
 

    def broadcast(self, payload: any):
        message = BroadcastMessage(payload, self.name)
        self.sendMessage(message)

    # Gestion de la demande de section critique
    def requestSC(self):
        print(f"{self.name} demande la section critique.")
        self.token_state = TokenState.Requested

    # Gestion de la libération de la section critique
    def releaseSC(self):
        print(f"{self.name} libère la section critique.")
        self.token_state = TokenState.Release
        self.sendTokentoNext()

    # Gestion du jeton
    @subscribe(threadMode=Mode.PARALLEL, onEvent=Token)
    def manageToken(self, event: Token):
        if event.to_process == self.name:
            print(f"Token reçu par {event.from_process}.")
            #self.token_manager.give_token()

            if self.token_state == TokenState.Requested:
                self.token_state = TokenState.SC
            elif self.token_state == TokenState.Release:
                self.token_state = TokenState.Null
                self.sendTokentoNext()

    def sendTokentoNext(self):
        nextId = Com.next(self.myId, self.nbProcess)
        token = Token()
        token.to_process = nextId
        self.sendMessage(token)
        self.token_manager.take_token()
        print(f"{self.name} a envoyé le jeton à {nextId}.")

    # Synchronisation
    def synchronize(self):
        PyBus.Instance().post(SyncingMessage(self.myId))

    @subscribe(threadMode=Mode.PARALLEL, onEvent=SyncingMessage)
    def onSyncing(self, event: SyncingMessage):
        if event.from_process != self.myId:
            self.receiveMessage(event)

    def broadcastSync(self, payload: any, from_process: int):
        if self.myId == from_process:
            self.broadcast(payload)
            self.synchronize()
        else:
            while not self.mailbox:
                sleep(1)
            print(f"Message synchronisé reçu par {self.name}")
            self.synchronize()

    def waitStopped(self):
        self.join()
