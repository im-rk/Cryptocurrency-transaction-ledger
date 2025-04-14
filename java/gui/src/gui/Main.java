package gui;

import java.awt.EventQueue;
import javax.swing.*;
import javax.swing.border.EmptyBorder;
import core.TransactionLedger;

public class Main extends JFrame {
    
    private JPanel contentPane;

    public static void main(String[] args) {
        EventQueue.invokeLater(() -> {
            try {
                Main frame = new Main();
                frame.setVisible(true);
            } catch (Exception e) {
                e.printStackTrace();
            }
        });
    }

    public Main() {
        setTitle("Transaction Ledger");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setBounds(100, 100, 700, 520);
        contentPane = new JPanel();
        contentPane.setBorder(new EmptyBorder(10, 10, 10, 10));
        contentPane.setLayout(null);
        setContentPane(contentPane);

        JLabel lblSender = new JLabel("Sender:");
        lblSender.setBounds(10, 10, 80, 25);
        contentPane.add(lblSender);

        JTextField txtSender = new JTextField();
        txtSender.setBounds(100, 10, 150, 25);
        contentPane.add(txtSender);

        JButton btnAdd = new JButton("Add Transaction");
        btnAdd.setBounds(270, 10, 160, 25);
        contentPane.add(btnAdd);

        JLabel lblReceiver = new JLabel("Receiver:");
        lblReceiver.setBounds(10, 45, 80, 25);
        contentPane.add(lblReceiver);

        JTextField txtReceiver = new JTextField();
        txtReceiver.setBounds(100, 45, 150, 25);
        contentPane.add(txtReceiver);

        JButton btnDisplay = new JButton("Display Ledger");
        btnDisplay.setBounds(270, 45, 160, 25);
        contentPane.add(btnDisplay);

        JLabel lblAmount = new JLabel("Amount:");
        lblAmount.setBounds(10, 80, 80, 25);
        contentPane.add(lblAmount);

        JTextField txtAmount = new JTextField();
        txtAmount.setBounds(100, 80, 150, 25);
        contentPane.add(txtAmount);

        JButton btnVerify = new JButton("Verify Ledger");
        btnVerify.setBounds(270, 80, 160, 25);
        contentPane.add(btnVerify);

        // Search components
        JTextField txtSearch = new JTextField();
        txtSearch.setBounds(450, 10, 120, 25);
        contentPane.add(txtSearch);

        String[] searchOptions = { "hash", "address", "amount" };
        JComboBox<String> comboSearchType = new JComboBox<>(searchOptions);
        comboSearchType.setBounds(580, 10, 100, 25);
        contentPane.add(comboSearchType);

        JButton btnSearch = new JButton("Search Transactions");
        btnSearch.setBounds(450, 45, 230, 25);
        contentPane.add(btnSearch);

        // Text Area
        JTextArea textArea = new JTextArea();
        textArea.setEditable(false);
        JScrollPane scrollPane = new JScrollPane(textArea);
        scrollPane.setBounds(10, 120, 660, 310);
        contentPane.add(scrollPane);

        // Clear button at the bottom
        JButton btnClear = new JButton("Clear Display");
        btnClear.setBounds(540, 440, 130, 25);
        contentPane.add(btnClear);

        // Ledger logic
        TransactionLedger ledger = new TransactionLedger();

        btnAdd.addActionListener(e -> {
            textArea.setText("");
            String sender = txtSender.getText().trim();
            String receiver = txtReceiver.getText().trim();
            String amountText = txtAmount.getText().trim();

            if (sender.isEmpty() || receiver.isEmpty() || amountText.isEmpty()) {
                JOptionPane.showMessageDialog(this, "Please fill in all fields.", "Input Error", JOptionPane.WARNING_MESSAGE);
                return;
            }

            try {
                double amount = Double.parseDouble(amountText);
                ledger.addTransaction(sender, receiver, amount);
                textArea.setText("Transaction added successfully.\n");
                txtSender.setText("");
                txtReceiver.setText("");
                txtAmount.setText("");
            } catch (NumberFormatException ex) {
                JOptionPane.showMessageDialog(this, "Amount must be a valid number.", "Input Error", JOptionPane.WARNING_MESSAGE);
            }
        });

        btnDisplay.addActionListener(e -> {
            textArea.setText("");
            if (ledger.head == null) {
                JOptionPane.showMessageDialog(this, "No transactions to display.", "Ledger Empty", JOptionPane.INFORMATION_MESSAGE);
                return;
            }
            textArea.setText(ledger.getFormattedLedger());
        });

        btnVerify.addActionListener(e -> {
            textArea.setText("");
            if (ledger.head == null) {
                JOptionPane.showMessageDialog(this, "Ledger is empty.", "Verification Error", JOptionPane.WARNING_MESSAGE);
                return;
            }
            boolean isValid = ledger.verifyChain();
            if (isValid) {
            	textArea.setText("Ledger is valid.\n\n");
            	} else {
            		textArea.setText("Ledger is corrupted. Verification failed.\n\n");
            	}

        });

        btnSearch.addActionListener(e -> {
            String searchValue = txtSearch.getText().trim();
            String searchType = (String) comboSearchType.getSelectedItem();

            if (searchValue.isEmpty()) {
                JOptionPane.showMessageDialog(this, "Please enter a value to search.", "Search Error", JOptionPane.WARNING_MESSAGE);
                return;
            }

            textArea.setText("");
            var results = ledger.searchTransactions(searchType, searchValue);

            if (results.isEmpty()) {
                textArea.setText("No matching transactions found.\n");
            } else {
                for (var txn : results) {
                    textArea.append("Sender: " + txn.get("sender_address") + "\n");
                    textArea.append("Receiver: " + txn.get("receiver_address") + "\n");
                    textArea.append("Amount: " + txn.get("amount") + "\n");
                    textArea.append("Timestamp: " + txn.get("timestamp") + "\n");
                    textArea.append("Hash: " + txn.get("hash") + "\n");
                    textArea.append("Previous Hash: " + txn.get("previous_hash") + "\n\n");
                }
            }
        });

        btnClear.addActionListener(e -> textArea.setText(""));
    }
}

