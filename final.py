import time
import hashlib
import pymongo
import ecdsa
import base58
from datetime import datetime
from typing import List
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["TransactionDB"]
users_collection = db["Users"]
collection = db["Transactions"]

def generate_wallet_address(username):
    existing_user = users_collection.find_one({"name": username})
    if existing_user:
        return existing_user["wallet_address"]
    
    __private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    public_key = __private_key.verifying_key.to_string()
    sha256_hash = hashlib.sha256(public_key).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_hash)
    public_key_hash = ripemd160.digest()
    versioned_payload = b'\x00' + public_key_hash
    checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
    wallet_address = base58.b58encode(versioned_payload + checksum).decode('utf-8')
    users_collection.insert_one({"name": username, "wallet_address": wallet_address, "balance": 1000.0})
    return wallet_address


class MerkleTree:
    def __init__(self, transactions: List[dict]):
        self.leaves = [self._hash_transaction(txn) for txn in transactions]
        self.root = self._build_merkle_tree(self.leaves) if self.leaves else None

    def _hash_transaction(self, txn: dict) -> str:
        data = f"{txn['sender_address']}{txn['receiver_address']}{txn['amount']}{txn['timestamp']}"
        return hashlib.sha256(data.encode()).hexdigest()

    def _build_merkle_tree(self, leaves: List[str]) -> str:
        if not leaves:
            return None
        if len(leaves) == 1:
            return leaves[0]

        if len(leaves) % 2 != 0:
            leaves.append(leaves[-1])

        new_level = []
        for i in range(0, len(leaves), 2):
            combined = leaves[i] + leaves[i + 1]
            new_hash = hashlib.sha256(combined.encode()).hexdigest()
            new_level.append(new_hash)

        return self._build_merkle_tree(new_level)

    def get_root(self) -> str:
        return self.root
    

class Transaction:
    def __init__(self, sender_address, receiver_address, amount):
        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.amount = amount
        self.timestamp = datetime.now().isoformat()  

    def __str__(self):
        return f"Sender: {self.sender_address}, Receiver: {self.receiver_address}, Amount: {self.amount}, Timestamp: {self.timestamp}"

class BlockchainComponent:
    def calculate_hash(self, sender, receiver, amount, timestamp, previous_hash):
        data = f"{sender}{receiver}{amount}{timestamp}{previous_hash}"
        return hashlib.sha256(data.encode()).hexdigest()

class Node(BlockchainComponent):
    def __init__(self, transaction, previous_hash=""):
        self.transaction = transaction
        self.__previous_hash = previous_hash
        self.__hash = self.calculate_hash(transaction.sender_address, transaction.receiver_address, transaction.amount, transaction.timestamp, previous_hash)
        self.next = None

    def get_hash(self):
        return self.__hash

    def get_previous_hash(self):
        return self.__previous_hash

