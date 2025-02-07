import time 
import hashlib
class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = time.time()  #used to record the time
    
    def __str__(self):
        return f"Sender: {self.sender}, Receiver: {self.receiver}, Amount: {self.amount}, Timestamp: {self.timestamp}"
    
class Node:
    def __init__(self, transaction, previous_hash=""):
        self.transaction = transaction
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
        self.next = None  # It is a pointer which point to the next node.
    
    def calculate_hash(self):
        data = f"{self.transaction}{self.previous_hash}{self.transaction.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()

class TransactionLedger:
    def __init__(self):
        self.head = None  # Point to the start of the linked list
        self.tail = None  # Point to the end of the linked list
    
    def add_transaction(self, sender, receiver, amount):
        transaction = Transaction(sender, receiver, amount)
        previous_hash = self.tail.hash if self.tail else "0"
        new_node = Node(transaction, previous_hash)
        
        #to add the node to the linked list
        if self.head is None:
            self.head = new_node
        else:
            self.tail.next = new_node
        self.tail = new_node
        
        print(f"Transaction added:\n{transaction}")
    
    def verify_chain(self):
        current = self.head
        while current and current.next:
            if current.hash != current.next.previous_hash:
                return False  # Chain is broken
            current = current.next
        return True
    
    def display_ledger(self):
        current = self.head
        while current:
            print(f"Transaction: {current.transaction}\nHash: {current.hash}\n")
            current = current.next
