import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Scanner;
class Transaction {
    String sender;
    String receiver;
    double amount;
    long timestamp;

    public Transaction(String sender, String receiver, double amount) {
        this.sender = sender;
        this.receiver = receiver;
        this.amount = amount;
        this.timestamp = System.currentTimeMillis();
    }
    public String getMyString() {
        
        return "Sender: " + sender + ", Receiver: " + receiver + ", Amount: " + amount + ", Timestamp: " + timestamp;
    }
}
class Node {
    String transaction;
    String previousHash;
    String hash;
    Node next;

    Node(String transaction, String previousHash) {
        this.transaction = transaction;
        this.previousHash = previousHash;
        this.hash = calculateHash();
        this.next = null;
    }
    
    String calculateHash() {
        String result = this.transaction + this.previousHash;

        return getSHA(result);
    }

    public static String getSHA(String input) {
        try {
            // Create a MessageDigest instance for SHA-256
            MessageDigest digest = MessageDigest.getInstance("SHA-256");

            // Convert the input string to a byte array and hash it
            byte[] hashBytes = digest.digest(input.getBytes(StandardCharsets.UTF_8));

            // Convert the byte array to a hexadecimal string
            StringBuilder hexString = new StringBuilder();
            for (byte b : hashBytes) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) {
                    hexString.append('0');
                }
                hexString.append(hex);
            }

            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            // SHA-256 should always be available, but handle the exception just in case
            throw new RuntimeException("SHA-256 algorithm not found", e);
        }
    }

}
class TransactionLedger {
    Node head;
    Node tail;
    int size;

    public TransactionLedger() {
        head = null;
        tail = null;
        size = 0;
    }

    public void addTransaction(String sender, String receiver, double amount) {
        Transaction transaction1 = new Transaction(sender, receiver, amount);
        String transaction2;
        transaction2=transaction1.getMyString();
        String previousHash;
        if (tail==null){
           previousHash=null;
        }
        else{
            previousHash=tail.hash;

        }
        Node newNode = new Node(transaction2,previousHash);

        if (head == null) {
            head = newNode;
        } else {
            tail.next = newNode;
        }
        tail = newNode;
        size++;

        System.out.println("Transaction added:\n" + transaction2 + "\n");
    }

    public void verifyAndFixChain() {
        Node current = head;
        Node previous = null;
        while (current != null && current.next != null) {
            if (current.hash!=current.next.previousHash) {
                System.out.println("Invalid transaction detected and removed: " + current.next.transaction);
                current.next = current.next.next; // Remove corrupted node
                if (current.next == null) {
                    tail = current;
                }
                size--;
            } else {
                previous = current;
                current = current.next;
            }
        }
    }

    public void displayLedger() {
        Node current = head;
        while (current != null) {
            System.out.println(current.transaction);
            current = current.next;
        }
    }

    public int getChainLength() {
        return size;
    }
}

class main {
    public static void main(String[] args) {
        
        TransactionLedger ledger = new TransactionLedger();
        Scanner scanner = new Scanner(System.in);
        
        while (true) {
            System.out.println("\nOptions: 1. Add Transaction  2. Display Ledger  3. Verify Ledger  4. Exit");
            System.out.print("Enter your choice: ");
            int choice = scanner.nextInt();
            scanner.nextLine();
            
            switch (choice) {
                case 1:
                    System.out.print("Enter sender name: ");
                    String sender = scanner.nextLine();
                    System.out.print("Enter receiver name: ");
                    String receiver = scanner.nextLine();
                    System.out.print("Enter transaction amount: ");
                    double amount = scanner.nextDouble();
                    ledger.addTransaction(sender, receiver, amount);
                    break;
                case 2:
                    ledger.displayLedger();
                    break;
                case 3:
                    ledger.verifyAndFixChain();
                    System.out.println("Ledger verified and fixed.");
                    break;
                case 4:
                    System.out.println("Thank you");
                    scanner.close();
                    return;
                default:
                    System.out.println("Invalid choice! Please enter a valid option.");
            }
        }
    }
}

    
