from Message import Message
class Numerotation(Message):  # Inherit from Message
    def __init__(self, pid: int, from_process_name : int):
        super().__init__("Changing number")
        self.pid = pid
        self.from_process_name = from_process_name

    def getPayload(self):
        return super().getPayload() 



class MyContact(Message):  # Inherit from Message
    def __init__(self, pid: int, from_process_name : int):
        super().__init__("Sending my contact")
        self.pid = pid
        self.from_process_name = from_process_name

    def getPayload(self):
        return super().getPayload() 


