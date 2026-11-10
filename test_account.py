import unittest
from decimal import Decimal
from account import BankAccount

class TestBankAccount(unittest.TestCase):

    def setUp(self):
        """Create fresh accounts before each test."""
        self.account = BankAccount(
        account_number="1234567890",
        full_name="John Doe",
        email="john@example.com",
        password_hash="sample_password_hash",
        transaction_pin_hash="sample_pin_hash",
        balance="1000.00"
    )

        self.recipient = BankAccount(
        account_number="0987654321",
        full_name="Jane Doe",
        email="jane@example.com",
        password_hash="another_password_hash",
        transaction_pin_hash="another_pin_hash",
        balance="500.00"
    )



    def test_account_creation(self):
        """Check that account details are stored correctly."""
        self.assertEqual(self.account.account_number, "1234567890")
        self.assertEqual(self.account.full_name, "John Doe")
        self.assertEqual(self.account.email, "john@example.com")
        self.assertEqual(self.account.balance, Decimal("1000.00"))

    def test_deposit(self):
        """Check that a deposit increases the balance."""
        self.account.deposit("200.00")

        self.assertEqual(self.account.balance, Decimal("1200.00"))

    def test_withdraw(self):
        """Check that a withdrawal decreases the balance."""
        self.account.withdraw("300.00")

        self.assertEqual(self.account.balance, Decimal("700.00"))

    def test_transfer(self):
        """Check that a transfer updates both accounts."""
        self.account.transfer(self.recipient, "200.00")

        self.assertEqual(self.account.balance, Decimal("800.00"))
        self.assertEqual(self.recipient.balance, Decimal("700.00"))

    def test_transaction_history(self):
        """Check that successful transactions are recorded."""
        self.account.deposit("100.00")

        history = self.account.get_transaction_history()

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["type"], "Deposit")
        self.assertEqual(history[0]["amount"], "100.00")
        self.assertIn("timestamp", history[0])

    def test_invalid_deposit(self):
        """Check that zero deposits are rejected."""
        with self.assertRaises(ValueError):
            self.account.deposit("0")

    def test_invalid_withdrawal(self):
        """Check that negative withdrawals are rejected."""
        with self.assertRaises(ValueError):
            self.account.withdraw("-100")

    def test_insufficient_funds(self):
        """Check that a withdrawal cannot exceed the balance."""
        with self.assertRaises(ValueError):
            self.account.withdraw("2000")

    def test_invalid_transfer_amount(self):
        """Check that zero-value transfers are rejected."""
        with self.assertRaises(ValueError):
            self.account.transfer(self.recipient, "0")

    def test_transfer_to_self(self):
        """Check that an account cannot transfer to itself."""
        with self.assertRaises(ValueError):
            self.account.transfer(self.account, "100")

    def test_invalid_decimal_places(self):
        """Check that amounts with more than two decimal places are rejected."""
        with self.assertRaises(ValueError):
            self.account.deposit("10.123")

    def test_invalid_amount(self):
        """Check that non-numeric amounts are rejected."""
        with self.assertRaises(ValueError):
            self.account.deposit("hello")

    def test_transaction_history_is_independent(self):
        """Check that modifying returned history doesn't alter account history."""
        self.account.deposit("100.00")

        history = self.account.get_transaction_history()
        history[0]["description"] = "Modified externally"

        original_history = self.account.get_transaction_history()

        self.assertNotEqual(
        original_history[0]["description"],
        "Modified externally"
    )