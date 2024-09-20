import random
from time import sleep
from threading import Thread
from pyeventbus3.pyeventbus3 import *

from Message import Message, MessageTo, SyncMessageTo
from Token import Token, TokenState, TokenManager
from SyncingMessage import SyncingMessage
from BroadcastMessage import BroadcastMessage, BroadcastMessageSync
from Numerotation import Numerotation, MyContact

class Com(Thread):
    """
    Represents a communication process in a distributed system.
    
    Attributes:
        nbProcess (int): Total number of processes in the system.
        nbProcess2 (int): Count of currently known processes.
        name (str): Name of the process.
        myId (int): Unique identifier for the process.
        alive (bool): Indicates if the process is running.
        horloge (int): Logical clock for synchronization.
        mailbox (list): List of received messages.
        contact (list): List of known contacts.
        mup (int): Upper limit for random PID generation.
        receivedSyncMsg (bool): Flag indicating if a sync message has been received.
        pid (int): Process ID.
    """

    def __init__(self, name: str, id: int, nbProcess: int):
        """
        Initializes the communication process.
        
        Args:
            name (str): Name of the process.
            id (int): Unique identifier for the process.
            nbProcess (int): Total number of processes in the system.
        """
        super().__init__()
        self.nbProcess = nbProcess
        self.nbProcess2 = 0 
        self.name = name
        self.myId = id
        PyBus.Instance().register(self, self)
        self.alive = True
        self.horloge = 0  
        self.cptSynchronize = self.nbProcess - 1
        self.Msgobject = None
        self.token_state = TokenState.Null  
        self.mailbox = []  
        self.contact = []
        self.mup = 1000

        self.start()
        self.receivedSyncMsg = False

        self.pid = None
        sleep(2)
        self.chooseNumerotation()
        sleep(5)

    def next(self):
        """
        Returns the ID of the next process in a circular manner.
        
        Returns:
            int: ID of the next process.
        """
        return (self.myId + 1) % self.nbProcess

    def nextPid(self):
        """
        Finds and returns the PID of the next contact in the contact list.
        
        Returns:
            int: PID of the next contact, or None if not found.
        """
        for i, contact in enumerate(self.contact):
            if contact["pid"] == self.pid:
                return self.contact[(i + 1) % len(self.contact)]["pid"]

    def findPidWithName(self, name_process: str):
        """
        Finds a process by name and returns its PID.
        
        Args:
            name_process (str): Name of the process to find.
        
        Returns:
            int or None: PID of the process, or None if not found.
        """
        for contact in self.contact:
            if contact["name"] == name_process:
                return contact["pid"]
        return None

    def inc_clock(self, message: Message):
        """
        Increments the logical clock based on the received message's clock.
        
        Args:
            message (Message): The message whose clock is to be considered.
        """
        self.horloge = max(self.horloge, message.horloge) + 1

    def lireMessage(self) -> Message:
        """
        Reads and removes the first message from the mailbox.
        
        Returns:
            Message: The first message in the mailbox.
        """
        return self.mailbox.pop(0).getPayload()

    def addContact(self, pid: int, name_process: str):
        """
        Adds a contact to the process's contact list.
        
        Args:
            pid (int): PID of the new contact.
            name_process (str): Name of the new contact.
        """
        if any(contact["pid"] == pid for contact in self.contact):
            return  # Exit if the contact already exists
        
        self.contact.append({"pid": pid, "name": name_process})
        self.contact.sort(key=lambda contact: contact["pid"])
        self.nbProcess2 = len(self.contact) + 1

    ########################SEND
    def sendMessage(self, message: Message):
        """
        Sends a message to the message bus.
        
        Args:
            message (Message): The message to be sent.
        """
        if not isinstance(message, Token) and not isinstance(message, SyncingMessage):
            self.horloge += 1
        print(f"{self.name} --- Sending message: {message.getPayload()}")
        PyBus.Instance().post(message)  

    def sendAll(self, payload: any):
        """
        Sends a message to all processes.
        
        Args:
            payload (any): The payload of the message.
        """
        self.sendMessage(Message(payload))

    def sendTo(self, dest: str, payload: any):
        """
        Sends a message to a specific process.
        
        Args:
            dest (str): Name of the destination process.
            payload (any): The payload of the message.
        """
        self.sendMessage(MessageTo(payload, self.name, dest))

    def broadcast(self, payload: any):
        """
        Broadcasts a message to all processes.
        
        Args:
            payload (any): The payload of the broadcast message.
        """
        message = BroadcastMessage(payload, self.name)
        self.sendMessage(message)

    ########################RECEIVE
    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event: BroadcastMessage):
        """
        Handles incoming broadcast messages.
        
        Args:
            event (BroadcastMessage): The broadcast message received.
        """
        print(event.from_process, self.name)
        if event.from_process != self.name:
            self.receiveMessage(event)

    def receiveMessage(self, message: Message):
        """
        Processes a received message and adds it to the mailbox.
        
        Args:
            message (Message): The received message.
        """
        if not isinstance(message, Token) and not isinstance(message, SyncingMessage):
            print(f"{self.name}, received message: {message.getPayload()} [Added to mailbox]")
            self.mailbox.append(message)
            self.inc_clock(message)
        else:
            print(f"{self.name}, received message: {message.getPayload()}")

    @subscribe(threadMode=Mode.PARALLEL, onEvent=MessageTo)
    def onReceive(self, event: MessageTo):
        """
        Handles incoming directed messages.
        
        Args:
            event (MessageTo): The directed message received.
        """
        if event.to_process == self.name:
            self.receiveMessage(event)

    ########################TOKEN
    def startToken(self):
        """
        Initiates the process of sending the token to the next process.
        """
        self.sendTokentoNext()

    def requestSC(self):
        """
        Requests access to the critical section.
        """
        print(f"{self.name} requests the critical section.")
        self.token_state = TokenState.Requested

    def releaseSC(self):
        """
        Releases the critical section.
        """
        print(f"{self.name} releases the critical section.")
        self.token_state = TokenState.Release
        self.sendTokentoNext()

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Token)
    def manageToken(self, event: Token):
        """
        Manages the received token.
        
        Args:
            event (Token): The token received.
        """
        if event.to_process == self.name:
            print(f"Token received from {event.from_process}.")
            if self.token_state == TokenState.Requested:
                self.token_state = TokenState.SC
            elif self.token_state == TokenState.Release:
                self.token_state = TokenState.Null
            self.sendTokentoNext()

    def sendTokentoNext(self):
        """
        Sends the token to the next process.
        """
        nextId = "P" + str(self.next())
        token = Token(self.name, nextId)
        print(f"{self.name} sent token to {nextId}.")
        sleep(5)
        self.sendMessage(token)

    ###################### Synchronisation
    def synchronize(self):
        """
        Initiates synchronization among processes.
        """
        PyBus.Instance().post(SyncingMessage(self.name))
        print("Synchronization waiting for", self.name)
        while self.cptSynchronize > 0:
            sleep(1)

        print("I am ", self.name, " and I am synchronized")
        self.cptSynchronize = self.nbProcess - 1 

    @subscribe(threadMode=Mode.PARALLEL, onEvent=SyncingMessage)
    def onSyncing(self, event: SyncingMessage):
        """
        Handles synchronization messages.
        
        Args:
            event (SyncingMessage): The synchronization message received.
        """
        if event.from_process != self.name:
            self.receiveMessage(event)
            self.cptSynchronize -= 1
            print(self.name, self.cptSynchronize)

    #################### Broadcast sync 
    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessageSync)
    def onBroadcastSync(self, event: BroadcastMessageSync):
        """
        Handles incoming broadcast sync messages.
        
        Args:
            event (BroadcastMessageSync): The broadcast sync message received.
        """
        if event.from_process != self.myId:
            self.receiveMessage(event)
            self.receivedSyncMsg = True

    def broadcastSync(self, payload: any, From: int):
        """
        Broadcasts a sync message and handles synchronization.
        
        Args:
            payload (any): The payload of the sync message.
            From (int): The PID of the process broadcasting.
        """
        if self.myId == From:
            self.sendMessage(BroadcastMessageSync(payload, From))
            self.synchronize()
        else:
            while not self.receivedSyncMsg:
                sleep(1)
            self.synchronize()
            self.receivedSyncMsg = False
          
    #################### Message Sync 

    def sendToSync(self, payload: any, dest: int):
        """
        Sends a sync message to a specific destination process.
        
        Args:
            payload (any): The payload of the sync message.
            dest (int): The destination process ID.
        """
        destName = "P" + str(dest)
        message = SyncMessageTo(payload, self.name, destName)
        self.sendMessage(message)
        while not self.receivedSyncMsg:
            sleep(1)
        print("Message sent successfully, receipt confirmed")
        self.receivedSyncMsg = False

    @subscribe(threadMode=Mode.PARALLEL, onEvent=SyncMessageTo)
    def recevSync(self, event: SyncMessageTo):
        """
        Handles received sync messages.
        
        Args:
            event (SyncMessageTo): The sync message received.
        """
        if event.to_process == self.name:
            self.receivedSyncMsg = True
            self.Msgobject = event

    def recevFromSync(self, Object: Message, From: int):
        """
        Confirms receipt of a sync message and sends a confirmation message.
        
        Args:
            Object (Message): The sync message object.
            From (int): The PID of the sender.
        """
        while not self.receivedSyncMsg:
            sleep(1)
        fromName = "P" + str(From)
        print("Receipt confirmed")
        message = SyncMessageTo("Message from sync", self.name, fromName)
        self.sendMessage(message)
        self.receivedSyncMsg = False
        Object = self.Msgobject

    ###################

    def waitStopped(self):
        """
        Waits for the thread to finish execution.
        """
        self.join()

    def stop(self):
        """
        Stops the process and waits for the thread to finish.
        """
        self.alive = False
        self.join()

    ##################### Numérotation

    def chooseNumerotation(self):
        """
        Chooses a process ID, ensuring no conflicts with existing PIDs.
        """
        if self.name == "P0":
            self.pid = 0
        else:
            self.pid = random.randint(0, self.mup)
        self.sendMessage(Numerotation(self.pid, self.name))

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Numerotation)
    def onNumerotation(self, event: Numerotation):
        """
        Handles PID assignment and conflict resolution.
        
        Args:
            event (Numerotation): The PID assignment message received.
        """
        if event.pid == self.pid and self.name != event.from_process_name:
            print(f"PID conflict detected for {self.name}. Generating a new PID.")
            self.mup *= 2
            self.chooseNumerotation()
        else:
            print(f"Process {self.name} received PID {event.pid} from {event.from_process_name}.")
            self.addContact(event.pid, event.from_process_name)
            self.sendToAnnuaire()

    def sendToAnnuaire(self):
        """
        Sends the current process's information to the directory.
        """
        self.sendMessage(MyContact(self.pid, self.name))

    @subscribe(threadMode=Mode.PARALLEL, onEvent=MyContact)
    def onReceiveAnnuaire(self, event: MyContact):
        """
        Handles received directory messages.
        
        Args:
            event (MyContact): The directory message received.
        """
        if self.name != event.from_process_name:
            self.addContact(event.pid, event.from_process_name)
