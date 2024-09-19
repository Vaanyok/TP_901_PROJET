from Message import Message
from enum import Enum
from threading import Thread
from time import sleep


class TokenState(Enum):
    Null = 1
    Requested = 2
    SC = 3
    Release = 4


class Token(Message):
    def __init__(self,from_process,to_process):
        Message.__init__(self, "Token")
        self.from_process = from_process
        self.to_process = to_process
        



class TokenManager(Thread):
    def __init__(self, com_instance):
        super().__init__()
        self.com_instance = com_instance
        self.alive = True
        self.token_available = False
        self.start()

    def run(self):
        while self.alive:
            if self.com_instance.token_state == TokenState.Requested:
                if self.token_available:
                    # Accorder la section critique
                    self.com_instance.token_state = TokenState.SC
                    print(f"{self.com_instance.name} a reçu le jeton et entre en section critique.")
                else:
                    print(f"{self.com_instance.name} attend le jeton.")
            sleep(1)

    def stop(self):
        self.alive = False
        self.join()

    def give_token(self):
        self.token_available = True

    def take_token(self):
        self.token_available = False