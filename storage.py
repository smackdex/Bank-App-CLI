import json
from pathlib import Path

from account import BankAccount


# Define the location of the project's data directory.
DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_FILE = DATA_DIR / "accounts.json"


def load_accounts():
    """Load saved customer accounts from the JSON file."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # If the file does not exist, start with no accounts.
    if not DATA_FILE.exists():
        return {}

    # If the file exists but is empty, start with no accounts.
    if DATA_FILE.stat().st_size == 0:
        return {}

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            saved_data = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            "The accounts file contains invalid JSON. "
            "Check its contents before continuing."
        ) from error

    if not isinstance(saved_data, dict):
        raise ValueError("Invalid accounts data format.")

    accounts = {}

    for account_number, details in saved_data.items():

        if not isinstance(details, dict):
            raise ValueError(
                f"Invalid data for account {account_number}."
            )

        try:
            # Support both the new and previous account structures.
            full_name = details.get(
                "full_name",
                details.get("account_name")
            )

            transaction_pin_hash = details.get(
                "transaction_pin_hash",
                details.get("pin_hash")
            )

            account = BankAccount(
                account_number=account_number,
                full_name=full_name,
                email=details.get("email"),
                password_hash=details.get("password_hash"),
                transaction_pin_hash=transaction_pin_hash,
                balance=details["balance"],

                # Load transaction PIN security information.
                failed_pin_attempts=details.get(
                    "failed_pin_attempts", 0
                ),
                pin_locked_until=details.get("pin_locked_until")
            )

        except KeyError as error:
            raise ValueError(
                f"Missing required information for account "
                f"{account_number}."
            ) from error

        transactions = details.get("transactions", [])

        if not isinstance(transactions, list):
            raise ValueError(
                f"Invalid transaction history for account "
                f"{account_number}."
            )

        account.transactions = transactions

        accounts[account_number] = account

    return accounts


def save_accounts(accounts):
    """Save customer account information to the JSON file."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    saved_data = {}

    for account_number, account in accounts.items():

        saved_data[account_number] = {
            "full_name": account.full_name,
            "email": account.email,
            "password_hash": account.password_hash,
            "transaction_pin_hash": account.transaction_pin_hash,
            "balance": str(account.balance),
            "transactions": account.get_transaction_history(),

            # Save transaction PIN security information.
            "failed_pin_attempts": account.failed_pin_attempts,
            "pin_locked_until": account.pin_locked_until
        }

    # Write to a temporary file before replacing the saved file.
    temp_file = DATA_DIR / "accounts.tmp"

    try:
        with temp_file.open("w", encoding="utf-8") as file:
            json.dump(saved_data, file, indent=4)

        temp_file.replace(DATA_FILE)

    finally:
        if temp_file.exists():
            temp_file.unlink()