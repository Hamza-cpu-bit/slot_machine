import json
import os
import random
from datetime import datetime

# --- Config ---
USER_FILE = "account_management.json"
MAX_LINES = 5
MIN_BET = 1
MAX_BET = 100000
DAILY_BONUS = 500  # changed from 500 to 100

ROWS = 5
COLS = 3

symbol_count = {
    "A": 2,
    "B": 4,
    "C": 6,
    "D": 8
}
symbol_value = {
    "A": 5,
    "B": 4,
    "C": 3,
    "D": 2
}

# --- User File Handling ---
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def ensure_daily_bonus(user):
    today = datetime.now().strftime("%Y-%m-%d")
    if user["daily_deposit"]["date"] != today:
        user["daily_deposit"]["date"] = today
        user["in_game_balance"] += DAILY_BONUS
        print(f"\nDaily bonus of ${DAILY_BONUS} added to your in-game balance!")

# --- Auth ---
def signup(users):
    username = input("Choose a username: ")
    if username in users:
        print("Username already exists.")
        return None
    password = input("Choose a password: ")
    users[username] = {
        "password": password,
        "in_game_balance": DAILY_BONUS,
        "money_account": 0,
        "daily_deposit": {
            "date": datetime.now().strftime("%Y-%m-%d")
        }
    }
    print(f"\nWelcome {username}, you’ve been credited with ${DAILY_BONUS} for practice.")
    return username

def login(users):
    username = input("Username: ")
    password = input("Password: ")
    if username in users and users[username]["password"] == password:
        return username
    print("Invalid credentials.")
    return None

# --- Slot Machine Logic ---
def get_number_of_lines():
    while True:
        lines = input(f"Enter number of lines to bet on (1-{MAX_LINES}): ")
        if lines.isdigit():
            lines = int(lines)
            if 1 <= lines <= MAX_LINES:
                return lines
        print("Invalid number of lines.")

def get_bet(balance):
    while True:
        amount = input(f"Enter bet per line (${MIN_BET}-${MAX_BET}): ")
        if amount.isdigit():
            amount = int(amount)
            if MIN_BET <= amount <= MAX_BET and amount * MAX_LINES <= balance:
                return amount
        print("Invalid bet amount.")

def generate_spin():
    all_symbols = []
    for symbol, count in symbol_count.items():
        all_symbols.extend([symbol] * count)

    columns = []
    for _ in range(COLS):
        current = all_symbols[:]
        col = []
        for _ in range(ROWS):
            val = random.choice(current)
            current.remove(val)
            col.append(val)
        columns.append(col)
    return columns

def print_slot(columns):
    for row in range(ROWS):
        print(" | ".join(columns[col][row] for col in range(COLS)))

def calculate_winnings(columns, lines, bet):
    winnings = 0
    winning_lines = []
    for line in range(lines):
        symbol = columns[0][line]
        if all(columns[col][line] == symbol for col in range(1, COLS)):
            winnings += symbol_value[symbol] * bet
            winning_lines.append(line + 1)
    return winnings, winning_lines

def withdraw(user):
    print(f"Your current in-game balance: ${user['in_game_balance']}")
    amount = input("Enter amount to withdraw to your money account: $")
    if amount.isdigit():
        amount = int(amount)
        if 0 < amount <= user["in_game_balance"]:
            user["in_game_balance"] -= amount
            user["money_account"] += amount
            print(f"${amount} withdrawn successfully to your money account.")
        else:
            print("Invalid amount.")
    else:
        print("Please enter a valid number.")

# --- Main Game Loop ---
def main():
    print("🎰 DEMO SLOT MACHINE 🎰")
    users = load_users()

    while True:
        choice = input("\n1. Login\n2. Signup\nChoose option: ")
        if choice == "1":
            username = login(users)
        elif choice == "2":
            username = signup(users)
        else:
            print("Invalid option.")
            continue
        if username:
            break

    user = users[username]
    ensure_daily_bonus(user)

    while True:
        print(f"\nIn-game balance: ${user['in_game_balance']}")
        print(f"Money account:   ${user['money_account']}")

        print("\nOptions:")
        print("1. Play slot machine")
        print("2. Withdraw to money account")
        print("3. Quit")

        choice = input("Choose: ")

        if choice == "1":
            lines = get_number_of_lines()
            bet = get_bet(user['in_game_balance'])
            total_bet = lines * bet

            if total_bet > user['in_game_balance']:
                print("Insufficient in-game balance.")
                continue

            user['in_game_balance'] -= total_bet
            slots = generate_spin()
            print_slot(slots)

            winnings, winning_lines = calculate_winnings(slots, lines, bet)
            user['in_game_balance'] += winnings

            print(f"\nYou won ${winnings}")
            if winning_lines:
                print("Winning lines:", ", ".join(map(str, winning_lines)))

        elif choice == "2":
            withdraw(user)

        elif choice == "3":
            break

        else:
            print("Invalid choice.")

    save_users(users)
    print("Thanks for playing!")

if __name__ == "__main__":
    main()