class TransactionLedger(BlockchainComponent):
    def __init__(self):
        self.head = None
        self.tail = None
        self.load_previous_transactions()

    def load_previous_transactions(self):
        transactions = list(collection.find({}))
        previous_node = None
        for txn in transactions:
            transaction = Transaction(txn["sender_address"], txn["receiver_address"], txn["amount"])
            transaction.timestamp = txn["timestamp"]  

            node = Node(transaction, txn["previous_hash"])
            node.__hash = txn["hash"]

            if self.head is None:
                self.head = node

            if previous_node:
                previous_node.next = node

            previous_node = node

        self.tail = previous_node

    def get_wallet_address(self, username):
        return generate_wallet_address(username)
    def get_balance(self, username):
        user = users_collection.find_one({"name": username})
        return user.get("balance", 0.0) if user else 0.0

    def add_transaction(self, sender, receiver, amount):
        sender_address = self.get_wallet_address(sender)
        receiver_address = self.get_wallet_address(receiver)
        transaction = Transaction(sender_address, receiver_address, amount)
        previous_hash = self.tail.get_hash() if self.tail else "0"
        new_node = Node(transaction, previous_hash)

        if self.head is None:
            self.head = new_node
        else:
            self.tail.next = new_node

        self.tail = new_node
        users_collection.update_one(
                {"wallet_address": sender_address},
                {"$inc": {"balance": -amount}}
            )
        users_collection.update_one(
            {"wallet_address": receiver_address},
            {"$inc": {"balance": amount}}
        )

        transaction_data = {
            "sender_address": sender_address,
            "receiver_address": receiver_address,
            "amount": amount,
            "timestamp": transaction.timestamp,  
            "hash": new_node.get_hash(),
            "previous_hash": previous_hash
        }
        collection.insert_one(transaction_data)
        print(f"Transaction added:\n{transaction}")
        all_transactions = list(collection.find().sort("timestamp", 1))
        merkle_tree = MerkleTree(all_transactions)
        db["merkle_roots"].insert_one({"root": merkle_tree.get_root(), "timestamp": transaction.timestamp})

    def search_transactions(self, search_type, value, user_wallet=None):
        results = []
        current = self.head
        try:
            if search_type == "amount":
                value = float(value)  
            while current:
                txn = current.transaction
                txn_data = {
                    "sender_address": txn.sender_address,
                    "receiver_address": txn.receiver_address,
                    "amount": txn.amount,
                    "timestamp": txn.timestamp,
                    "hash": current.get_hash(),
                    "previous_hash": current.get_previous_hash()
                }
                
                if user_wallet is None or txn.sender_address == user_wallet:
                    if search_type == "address" and txn.receiver_address == value:
                        results.append(txn_data)
                    elif search_type == "amount" and txn.amount == value:
                        results.append(txn_data)
                current = current.next
            return results
        except ValueError:
            print(f"Invalid value for {search_type} search.")
            return []
    

    def verify_chain(self):
        transactions = list(collection.find().sort("timestamp", 1))
        print(f"DEBUG: Retrieved Transactions -> {transactions}")

        if not transactions:
            return {"message": "Ledger is empty.", "valid": True}
        
        # ---HASH CHAIN VERIFICATION---
        
        for i in range(1, len(transactions)):
            recalculated_hash = self.calculate_hash(
                transactions[i]["sender_address"],
                transactions[i]["receiver_address"],
                transactions[i]["amount"],
                transactions[i]["timestamp"],  
                transactions[i - 1]["hash"]
            )

            if transactions[i]["previous_hash"] != transactions[i - 1]["hash"]:
                return {"message": "Blockchain is broken! Hash mismatch between blocks.", "valid": False}

            if transactions[i]["hash"] != recalculated_hash:
                return {
                    "message": f"Tampering detected! Expected: {recalculated_hash}, Found: {transactions[i]['hash']}",
                    "valid": False
                }

        return {"message": "Blockchain is valid.", "valid": True}
        

        #---MERKLE TREE VERIFICATION---
        '''
        merkle_tree = MerkleTree(transactions)
        computed_root = merkle_tree.get_root()
        stored_root = db["merkle_roots"].find_one(sort=[("timestamp", -1)])["root"]  
        print("com",computed_root)
        print("mer",stored_root)
        if computed_root != stored_root:
            return {"message": "Merkle Tree verification failed! Data tampered.", "valid": False}

        return {"message": "Merkle Tree is valid.", "valid": True}
        '''

        #-----using linked list------
        '''
        if not self.head:
            return {"message": "Ledger is empty.", "valid": True}

        current = self.head
        previous = None

        while current:
            recalculated_hash = self.calculate_hash(
                current.transaction.sender_address,
                current.transaction.receiver_address,
                current.transaction.amount,
                current.transaction.timestamp,
                current.get_previous_hash()
            )

            if current.get_hash() != recalculated_hash:
                return {
                    "message": f"Tampering detected! Expected: {recalculated_hash}, Found: {current.get_hash()}",
                    "valid": False
                }

            if previous and current.get_previous_hash() != previous.get_hash():
                return {
                    "message": "Blockchain is broken! Hash mismatch between blocks.",
                    "valid": False
                }

            previous = current
            current = current.next

        return {"message": "Blockchain is valid.","valid":True}
        '''

    def display_ledger(self):
        if not self.head:
            print("The ledger is empty.")
            return
        print("\n===== Transaction Ledger =====\n")
        current = self.head
        while current:
            txn = current.transaction
            print(f"Sender Address: {txn.sender_address}")
            print(f"Receiver Address: {txn.receiver_address}")
            print(f"Amount: {txn.amount}")
            timestamp_obj = datetime.fromisoformat(txn.timestamp)
            print(f"Timestamp: {timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 40)
            current = current.next


obj = TransactionLedger()

if __name__ == "__main__":
    while True:
        print("\nOptions: 1. Add Transaction  2. Display Ledger  3. Verify Ledger  4. Exit  5. Tamper Data")
        choice = input("Enter your choice: ")

        if choice == "1":
            sender = input("Sender name: ")
            receiver = input("Receiver name: ")
            try:
                amount = float(input("Amount: "))
                obj.add_transaction(sender, receiver, amount)
            except ValueError:
                print("Invalid amount! Please enter a valid number.")

        elif choice == "2":
            obj.display_ledger()

        elif choice == "3":
            print("Ledger Integrity Verified:", obj.verify_chain())

        elif choice == "4":
            print("THANK YOU")
            break

        elif choice == "5":
            if obj.head:
                print("\n⚠️ Tampering first transaction data...")
                obj.head.transaction.amount = 9999999  # Modify the amount
                print("Transaction tampered successfully!")
            else:
                print("No transactions found to tamper.")

        else:
            print("Invalid choice! Please enter a valid option.")
