import uuid
from decimal import Decimal

from bank import Bank


def expect_value_error(operation):
    """Confirm that an operation raises ValueError."""

    try:
        operation()

    except ValueError:
        return

    raise AssertionError("Expected ValueError, but no error was raised.")


def test_bank_registration_and_login():

    bank = Bank()

    # Generate a unique email for every test run.
    email = f"sanusi_{uuid.uuid4().hex[:8]}@example.com"

    # Register a new customer.
    account = bank.sign_up(
        "Sanusi Abdul",
        email,
        "Secure@123",
        "1234"
    )

    print("Account successfully created!")
    print("Full Name:", account.full_name)
    print("Email:", account.email)
    print("Account Number:", account.account_number)
    print("Initial Balance:", account.balance)

    # Confirm that credentials are hashed.
    assert account.password_hash != "Secure@123"
    assert account.transaction_pin_hash != "1234"

    # Test successful login.
    logged_in_account = bank.login(
        email,
        "Secure@123"
    )

    assert logged_in_account is not None

    # Test incorrect password.
    failed_login = bank.login(
        email,
        "Wrong@123"
    )

    assert failed_login is None

    # Test nonexistent email.
    invalid_login = bank.login(
        "unknown@example.com",
        "Secure@123"
    )

    assert invalid_login is None

    # Test persistence.
    new_bank = Bank()

    saved_account = new_bank.login(
        email,
        "Secure@123"
    )

    assert saved_account is not None

    # Verify transaction PIN after loading the account.
    assert new_bank.verify_pin(
        "1234",
        saved_account.transaction_pin_hash
    )

    print("\nRegistration and login tests passed!")


def test_invalid_registration():

    bank = Bank()

    email = f"invalid_{uuid.uuid4().hex[:8]}@example.com"

    # Test invalid full name.
    expect_value_error(
        lambda: bank.sign_up(
            "Sanusi",
            email,
            "Secure@123",
            "1234"
        )
    )

    # Test invalid email.
    expect_value_error(
        lambda: bank.sign_up(
            "Sanusi Abdul",
            "invalid-email",
            "Secure@123",
            "1234"
        )
    )

    # Test password without a letter.
    expect_value_error(
        lambda: bank.sign_up(
            "Sanusi Abdul",
            email,
            "12345678@",
            "1234"
        )
    )

    # Test password without a digit.
    expect_value_error(
        lambda: bank.sign_up(
            "Sanusi Abdul",
            email,
            "Secure@Password",
            "1234"
        )
    )

    # Test password without a special character.
    expect_value_error(
        lambda: bank.sign_up(
            "Sanusi Abdul",
            email,
            "Secure123",
            "1234"
        )
    )

    # Test password shorter than eight characters.
    expect_value_error(
        lambda: bank.sign_up(
            "Sanusi Abdul",
            email,
            "Ab1@",
            "1234"
        )
    )

    # Test invalid transaction PIN.
    expect_value_error(
        lambda: bank.sign_up(
            "Sanusi Abdul",
            email,
            "Secure@123",
            "123"
        )
    )

    print("Invalid registration tests passed!")


def test_duplicate_email():

    bank = Bank()

    email = f"duplicate_{uuid.uuid4().hex[:8]}@example.com"

    # Register the first customer.
    bank.sign_up(
        "Sanusi Abdul",
        email,
        "Secure@123",
        "1234"
    )

    # Attempt to register another customer with the same email.
    expect_value_error(
        lambda: bank.sign_up(
            "Another Customer",
            email.upper(),
            "Another@123",
            "5678"
        )
    )

    print("Duplicate email test passed!")


def test_deposit():

    bank = Bank()

    # Generate a unique email.
    email = f"deposit_{uuid.uuid4().hex[:8]}@example.com"

    # Register a new customer.
    account = bank.sign_up(
        "Sanusi Abdul",
        email,
        "Secure@123",
        "1234"
    )

    # Test first deposit.
    bank.deposit(account, "5000.00")

    assert account.balance == Decimal("5000.00")

    # Test another deposit.
    bank.deposit(account, "2500.00")

    assert account.balance == Decimal("7500.00")

    # Test negative deposit.
    expect_value_error(
        lambda: bank.deposit(account, "-1000")
    )

    # Test zero deposit.
    expect_value_error(
        lambda: bank.deposit(account, "0")
    )

    # Test persistence.
    new_bank = Bank()

    saved_account = new_bank.login(
        email,
        "Secure@123"
    )

    assert saved_account is not None
    assert saved_account.balance == Decimal("7500.00")

    print("Deposit tests passed!")



