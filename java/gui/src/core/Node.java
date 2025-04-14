package core;

public class Node {
    public Transaction transaction;
    public Node next;

    public Node(Transaction transaction) {
        this.transaction = transaction;
        this.next = null;
    }
}
