from decimal import Decimal

from account import BankAccount
from storage import save_accounts, load_accounts


def test_bank_app_storage():

    # Create two accounts.
    account1 = BankAccount(
        account_number="1000000001",
        full_name="Sanusi Abdul",
        email="sanusi@example.com",
        password_hash="sample_password_hash",
        transaction_pin_hash="sample_pin_hash",
        balance="10000.00"
    )

    account2 = BankAccount(
        account_number="1000000002",
        full_name="Sumayyah Ahmed",
        email="sumayyah@example.com",
        password_hash="sample_password_hash",
        transaction_pin_hash="sample_pin_hash",
        balance="5000.00"
    )

    # Perform transactions.
    account1.deposit("2000.00")
    account1.withdraw("1000.00")
    account1.transfer(account2, "3000.00")

    # Verify balances before saving.
    assert account1.balance == Decimal("8000.00")
    assert account2.balance == Decimal("8000.00")

    # Save the accounts.
    accounts = {
        account1.account_number: account1,
        account2.account_number: account2
    }

    save_accounts(accounts)

    # Load the accounts again.
    loaded_accounts = load_accounts()

    loaded_account1 = loaded_accounts["1000000001"]
    loaded_account2 = loaded_accounts["1000000002"]

    # Verify that the balances were restored.
    assert loaded_account1.balance == Decimal("8000.00")
    assert loaded_account2.balance == Decimal("8000.00")

    # Verify account information.
    assert loaded_account1.full_name == "Sanusi Abdul"
    assert loaded_account1.email == "sanusi@example.com"
    assert loaded_account1.password_hash == "sample_password_hash"
    assert loaded_account1.transaction_pin_hash == "sample_pin_hash"

    assert loaded_account2.full_name == "Sumayyah Ahmed"
    assert loaded_account2.email == "sumayyah@example.com"

    # Verify transaction histories.
    assert len(loaded_account1.get_transaction_history()) == 3
    assert len(loaded_account2.get_transaction_history()) == 1

    print("All storage tests passed!")

    print(f"Sanusi's balance: {loaded_account1.balance}")
    print(f"Sumayyah's balance: {loaded_account2.balance}")

    print(
        "Sanusi's transactions:",
        len(loaded_account1.get_transaction_history())
    )

    print(
        "Sumayyah's transactions:",
        len(loaded_account2.get_transaction_history())
    )


if __name__ == "__main__":
    test_bank_app_storage()