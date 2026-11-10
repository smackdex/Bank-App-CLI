from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation


class BankAccount:
    def __init__(
        self,
        account_number,
        account_name=None,
        pin_hash=None,
        balance=0,
        *,
        full_name=None,
        email=None,
        password_hash=None,
        transaction_pin_hash=None,
        failed_pin_attempts=0,
        pin_locked_until=None
    ):
        """
        Represent an individual bank account.
        """

        # Support both old and new account field names.
        if full_name is None:
            full_name = account_name

        if transaction_pin_hash is None:
            transaction_pin_hash = pin_hash

        self.account_number = account_number
        self.full_name = full_name
        self.email = email
        self.password_hash = password_hash
        self.transaction_pin_hash = transaction_pin_hash

        # Temporary compatibility aliases.
        self.account_name = self.full_name
        self.pin_hash = self.transaction_pin_hash

        self._balance = self._convert_amount(balance)
        self.transactions = []

        # Track unsuccessful transaction PIN attempts.
        if (
            not isinstance(failed_pin_attempts, int)
            or isinstance(failed_pin_attempts, bool)
            or failed_pin_attempts < 0
        ):
            raise ValueError("Invalid failed PIN attempt count.")

        self.failed_pin_attempts = failed_pin_attempts

        # Store the lock expiration timestamp.
        if (
            pin_locked_until is not None
            and not isinstance(pin_locked_until, str)
        ):
            raise ValueError("Invalid PIN lock expiration value.")

        self.pin_locked_until = pin_locked_until

    @staticmethod
    def _convert_amount(amount):
        """Convert an amount to Decimal and reject invalid values."""

        try:
            amount = Decimal(str(amount))

        except (InvalidOperation, ValueError, TypeError) as error:
            raise ValueError("Invalid monetary amount.") from error

        if not amount.is_finite():
            raise ValueError("Amount must be a finite number.")

        if amount.as_tuple().exponent < -2:
            raise ValueError(
                "Amount cannot have more than two decimal places."
            )

        return amount

    @property
    def balance(self):
        """Return the current account balance."""

        return self._balance

    def _record_transaction(
        self,
        transaction_type,
        amount,
        description
    ):
        """Record a transaction after a successful operation."""

        transaction = {
            "type": transaction_type,
            "amount": str(amount),
            "description": description,
            "balance_after": str(self._balance),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        self.transactions.append(transaction)

    def deposit(self, amount):
        """Deposit money into the account."""

        amount = self._convert_amount(amount)

        if amount <= 0:
            raise ValueError(
                "Deposit amount must be greater than zero."
            )

        self._balance += amount

        self._record_transaction(
            "Deposit",
            amount,
            "Money deposited into account"
        )

        return (
            f"Successfully deposited {amount}. "
            f"New balance: {self.balance}"
        )

    def withdraw(self, amount):
        """Withdraw money from the account."""

        amount = self._convert_amount(amount)

        if amount <= 0:
            raise ValueError(
                "Withdrawal amount must be greater than zero."
            )

        if amount > self._balance:
            raise ValueError("Insufficient funds.")

        self._balance -= amount

        self._record_transaction(
            "Withdrawal",
            amount,
            "Money withdrawn from account"
        )

        return (
            f"Successfully withdrawn {amount}. "
            f"New balance: {self.balance}"
        )

    def transfer(self, recipient, amount):
        """
        Transfer money to another BankAccount.

        The Bank layer must verify the sender's transaction PIN
        before allowing this operation through the application.
        """

        if not isinstance(recipient, BankAccount):
            raise ValueError(
                "Recipient must be a valid bank account."
            )

        if recipient is self:
            raise ValueError(
                "You cannot transfer money to yourself."
            )

        amount = self._convert_amount(amount)

        if amount <= 0:
            raise ValueError(
                "Transfer amount must be greater than zero."
            )

        if amount > self._balance:
            raise ValueError("Insufficient funds.")

        # Update both account balances.
        self._balance -= amount
        recipient._balance += amount

        # Record the sender's transaction.
        self._record_transaction(
            "Transfer",
            amount,
            f"Transfer to account {recipient.account_number}"
        )

        # Record the recipient's transaction.
        recipient._record_transaction(
            "Transfer Received",
            amount,
            f"Transfer from account {self.account_number}"
        )

        return (
            f"Successfully transferred {amount} "
            f"to account {recipient.account_number}."
        )

    def get_transaction_history(self):
        """Return a copy of the transaction history."""

        return deepcopy(self.transactions)
