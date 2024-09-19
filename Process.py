import random
from time import sleep
from threading import Thread
from pyeventbus3.pyeventbus3 import *

from Message import Message, MessageTo
from Token import Token, TokenState
from Com import Com


class Process(Com):
    nbProcessCreated = 0

    def __init__(self, name: str, nbProcess: int):
        super().__init__(name, nbProcess)  # Utilisation correcte de super()

    def run(self):
        loop = 0
        while self.alive:
            if self.name == "P1":
                self.broadcast("PMSG")
            loop += 1
            sleep(1)  # Ajout d'un délai pour éviter une boucle trop rapide

    # Diffusion des messages asynchrones
    def broadcast(self, message : any):
        super().broadcast(message)
