package core;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class Transaction {
    public String sender;
    public String receiver;
    public double amount;
    public String hash;
    public String previousHash;
    public String timestamp;

    public Transaction(String sender, String receiver, double amount, String previousHash) {
        this.sender = sender;
        this.receiver = receiver;
        this.amount = amount;
        this.previousHash = previousHash;
        this.timestamp = getCurrentTimestamp();
        this.hash = calculateHash();
    }

    private String getCurrentTimestamp() {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        return LocalDateTime.now().format(formatter);
    }

    public String calculateHash() {
        String data = sender + receiver + amount + previousHash + timestamp;
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hashBytes = digest.digest(data.getBytes());
            StringBuilder sb = new StringBuilder();
            for (byte b : hashBytes) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }
}


