import hashlib
import hmac
import secrets
import re

from datetime import datetime, timedelta, timezone

from account import BankAccount
from storage import load_accounts, save_accounts


class Bank:

    # Transaction PIN security settings.
    MAX_PIN_ATTEMPTS = 3
    PIN_LOCK_DURATION = timedelta(minutes=5)

    def __init__(self):
        self.accounts = load_accounts()

    @staticmethod
    def hash_password(password):
        """Securely hash a customer's account password."""

        salt = secrets.token_hex(16)

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            600_000
        )

        return f"{salt}${password_hash.hex()}"

    @staticmethod
    def verify_password(password, stored_hash):
        """Verify a customer's password against its stored hash."""

        try:
            salt, original_hash = stored_hash.split("$")

            new_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt.encode("utf-8"),
                600_000
            )

            return hmac.compare_digest(
                new_hash.hex(),
                original_hash
            )

        except (ValueError, AttributeError, TypeError):
            return False

    @staticmethod
    def hash_pin(pin):
        """Securely hash a customer's transaction PIN."""

        salt = secrets.token_hex(16)

        pin_hash = hashlib.pbkdf2_hmac(
            "sha256",
            pin.encode("utf-8"),
            salt.encode("utf-8"),
            600_000
        )

        return f"{salt}${pin_hash.hex()}"

    @staticmethod
    def verify_pin(pin, stored_hash):
        """Verify a customer's transaction PIN."""

        try:
            salt, original_hash = stored_hash.split("$")

            new_hash = hashlib.pbkdf2_hmac(
                "sha256",
                pin.encode("utf-8"),
                salt.encode("utf-8"),
                600_000
            )

            return hmac.compare_digest(
                new_hash.hex(),
                original_hash
            )

        except (ValueError, AttributeError, TypeError):
            return False

    @staticmethod
    def validate_full_name(full_name):
        """Validate a customer's full name."""

        if not isinstance(full_name, str):
            raise ValueError("Full name must be text.")

        full_name = full_name.strip()

        name_parts = full_name.split()

        if len(name_parts) < 2:
            raise ValueError(
                "Please enter your first name and surname."
            )

        if not all(
            re.fullmatch(
                r"[^\W\d_]+(?:[-'][^\W\d_]+)*",
                part,
                re.UNICODE
            )
            for part in name_parts
        ):
            raise ValueError("Full name contains invalid characters.")

        return " ".join(name_parts)

    @staticmethod
    def validate_email(email):
        """Validate and normalize an email address."""

        if not isinstance(email, str):
            raise ValueError("Email must be text.")

        email = email.strip().lower()

        email_pattern = (
            r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        )

        if not re.fullmatch(email_pattern, email):
            raise ValueError("Please enter a valid email address.")

        return email

    @staticmethod
    def validate_password(password):
        """Validate a customer's account password."""

        if not isinstance(password, str):
            raise ValueError("Password must be text.")

        if len(password) < 8:
            raise ValueError(
                "Password must contain at least 8 characters."
            )

        if not any(char.isalpha() for char in password):
            raise ValueError(
                "Password must contain at least one letter."
            )

        if not any(char.isdigit() for char in password):
            raise ValueError(
                "Password must contain at least one digit."
            )

        if not any(not char.isalnum() for char in password):
            raise ValueError(
                "Password must contain at least one special character."
            )

        return password

    @staticmethod
    def validate_pin(pin):
        """Validate a customer's four-digit transaction PIN."""

        if not isinstance(pin, str) or not pin.isdigit() or len(pin) != 4:
            raise ValueError("PIN must contain exactly four digits.")

        return pin

    def generate_account_number(self):
        """Generate a unique 10-digit account number."""

        while True:
            account_number = str(
                secrets.randbelow(9_000_000_000) + 1_000_000_000
            )

            if account_number not in self.accounts:
                return account_number

    def sign_up(self, full_name, email, password, pin):
        """Register a new customer."""

        full_name = self.validate_full_name(full_name)
        email = self.validate_email(email)
        password = self.validate_password(password)
        pin = self.validate_pin(pin)

        # Prevent duplicate email registrations.
        for account in self.accounts.values():

            if account.email and account.email.lower() == email:
                raise ValueError(
                    "An account with this email already exists."
                )

        account_number = self.generate_account_number()

        password_hash = self.hash_password(password)
        pin_hash = self.hash_pin(pin)

        new_account = BankAccount(
            account_number=account_number,
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            transaction_pin_hash=pin_hash,
            balance=0
        )

        self.accounts[account_number] = new_account

        save_accounts(self.accounts)

        return new_account

    def login(self, email, password):
        """Authenticate a customer using email and password."""

        try:
            email = self.validate_email(email)

        except ValueError:
            return None

        for account in self.accounts.values():

            if account.email == email:

                if self.verify_password(
                    password,
                    account.password_hash
                ):
                    return account

                return None

        return None

    def deposit(self, account, amount):
        """Deposit money into a customer's account."""

        if self.accounts.get(account.account_number) is not account:
            raise ValueError("Account does not exist.")

        result = account.deposit(amount)

        save_accounts(self.accounts)

        return result

    def withdraw(self, account, amount):
        """Withdraw money from a customer's account."""

        if self.accounts.get(account.account_number) is not account:
            raise ValueError("Account does not exist.")

        result = account.withdraw(amount)

        save_accounts(self.accounts)

        return result

    def _check_pin_lock(self, account):
        """Check whether a customer's transaction PIN is locked."""

        if account.pin_locked_until is None:
            return

        try:
            locked_until = datetime.fromisoformat(
                account.pin_locked_until
            )

            if locked_until.tzinfo is None:
                raise ValueError("PIN lock timestamp has no timezone.")

        except (ValueError, TypeError) as error:
            raise ValueError(
                "Invalid PIN lock information. Please contact support."
            ) from error

        current_time = datetime.now(timezone.utc)

        # The lockout is still active.
        if current_time < locked_until:

            remaining_seconds = (
                locked_until - current_time
            ).total_seconds()

            remaining_minutes = max(
                1,
                int(remaining_seconds // 60) + 1
            )

            raise ValueError(
                "Your transaction PIN is temporarily locked. "
                f"Please try again in approximately "
                f"{remaining_minutes} minute(s)."
            )

        # The lockout has expired.
        account.failed_pin_attempts = 0
        account.pin_locked_until = None

        save_accounts(self.accounts)

    def _verify_transaction_pin(self, account, pin):
        """Verify PIN and manage unsuccessful attempts."""

        # Check whether the account is currently locked.
        self._check_pin_lock(account)

        # Validate the entered PIN.
        if not self.verify_pin(
            pin,
            account.transaction_pin_hash
        ):

            account.failed_pin_attempts += 1

            # Lock the account after the maximum failed attempts.
            if account.failed_pin_attempts >= self.MAX_PIN_ATTEMPTS:

                lock_expiration = (
                    datetime.now(timezone.utc)
                    + self.PIN_LOCK_DURATION
                )

                account.pin_locked_until = (
                    lock_expiration.isoformat()
                )

                save_accounts(self.accounts)

                raise ValueError(
                    "Too many incorrect PIN attempts. "
                    "Transfers are locked for 5 minutes."
                )

            remaining_attempts = (
                self.MAX_PIN_ATTEMPTS
                - account.failed_pin_attempts
            )

            # Save the failed attempt immediately.
            save_accounts(self.accounts)

            raise ValueError(
                "Incorrect transaction PIN. "
                f"{remaining_attempts} attempt(s) remaining."
            )

        # Correct PIN: reset the failed attempt counter.
        account.failed_pin_attempts = 0
        account.pin_locked_until = None

        save_accounts(self.accounts)

    def transfer(self, sender, recipient_account_number, amount, pin):
        """Transfer money from one account to another."""

        # Confirm that the sender belongs to this bank instance.
        if self.accounts.get(sender.account_number) is not sender:
            raise ValueError("Sender account does not exist.")

        # Find the recipient's account.
        recipient = self.accounts.get(recipient_account_number)

        if recipient is None:
            raise ValueError("Recipient account does not exist.")

        # Validate the transfer amount before PIN verification.
        amount = BankAccount._convert_amount(amount)

        if amount <= 0:
            raise ValueError(
                "Transfer amount must be greater than zero."
            )

        if amount > sender.balance:
            raise ValueError("Insufficient funds.")

        # Prevent transfers to the same account.
        if sender is recipient:
            raise ValueError("You cannot transfer money to yourself.")

        # Verify PIN and enforce temporary lockout.
        self._verify_transaction_pin(sender, pin)

        # Process the transfer.
        result = sender.transfer(recipient, amount)

        # Save both accounts and their transaction histories.
        save_accounts(self.accounts)

        return result

    def get_transaction_history(self, account):
        """Retrieve a customer's transaction history."""

        if self.accounts.get(account.account_number) is not account:
            raise ValueError("Account does not exist.")

        return account.get_transaction_history()