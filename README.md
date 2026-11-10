# Bank App CLI

A terminal-based banking application built with Python and Object-Oriented Programming (OOP). It allows users to create accounts, authenticate securely, manage their balances, transfer funds, and view transaction history.

This project was developed as a practical exercise in Python programming, OOP principles, data persistence, authentication, and software testing.

## Features

- **Account Registration:** Users can register with their full name, email address, password, and four-digit transaction PIN.
- **User Authentication:** Registered users can log in using their email address and password.
- **Automatic Account Number Generation:** Each registered user receives a unique account number.
- **Password Security:** Passwords are securely hashed before being stored.
- **Transaction PIN Security:** Transaction PINs are hashed and verified before transfers are authorised.
- **Deposit:** Users can deposit money into their accounts.
- **Withdrawal:** Users can withdraw money, subject to available balance.
- **Fund Transfer:** Users can transfer money between registered accounts.
- **Transaction History:** Users can view their previous banking transactions.
- **PIN Protection:** Three consecutive incorrect transaction PIN attempts trigger a temporary five-minute lockout.
- **Data Persistence:** Account information and transaction records are stored locally using JSON.
- **Input Validation:** The application validates user inputs and handles invalid operations.

## Technologies Used

- **Python 3**
- **JSON** – Data storage and persistence.
- **Hashlib** – Password and transaction PIN hashing.
- **HMAC** – Secure hash comparison.
- **Decimal** – Accurate financial calculations.
- **Getpass** – Masked transaction PIN input.
- **Datetime** – Transaction timestamps and PIN lockout management.
- **Unittest** – Automated testing.

## Project Structure

```text
Bank-App-CLI/
│
├── account.py
├── bank.py
├── main.py
├── storage.py
│
├── data/
│   └── accounts.example.json
│
├── test_account.py
├── test_bank.py
├── test_pin_security.py
├── test_storage.py
│
├── .gitignore
└── README.md
```

### File Descriptions

| File/Directory | Description |
|---|---|
| `account.py` | Defines the BankAccount class and account-related operations. |
| `bank.py` | Handles banking operations, registration, authentication, and transaction security. |
| `main.py` | Contains the command-line interface and application menu. |
| `storage.py` | Handles loading and saving account information using JSON. |
| `data/` | Stores the application's local account database. |
| `test_account.py` | Tests account-related functionality. |
| `test_bank.py` | Tests registration, authentication, and banking operations. |
| `test_pin_security.py` | Tests transaction PIN verification and lockout security. |
| `test_storage.py` | Tests JSON data storage and retrieval. |

## Getting Started

Follow these instructions to run the application on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/smackdex/Bank-App-CLI.git
```

### 2. Navigate into the Project Directory

```bash
cd Bank-App-CLI
```

### 3. Check Your Python Version

Python 3.10 or later is recommended.

```bash
python3 --version
```

### 4. Run the Application

```bash
python3 main.py
```

The application will display the main menu, allowing you to register, log in, or exit.

## Running the Tests

The project includes automated tests to verify its major functionalities.

Run the complete test suite using:

```bash
python3 -m unittest discover -v
```

You can also run individual test files:

```bash
python3 -m unittest -v test_account.py
python3 -m unittest -v test_bank.py
python3 -m unittest -v test_storage.py
python3 -m unittest -v test_pin_security.py
```

## Data Storage

The application uses JSON for local data persistence.

Account information, balances, transaction records, and security-related information are stored in:

```text
data/accounts.json
```

An example JSON file is provided in the repository:

```text
data/accounts.example.json
```

The actual account database is excluded from version control through `.gitignore` to prevent personal account information from being uploaded to GitHub.

## Python Concepts Demonstrated

This project demonstrates practical applications of several Python concepts, including:

- Object-Oriented Programming (OOP).
- Classes and objects.
- Constructors and instance methods.
- Encapsulation and properties.
- Inheritance and method overriding.
- Static methods and class methods.
- Modules and code organisation.
- Exception handling.
- File handling and JSON.
- Data validation.
- Password and PIN hashing.
- Automated unit testing.
- Git and GitHub version control.

## Disclaimer

This application is an educational project developed for learning and demonstration purposes.

It is not a production-ready banking application and should not be used to manage real financial transactions or sensitive financial information.

## Author

**Smackdex**

GitHub: [@smackdex](https://github.com/smackdex)

Project Repository: [Bank-App-CLI](https://github.com/smackdex/Bank-App-CLI)
