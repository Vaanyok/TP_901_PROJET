from Message import Message

class BroadcastMessage(Message):
    def __init__(self, obj: any, from_process: str):
        super().__init__(obj)
        self.from_process = from_process

    def getPayload(self):
        return super().getPayload() 