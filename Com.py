import random
from time import sleep
from threading import Thread
from pyeventbus3.pyeventbus3 import *

from Message import Message, MessageTo
from Token import Token, TokenState, TokenManager
from SyncingMessage import SyncingMessage
from BroadcastMessage import BroadcastMessage

class Com(Thread):


    def __init__(self, name: str, id : int, nbProcess: int):
        super().__init__()
        self.nbProcess = nbProcess
        self.name = name
        self.myId = id
        PyBus.Instance().register(self, self)
        self.alive = True
        self.horloge = 0  
        self.cptSynchronize = self.nbProcess-1

        self.token_state = TokenState.Null  
        self.mailbox = []  
        self.start()

    def next(self):
        return (self.myId + 1) % self.nbProcess

    def inc_clock(self, message: Message):
        self.horloge = max(self.horloge, message.horloge) + 1




    ########################SEND
    def sendMessage(self, message: Message):
        if not isinstance(message, Token) and not isinstance(message, SyncingMessage):
            self.horloge += 1
        print(f"{self.name} --- Envoi du message : {message.getPayload()}")
        print(message)
        PyBus.Instance().post(message)  

    def sendAll(self, payload: any):
        self.sendMessage(Message(payload))

    def sendTo(self, dest: str, payload: any):
        self.sendMessage(MessageTo(payload, self.name, dest))

    def broadcast(self, payload: any):
        message = BroadcastMessage(payload, self.name)
        self.sendMessage(message)

    ########################RECEIVE
    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event: BroadcastMessage):
        print(event.from_process, self.name)
        if event.from_process != self.name:
            self.receiveMessage(event)

    def receiveMessage(self, message: Message):

        if not isinstance(message, Token) and not isinstance(message, SyncingMessage) :
            print(f"{self.name}, j'ai reçu le message : {message.getPayload()} [Ajouté à la boîte aux lettres]")
            self.mailbox.append(message)
            self.inc_clock(message)
        else:
            print(f"{self.name}, j'ai reçu le message : {message.getPayload()}")

 
    @subscribe(threadMode=Mode.PARALLEL, onEvent=MessageTo)
    def onReceive(self, event: MessageTo):
        if event.to_process == self.name:
            self.receiveMessage(event)
    


    ########################TOKEN
    def startToken(self):
        self.sendTokentoNext()

        
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
        #print("EVENT RECU",event.from_process,event.to_process)
        if event.to_process == self.name:
            print(f"Token reçu par {event.from_process}.")

            if self.token_state == TokenState.Requested:
                self.token_state = TokenState.SC
                
               
            elif self.token_state == TokenState.Release:
                self.token_state = TokenState.Null
        
            self.sendTokentoNext()
               

    def sendTokentoNext(self):
        nextId = "P" + str(self.next())
        token = Token(self.name,nextId)
        #print("EVENT ENVOYE",token.from_process,token.to_process)

        print(f"{self.name} a envoyé le jeton à {nextId}.")
        sleep(5)
        self.sendMessage(token)


    ###################### Synchronisation
    def synchronize(self):
        PyBus.Instance().post(SyncingMessage(self.name))
        print("Synchronisation en attente pour",self.name)
        while self.cptSynchronize > 0:
            sleep(1)  # Sleep to avoid busy-waiting


        print("Je suis ",self.name," et je suis synchronisé")
        self.cptSynchronize = self.nbProcess - 1 
        

    @subscribe(threadMode=Mode.PARALLEL, onEvent=SyncingMessage)
    def onSyncing(self, event: SyncingMessage):
        # Ensure the process doesn't handle its own synchronization messages
        if event.from_process != self.name:
            self.receiveMessage(event)
            self.cptSynchronize -= 1
            print(self.name,self.cptSynchronize)


    ####################

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

    def stop(self):
        # self.token_manager.stop()
        self.alive = False
        self.join()