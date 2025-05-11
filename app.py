import streamlit as st
from datetime import datetime

# ------------------ Models ------------------ #

class Transaction:
    def __init__(self, amount, type_):
        self.amount = amount
        self.type = type_
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Account:
    def __init__(self, username, account_type="Savings", balance=0):
        self.username = username
        self.account_type = account_type
        self._balance = balance
        self.transactions = []

    def deposit(self, amount):
        if amount > 0:
            self._balance += amount
            self.transactions.append(Transaction(amount, "Deposit"))
            return f"✅ Deposited ${amount}"
        return "❌ Invalid deposit amount"

    def withdraw(self, amount):
        if amount <= self._balance:
            self._balance -= amount
            self.transactions.append(Transaction(amount, "Withdrawal"))
            return f"✅ Withdrew ${amount}"
        return "❌ Insufficient funds"

    def get_balance(self):
        return self._balance

    def get_transactions(self):
        return self.transactions

class SavingsAccount(Account):
    def __init__(self, username, balance=0, interest_rate=0.03):
        super().__init__(username, "Savings", balance)
        self.interest_rate = interest_rate

    def calculate_interest(self):
        interest = self._balance * self.interest_rate
        self._balance += interest
        self.transactions.append(Transaction(interest, "Interest"))
        return f"💰 Interest of ${interest:.2f} added"

class CurrentAccount(Account):
    def __init__(self, username, balance=0, overdraft_limit=5000):
        super().__init__(username, "Current", balance)
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount):
        if amount <= self._balance + self.overdraft_limit:
            self._balance -= amount
            self.transactions.append(Transaction(amount, "Withdrawal"))
            return f"✅ Withdrew ${amount}"
        return "❌ Overdraft limit exceeded"


# ------------------ Session State ------------------ #
if "users" not in st.session_state:
    st.session_state.users = {}  # username -> Account object
if "current_user" not in st.session_state:
    st.session_state.current_user = None


# ------------------ Functions ------------------ #
def login(username, password):
    if username in st.session_state.users and password == "123":
        st.session_state.current_user = username
        return True
    return False

def register(username, acc_type):
    if username not in st.session_state.users:
        if acc_type == "Savings":
            st.session_state.users[username] = SavingsAccount(username)
        else:
            st.session_state.users[username] = CurrentAccount(username)
        return True
    return False


# ------------------ UI ------------------ #
st.set_page_config(page_title="🏦 Bank App", layout="centered")
st.sidebar.title("🏦 Navigation")
menu = st.sidebar.radio("Select Option", ["Login", "Register", "Dashboard"])

# ------------------ Login ------------------ #
if menu == "Login":
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(username, password):
            st.success(f"✅ Welcome back, {username}!")
        else:
            st.error("Invalid username or password (Hint: use 123)")

# ------------------ Register ------------------ #
elif menu == "Register":
    st.title("📝 Register")
    new_user = st.text_input("Choose a Username")
    acc_type = st.radio("Account Type", ["Savings", "Current"])
    if st.button("Register"):
        if register(new_user, acc_type):
            st.success("User registered! Now login with password '123'")
        else:
            st.warning("Username already taken")

# ------------------ Dashboard ------------------ #
elif menu == "Dashboard":
    if st.session_state.current_user:
        user = st.session_state.users[st.session_state.current_user]
        st.title(f"👤 Hello, {user.username}")
        st.info(f"Account Type: {user.account_type}")
        st.success(f"💰 Balance: ${user.get_balance():.2f}")

        st.subheader("💳 Deposit / Withdraw")
        col1, col2 = st.columns(2)
        with col1:
            dep_amt = st.number_input("Deposit Amount", min_value=0.0, step=10.0, key="deposit")
            if st.button("Deposit"):
                msg = user.deposit(dep_amt)
                st.info(msg)
        with col2:
            wit_amt = st.number_input("Withdraw Amount", min_value=0.0, step=10.0, key="withdraw")
            if st.button("Withdraw"):
                msg = user.withdraw(wit_amt)
                st.info(msg)

        if user.account_type == "Savings":
            if st.button("💰 Calculate Interest"):
                st.info(user.calculate_interest())


        st.subheader("📜 Transaction History")
        transactions = user.get_transactions()
        if transactions:
            st.table({
                "Type": [t.type for t in transactions],
                "Amount": [f"${t.amount:.2f}" for t in transactions],
                "Time": [t.timestamp for t in transactions]
            })
        else:
            st.write("No transactions yet.")
    else:
        st.warning("Please login to view the dashboard.")

