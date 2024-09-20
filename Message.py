
class Message():
    def __init__(self, payload: any):
        self.payload = payload
        self.horloge = 0

    def getPayload(self: any):
        return self.payload



class MessageTo(Message):  # Inherit from Message
    def __init__(self, obj: any, from_process: str, to_process: str):
        super().__init__(obj)  # Properly call the parent constructor using super()
        self.from_process = from_process
        self.to_process = to_process

    def getPayload(self):
        return super().getPayload() 


class SyncMessageTo(Message):  # Inherit from Message
    def __init__(self, obj: any, from_process: str, to_process: str):
        super().__init__(obj)  # Properly call the parent constructor using super()
        self.from_process = from_process
        self.to_process = to_process

    def getPayload(self):
        return super().getPayload() 