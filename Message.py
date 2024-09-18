
class Message():
    def __init__(self, obj: any):
        self.object = obj
        self.horloge = None

    def getObject(self: any):
        return self.object



class MessageTo(Message):  # Inherit from Message
    def __init__(self, obj: any, from_process: str, to_process: str):
        super().__init__(obj)  # Properly call the parent constructor using super()
        self.from_process = from_process
        self.to_process = to_process

    def getObject(self):
        return super().getObject()  # Call the parent class's getObject method