def test_withdraw():

    bank = Bank()

    # Generate a unique email for this test.
    email = f"withdraw_{uuid.uuid4().hex[:8]}@example.com"

    # Register a new customer.
    account = bank.sign_up(
        "Sanusi Abdul",
        email,
        "Secure@123",
        "1234"
    )

    # Deposit money before testing withdrawals.
    bank.deposit(account, "10000.00")

    assert account.balance == Decimal("10000.00")

    # Test a successful withdrawal.
    bank.withdraw(account, "3000.00")

    assert account.balance == Decimal("7000.00")

    # Test another successful withdrawal.
    bank.withdraw(account, "2000.00")

    assert account.balance == Decimal("5000.00")

    # Test withdrawal exceeding the available balance.
    expect_value_error(
        lambda: bank.withdraw(account, "6000.00")
    )

    # Confirm the balance remains unchanged.
    assert account.balance == Decimal("5000.00")

    # Test a negative withdrawal.
    expect_value_error(
        lambda: bank.withdraw(account, "-500")
    )

    # Test a zero withdrawal.
    expect_value_error(
        lambda: bank.withdraw(account, "0")
    )

    # Test an invalid amount.
    expect_value_error(
        lambda: bank.withdraw(account, "invalid")
    )

    # Confirm that successful withdrawals are recorded.
    history = account.get_transaction_history()

    assert len(history) == 3
    assert history[0]["type"] == "Deposit"
    assert history[1]["type"] == "Withdrawal"
    assert history[2]["type"] == "Withdrawal"

    # Test persistence by loading the bank again.
    new_bank = Bank()

    saved_account = new_bank.login(
        email,
        "Secure@123"
    )

    assert saved_account is not None
    assert saved_account.balance == Decimal("5000.00")

    print("Withdrawal tests passed!")

def test_transfer():

    bank = Bank()

    # Generate unique emails for both customers.
    sender_email = f"sender_{uuid.uuid4().hex[:8]}@example.com"
    recipient_email = f"recipient_{uuid.uuid4().hex[:8]}@example.com"

    # Register the sender.
    sender = bank.sign_up(
        "Sanusi Abdul",
        sender_email,
        "Secure@123",
        "1234"
    )

    # Register the recipient.
    recipient = bank.sign_up(
        "Sumayyah Abdul",
        recipient_email,
        "Secure@456",
        "5678"
    )

    # Fund the sender's account.
    bank.deposit(sender, "10000.00")

    assert sender.balance == Decimal("10000.00")
    assert recipient.balance == Decimal("0")

    # Test an incorrect transaction PIN.
    expect_value_error(
        lambda: bank.transfer(
            sender,
            recipient.account_number,
            "2000.00",
            "9999"
        )
    )

    # Confirm that neither account's balance changed.
    assert sender.balance == Decimal("10000.00")
    assert recipient.balance == Decimal("0")

    # Test a nonexistent recipient account.
    expect_value_error(
        lambda: bank.transfer(
            sender,
            "0000000000",
            "2000.00",
            "1234"
        )
    )

    # Test a successful transfer.
    bank.transfer(
        sender,
        recipient.account_number,
        "3000.00",
        "1234"
    )

    assert sender.balance == Decimal("7000.00")
    assert recipient.balance == Decimal("3000.00")

    # Test insufficient funds.
    expect_value_error(
        lambda: bank.transfer(
            sender,
            recipient.account_number,
            "8000.00",
            "1234"
        )
    )

    # Test negative transfer amount.
    expect_value_error(
        lambda: bank.transfer(
            sender,
            recipient.account_number,
            "-500",
            "1234"
        )
    )

    # Test zero transfer amount.
    expect_value_error(
        lambda: bank.transfer(
            sender,
            recipient.account_number,
            "0",
            "1234"
        )
    )

    # Test invalid transfer amount.
    expect_value_error(
        lambda: bank.transfer(
            sender,
            recipient.account_number,
            "invalid",
            "1234"
        )
    )

    # Confirm that failed transfers did not create transactions.
    sender_history = sender.get_transaction_history()
    recipient_history = recipient.get_transaction_history()

    assert len(sender_history) == 2
    assert len(recipient_history) == 1

    assert sender_history[0]["type"] == "Deposit"
    assert sender_history[1]["type"] == "Transfer"
    assert recipient_history[0]["type"] == "Transfer Received"

    # Test persistence after reloading the bank.
    new_bank = Bank()

    saved_sender = new_bank.login(
        sender_email,
        "Secure@123"
    )

    saved_recipient = new_bank.login(
        recipient_email,
        "Secure@456"
    )

    assert saved_sender is not None
    assert saved_recipient is not None

    assert saved_sender.balance == Decimal("7000.00")
    assert saved_recipient.balance == Decimal("3000.00")

    print("Transfer tests passed!")

