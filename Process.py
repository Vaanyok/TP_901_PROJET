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
        sleep(1)
        while self.alive:
            if loop==0 and self.name == "P1":
                 self.broadcast("PMSG")
            if loop==1 and self.name == "P2":
                self.sendTo("P1","P2 for P1")
            if loop==2:
                self.synchronization()
            if loop==3 :
                self.synchronization()
            loop += 1
            sleep(2)  # Ajout d'un délai pour éviter une boucle trop rapide

    # Diffusion des messages asynchrones
    def broadcast(self, message : any):
        super().broadcast(message)

    
    def sendTo(self, dest: str, payload: any):
        super().sendTo(dest,payload)


    def testToken(self):
        if(super().name == "P1"):
            super().startToken()
            super().requestSC()
            sleep(5)
        if(super().name == "P2"):
            super().requestSC()

    def synchronization(self):
        super().synchronize()      