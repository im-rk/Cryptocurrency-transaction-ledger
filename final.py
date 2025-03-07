import time
import hashlib
import pymongo
import ecdsa
import base58

# MongoDB Connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["TransactionDB"]
users_collection = db["Users"] 
collection = db["Transactions"]  

def generate_wallet_address(username):
    """Generate a unique wallet address for a user if not already created."""
    existing_user = users_collection.find_one({"name": username})
    if existing_user:
        return existing_user["wallet_address"]
    
    private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    public_key = private_key.verifying_key.to_string()
    sha256_hash = hashlib.sha256(public_key).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_hash)
    public_key_hash = ripemd160.digest()
    versioned_payload = b'\x00' + public_key_hash
    checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
    wallet_address = base58.b58encode(versioned_payload + checksum).decode('utf-8')
    users_collection.insert_one({"name": username, "wallet_address": wallet_address})
    return wallet_address

class Transaction:
    def __init__(self, sender_address, receiver_address, amount):
        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.amount = amount
        self.timestamp = time.time()

    def __str__(self):
        return f"Sender: {self.sender_address}, Receiver: {self.receiver_address}, Amount: {self.amount}, Timestamp: {self.timestamp}"

class Node:
    def __init__(self, transaction, previous_hash=""):
        self.transaction = transaction
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
        self.next = None

    def calculate_hash(self):
        data = f"{self.transaction.sender_address}{self.transaction.receiver_address}{self.transaction.amount}{self.transaction.timestamp}{self.previous_hash}"
        return hashlib.sha256(data.encode()).hexdigest()

class TransactionLedger:
    def __init__(self):
        self.head = None
        self.tail = None

    def get_wallet_address(self, username):
        return generate_wallet_address(username)

    def add_transaction(self, sender, receiver, amount):
        sender_address = self.get_wallet_address(sender)
        receiver_address = self.get_wallet_address(receiver)
        transaction = Transaction(sender_address, receiver_address, amount)
        previous_hash = self.tail.hash if self.tail else "0"
        new_node = Node(transaction, previous_hash)
        if self.head is None:
            self.head = new_node
        else:
            self.tail.next = new_node
        self.tail = new_node
        transaction_data = {
            "sender_address": sender_address,
            "receiver_address": receiver_address,
            "amount": amount,
            "timestamp": transaction.timestamp,
            "hash": new_node.hash,
            "previous_hash": previous_hash
        }
        collection.insert_one(transaction_data)
        print(f"Transaction added:\n{transaction}")

    def verify_chain(self):
        current = self.head
        while current and current.next:
            if current.next.previous_hash != current.hash:
                return False
            current = current.next
        return True

    def display_ledger(self):
        transactions = collection.find()
        if collection.count_documents({}) == 0:
            print("The ledger is empty.")
            return
        print("\n===== Transaction Ledger =====\n")
        for txn in transactions:
            print(f"Transaction ID: {txn['hash'][:10]}")
            print(f"Sender Address: {txn['sender_address']}")
            print(f"Receiver Address: {txn['receiver_address']}")
            print(f"Amount: {txn['amount']}")
            print(f"Timestamp: {time.ctime(txn['timestamp'])}")
            print(f"Previous Hash: {txn['previous_hash']}\n")
            print("-" * 40)

obj = TransactionLedger()
# while True:
#     print("\nOptions: 1. Add Transaction  2. Display Ledger  3. Verify Ledger  4. Exit")
#     choice = input("Enter your choice: ")
#     if choice == "1":
#         sender = input("Sender name: ")
#         receiver = input("Receiver name: ")
#         try:
#             amount = float(input("Amount: "))
#             obj.add_transaction(sender, receiver, amount)
#         except ValueError:
#             print("Invalid amount! Please enter a valid number.")
#     elif choice == "2":
#         obj.display_ledger()
#     elif choice == "3":
#         print("Ledger Integrity Verified:", obj.verify_chain())
#     elif choice == "4":
#         print("THANK YOU")
#         break
#     else:
#         print("Invalid choice! Please enter a valid option.")