def test_transaction_history():

    bank = Bank()

    # Generate unique emails for both customers.
    sender_email = f"history_sender_{uuid.uuid4().hex[:8]}@example.com"
    recipient_email = f"history_recipient_{uuid.uuid4().hex[:8]}@example.com"

    # Register the sender.
    sender = bank.sign_up(
        "Sanusi Abdul",
        sender_email,
        "Secure@123",
        "1234"
    )

    # Register the recipient.
    recipient = bank.sign_up(
        "Sumayyah Abdul",
        recipient_email,
        "Secure@456",
        "5678"
    )

    # Perform banking transactions.
    bank.deposit(sender, "10000.00")

    bank.withdraw(sender, "2000.00")

    bank.transfer(
        sender,
        recipient.account_number,
        "3000.00",
        "1234"
    )

    # Retrieve the sender's transaction history.
    sender_history = bank.get_transaction_history(sender)

    # Verify the sender's transaction count.
    assert len(sender_history) == 3

    # Verify the transaction types.
    assert sender_history[0]["type"] == "Deposit"
    assert sender_history[1]["type"] == "Withdrawal"
    assert sender_history[2]["type"] == "Transfer"

    # Verify transaction amounts.
    assert Decimal(sender_history[0]["amount"]) == Decimal("10000.00")
    assert Decimal(sender_history[1]["amount"]) == Decimal("2000.00")
    assert Decimal(sender_history[2]["amount"]) == Decimal("3000.00")

    # Verify the sender's final balance in the last transaction.
    assert Decimal(sender_history[2]["balance_after"]) == Decimal("5000.00")

    # Retrieve the recipient's transaction history.
    recipient_history = bank.get_transaction_history(recipient)

    assert len(recipient_history) == 1

    assert recipient_history[0]["type"] == "Transfer Received"

    assert Decimal(recipient_history[0]["amount"]) == Decimal("3000.00")

    assert Decimal(recipient_history[0]["balance_after"]) == Decimal("3000.00")

    # Confirm that transaction timestamps exist.
    for transaction in sender_history:
        assert "timestamp" in transaction
        assert transaction["timestamp"]

    # Confirm that the returned history is independent.
    sender_history.clear()

    assert len(bank.get_transaction_history(sender)) == 3

    # Test persistence by loading the bank again.
    new_bank = Bank()

    saved_sender = new_bank.login(
        sender_email,
        "Secure@123"
    )

    saved_recipient = new_bank.login(
        recipient_email,
        "Secure@456"
    )

    assert saved_sender is not None
    assert saved_recipient is not None

    # Verify the saved transaction histories.
    saved_sender_history = new_bank.get_transaction_history(saved_sender)

    saved_recipient_history = new_bank.get_transaction_history(saved_recipient)

    assert len(saved_sender_history) == 3
    assert len(saved_recipient_history) == 1

    assert saved_sender.balance == Decimal("5000.00")
    assert saved_recipient.balance == Decimal("3000.00")

    print("Transaction history tests passed!")


if __name__ == "__main__":

    test_bank_registration_and_login()

    test_invalid_registration()

    test_duplicate_email()

    test_deposit()

    test_withdraw()

    test_transfer()

    test_transaction_history()

    print("\nAll bank tests passed!")

