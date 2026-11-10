from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import storage
from bank import Bank


def test_pin_lockout():

    with TemporaryDirectory() as temp_dir:

        temp_path = Path(temp_dir)

        with patch.object(storage, "DATA_DIR", temp_path), \
             patch.object(
                 storage,
                 "DATA_FILE",
                 temp_path / "accounts.json"
             ), \
             patch(
                 "bank.load_accounts",
                 side_effect=storage.load_accounts
             ), \
             patch(
                 "bank.save_accounts",
                 side_effect=storage.save_accounts
             ):

            bank = Bank()

            account = bank.sign_up(
                "Security Test",
                "securitytest@example.com",
                "Security123!",
                "1234"
            )

            recipient = bank.sign_up(
                "Recipient Test",
                "recipienttest@example.com",
                "Recipient123!",
                "5678"
            )

            bank.deposit(account, 500)

            print("\nTesting incorrect PIN attempts...")

            # First incorrect attempt.
            try:
                bank.transfer(
                    account,
                    recipient.account_number,
                    100,
                    "0000"
                )
            except ValueError as error:
                print("Attempt 1:", error)

            assert account.failed_pin_attempts == 1

            print("\nTesting correct PIN...")

            bank.transfer(
                account,
                recipient.account_number,
                100,
                "1234"
            )

            assert account.failed_pin_attempts == 0
            assert account.balance == 400
            assert recipient.balance == 100

            print("Correct PIN accepted. Failed attempts reset.")

            print("\nTesting three consecutive incorrect attempts...")

            for attempt in range(1, 4):

                try:
                    bank.transfer(
                        account,
                        recipient.account_number,
                        100,
                        "0000"
                    )

                except ValueError as error:
                    print(f"Attempt {attempt}:", error)

            assert account.failed_pin_attempts == 3
            assert account.pin_locked_until is not None

            print("\nTesting correct PIN during lockout...")

            try:
                bank.transfer(
                    account,
                    recipient.account_number,
                    100,
                    "1234"
                )

            except ValueError as error:
                print("Lockout:", error)

            assert account.balance == 400
            assert recipient.balance == 100

            print("\nTesting actual JSON persistence...")

            # Simulate restarting the application.
            reloaded_bank = Bank()

            reloaded_account = reloaded_bank.accounts[
                account.account_number
            ]

            assert reloaded_account.failed_pin_attempts == 3
            assert reloaded_account.pin_locked_until is not None

            print("Lockout successfully recovered from JSON!")

            print("\nAll PIN security tests passed!")


if __name__ == "__main__":
    test_pin_lockout()