import random
from time import sleep
from typing import Callable

from pyeventbus3.pyeventbus3 import *

from Message import Message, MessageTo
from Token import Token, TokenState
from SyncingMessage import SyncingMessage
from BroadcastMessage import BroadcastMessage

def mod(x: int, y: int) -> int:
    return ((x % y) + y) % y


class Process(Message):
    def __init__(self, name: str, nbProcess: int):
        super().__init__(name : str,nbProcess : int)  # Properly call the parent constructor using super()

    def run(self):
        while self.nbProcess != Process.nbProcessCreated:
            pass
        if self.myId == 0:
            self.releaseToken()
        self.synchronize()
        loop = 0
        while self.alive:
            sleep(1)

            # if self.name == "P1":
            #     self.sendTo("P2", "ga")
            #     self.doCriticalAction(self.criticalActionWarning, ["BDG"])
            # if self.name == "P2":
            #     self.broadcast("P2 broadcast")
            # if self.name == "P3":
            #     receiver = str(random.randint(0, self.nbProcess - 1))
            #     self.sendTo("P" + receiver, "j'envoi sms" + receiver)
            loop += 1
        sleep(1)
