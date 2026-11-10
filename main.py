from bank import Bank
import getpass
from datetime import datetime
from decimal import Decimal

def display_main_menu():
    """Display the application's main menu."""

    print("\n========== BANK APP CLI ==========")
    print("1. Sign Up")
    print("2. Login")
    print("3. Exit")
    print("==================================")


def sign_up_user(bank):
    """Collect user information and register a new bank account."""

    print("\n========== SIGN UP ==========")

    full_name = input("Enter your full name: ").strip()

    email = input("Enter your email address: ").strip()

    password = input("Create your account password: ")

    pin = getpass.getpass("Create your four-digit transaction PIN: ")

    try:
        account = bank.sign_up(
            full_name,
            email,
            password,
            pin
        )

        print("\n========== REGISTRATION SUCCESSFUL ==========")
        print(f"Account Holder: {account.full_name}")
        print(f"Email Address: {account.email}")
        print(f"Account Number: {account.account_number}")
        print(f"Account Balance: {account.balance}")
        print("=============================================")

    except ValueError as error:
        print(f"\nRegistration failed: {error}")

def login_user(bank):
    """Authenticate a customer using email and password."""

    print("\n========== CUSTOMER LOGIN ==========")

    email = input("Enter your email address: ").strip()

    password = input("Enter your account password: ")

    try:
        account = bank.login(email, password)

        if account is None:
            print("\nLogin failed. Invalid email or password.")
            return
        print("\n========== LOGIN SUCCESSFUL ==========")
        customer_dashboard(bank, account)

    except ValueError as error:
        print(f"\nLogin failed: {error}")

def deposit_money(bank, account):
    """Handle deposits into a customer's account."""

    print("\n========== DEPOSIT MONEY ==========")

    amount = input("Enter the amount you want to deposit (₦): ").strip()

    try:
        result = bank.deposit(account, amount)

        print("\n========== DEPOSIT SUCCESSFUL ==========")
        print(result)
        print(f"Updated Balance: ₦{account.balance:,.2f}")
        print("========================================")

    except ValueError as error:
        print(f"\nDeposit failed: {error}")  

 
def withdraw_money(bank, account):
    """Handle withdrawals from a customer's account."""

    print("\n========== WITHDRAW MONEY ==========")

    amount = input("Enter the amount you want to withdraw (₦): ").strip()

    try:
        result = bank.withdraw(account, amount)

        print("\n========== WITHDRAWAL SUCCESSFUL ==========")
        print(result)
        print(f"Updated Balance: ₦{account.balance:,.2f}")
        print("===========================================")

    except ValueError as error:
        print(f"\nWithdrawal failed: {error}")

def transfer_money(bank, account):
    """Transfer money from one customer's account to another."""

    print("\n========== MONEY TRANSFER ==========")

    recipient_account_number = input(
        "Enter recipient's account number: "
    ).strip()

    amount = input(
        "Enter the amount you want to transfer (₦): "
    ).strip()

    pin = getpass.getpass(
        "Enter your four-digit transaction PIN: "
    )

    try:
        result = bank.transfer(
            account,
            recipient_account_number,
            amount,
            pin
        )

        print("\n========== TRANSFER SUCCESSFUL ==========")
        print(result)
        print(f"Remaining Balance: ₦{account.balance:,.2f}")
        print("==========================================")

    except ValueError as error:
        print(f"\nTransfer failed: {error}")

def view_transaction_history(bank, account):
    """Display the transaction history of a customer's account."""

    print("\n========== TRANSACTION HISTORY ==========")
    print(f"Account Holder: {account.full_name}")
    print(f"Account Number: {account.account_number}")
    print("-----------------------------------------")

    try:
        transactions = bank.get_transaction_history(account)

        if not transactions:
            print("\nYou have no transaction history yet.")
            print("Transactions will appear here when you perform banking operations.")
            return

        for index, transaction in enumerate(transactions, start=1):

            amount = Decimal(str(transaction["amount"]))
            balance_after = Decimal(str(transaction["balance_after"]))

            timestamp = transaction.get("timestamp", "Unknown")

            try:
                transaction_date = datetime.fromisoformat(
                    timestamp.replace("Z", "+00:00")
                )
                formatted_date = transaction_date.strftime(
                    "%d %B %Y, %I:%M:%S %p"
                ) + " UTC"
                
                

            except (ValueError, AttributeError):
                formatted_date = timestamp

            print(f"\nTransaction {index}")
            print("-----------------------------------------")
            print(f"Type: {transaction['type']}")
            print(f"Amount: ₦{amount:,.2f}")
            print(f"Description: {transaction['description']}")
            print(f"Balance After: ₦{balance_after:,.2f}")
            print(f"Date: {formatted_date}")

        print("\n=========================================")

    except ValueError as error:
        print(f"\nUnable to retrieve transaction history: {error}")


def customer_dashboard(bank, account):
    """Display the authenticated customer's banking dashboard."""

    while True:

        print("\n========== CUSTOMER DASHBOARD ==========")
        print(f"Welcome, {account.full_name}!")
        print(f"Account Number: {account.account_number}")
        print(f"Account Balance: ₦{account.balance:,.2f}")
        print("----------------------------------------")
        print("1. Check Account Balance")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Transfer Money")
        print("5. Transaction History")
        print("6. Logout")
        print("========================================")

        choice = input("Select an option (1-6): ").strip()

        if choice == "1":
            print(f"\nYour current balance is ₦{account.balance:,.2f}")

        elif choice == "2":
            deposit_money(bank, account)

        elif choice == "3":
            withdraw_money(bank, account)

        elif choice == "4":
            transfer_money(bank, account)

        elif choice == "5":
            view_transaction_history(bank, account)

        elif choice == "6":
            print("\nYou have successfully logged out.")
            break

        else:
            print("\nInvalid selection. Please choose between 1 and 6.")


def main():
    """Run the Bank App CLI application."""

    # Create a Bank instance and load the banking system.
    bank = Bank()

    while True:

        display_main_menu()

        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            sign_up_user(bank)

        elif choice == "2":
            login_user(bank)

        elif choice == "3":
            print("\nThank you for using Bank App CLI.")
            print("Goodbye!")
            break

        else:
            print("\nInvalid selection. Please choose between 1 and 3.")

if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:
        print("\n\nApplication interrupted.")
        print("Thank you for using Bank App CLI. Goodbye!")


    