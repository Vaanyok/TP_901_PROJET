import random
from time import sleep
from threading import Thread
from pyeventbus3.pyeventbus3 import *

from Message import Message, MessageTo
from Token import Token, TokenState
from Com import Com


class Process(Com):
    nbProcessCreated = 0

    def __init__(self, name: str, id:int,  nbProcess: int):
        super().__init__(name, id,nbProcess)  # Utilisation correcte de super()
        

    def run(self):
        loop = 0
        
        while self.alive:
            
            # if loop==0 and self.name == "P1":
            #      self.broadcast("PMSG")
            #########
            # if loop==1 and self.name == "P2":
            #     self.sendTo("P1","P2 for P1")
            # if loop==2:
            # #########
            #     self.synchronization()
            # if loop==3 :
            #     self.broadcastSync()
            # #########
            if loop==4 and self.name == "P2":
                self.sendToSync(3)
            if loop==4 and self.name == "P3":
                self.recevFromSync(2)
            loop += 1
            sleep(10)  # Ajout d'un délai pour éviter une boucle trop rapide
        self.showMessages()

    # Method to broadcast asynchronous messages
    def broadcast(self, message: any):
        super().broadcast(message)

    # Method to send a message to a specific destination
    def sendTo(self, dest: str, payload: any):
        super().sendTo(dest, payload)

    # Test token method for process synchronization
    def testToken(self):
        if super().name == "P1":
            super().startToken()  # Start the token for process P1
            super().requestSC()    # Request a critical section
            sleep(5)  # Wait for 5 seconds
        if super().name == "P2":
            super().requestSC()  # Request a critical section for P2

    # Method to handle synchronization
    def synchronization(self):
        super().synchronize()     

    # Method to broadcast a synchronized message
    def broadcastSync(self):
        super().broadcastSync("Broadcast sync", 1)

    # Method to send a synchronized message to a specific destination
    def sendToSync(self, dest):
        super().sendToSync("Message to sync", dest)

    # Method to receive synchronized messages from a specific source
    def recevFromSync(self, From):
        super().recevFromSync(Message(""), From)

    # Method to display messages and contacts
    def showMessages(self):
        print("I am", super().name, "and here are my contacts", self.contact)
        for i in range(len(self.mailbox)):
            print(super().lireMessage().getPayload())  # Read messages in the mailbox
