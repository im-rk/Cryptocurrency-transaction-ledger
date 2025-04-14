package core;

import java.util.*;

public class TransactionLedger {
    public Node head;

    public void addTransaction(String sender, String receiver, double amount) {
        String previousHash = (head == null) ? "0" : getLastHash();
        Transaction tx = new Transaction(sender, receiver, amount, previousHash);
        Node newNode = new Node(tx);

        if (head == null) {
            head = newNode;
        } else {
            Node current = head;
            while (current.next != null) {
                current = current.next;
            }
            current.next = newNode;
        }
    }

    private String getLastHash() {
        Node current = head;
        while (current.next != null) {
            current = current.next;
        }
        return current.transaction.hash;
    }

    public String getFormattedLedger() {
        StringBuilder sb = new StringBuilder();
        Node current = head;
        int index = 1;

        while (current != null) {
            Transaction tx = current.transaction;
            sb.append("Transaction ").append(index++).append(":\n");
            sb.append("  Sender: ").append(tx.sender).append("\n");
            sb.append("  Receiver: ").append(tx.receiver).append("\n");
            sb.append("  Amount: ").append(tx.amount).append("\n");
            sb.append("  Hash: ").append(tx.hash).append("\n");
            sb.append("  Previous Hash: ").append(tx.previousHash).append("\n\n");
            current = current.next;
        }

        return sb.toString();
    }

    public boolean verifyChain() {
        Node current = head;
        String prevHash = "0";

        while (current != null) {
            if (!current.transaction.previousHash.equals(prevHash)) {
                return false;
            }

            if (!current.transaction.hash.equals(current.transaction.calculateHash())) {
                return false;
            }

            prevHash = current.transaction.hash;
            current = current.next;
        }

        return true;
    }

    public List<Map<String, Object>> searchTransactions(String searchType, String value) {
        List<Map<String, Object>> results = new ArrayList<>();
        Node current = head;

        try {
            if (searchType.equals("amount")) {
                double amountVal = Double.parseDouble(value);
                while (current != null) {
                    Transaction tx = current.transaction;
                    if (tx.amount == amountVal) {
                        results.add(makeTxnMap(current));
                    }
                    current = current.next;
                }
            } else if (searchType.equals("address")) {
                while (current != null) {
                    Transaction tx = current.transaction;
                    if (tx.sender.equals(value) || tx.receiver.equals(value)) {
                        results.add(makeTxnMap(current));
                    }
                    current = current.next;
                }
            } else if (searchType.equals("hash")) {
                while (current != null) {
                    if (current.transaction.hash.equals(value)) {
                        results.add(makeTxnMap(current));
                        break;
                    }
                    current = current.next;
                }
            }
        } catch (NumberFormatException e) {
            System.out.println("Invalid amount format: " + value);
        }

        return results;
    }

    private Map<String, Object> makeTxnMap(Node node) {
        Transaction tx = node.transaction;
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("sender_address", tx.sender);
        map.put("receiver_address", tx.receiver);
        map.put("amount", tx.amount);
        map.put("timestamp", tx.timestamp.toString());
        map.put("hash", tx.hash);
        map.put("previous_hash", tx.previousHash);
        return map;
    }
}




