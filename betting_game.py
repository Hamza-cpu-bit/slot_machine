import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import random
from datetime import datetime

USER_FILE = "account_management.json"
DAILY_BONUS = 500
ROWS, COLS = 99,3
MAX_LINES = 5
MIN_BET = 1
MAX_BET = 100

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
        messagebox.showinfo("Daily Bonus", f"🎁 Daily bonus of ${DAILY_BONUS} added!")

def generate_spin():
    all_symbols = []
    for symbol, count in symbol_count.items():
        all_symbols.extend([symbol] * count)

    columns = []
    for _ in range(COLS):
        col = []
        for _ in range(ROWS):
            val = random.choice(all_symbols)  # Allow reuse of symbols
            col.append(val)
        columns.append(col)
    return columns


def calculate_winnings(columns, lines, bet):
    winnings = 0
    winning_lines = []
    for line in range(lines):
        symbol = columns[0][line]
        if all(columns[col][line] == symbol for col in range(1, COLS)):
            winnings += symbol_value[symbol] * bet
            winning_lines.append(line + 1)
    return winnings, winning_lines

class SlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎰 Slot Machine Game")
        self.users = load_users()
        self.current_user = None

        self.login_frame()

    def login_frame(self):
        self.clear()
        tk.Label(self.root, text="Login or Signup", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Login", width=15, command=self.login).pack(pady=5)
        tk.Button(self.root, text="Signup", width=15, command=self.signup).pack(pady=5)

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login(self):
        username = simpledialog.askstring("Login", "Username:")
        password = simpledialog.askstring("Login", "Password:", show='*')

        if username in self.users and self.users[username]["password"] == password:
            self.current_user = self.users[username]
            ensure_daily_bonus(self.current_user)
            self.main_menu()
        else:
            messagebox.showerror("Error", "Invalid credentials.")

    def signup(self):
        username = simpledialog.askstring("Signup", "Choose a username:")
        if username in self.users:
            messagebox.showerror("Error", "Username already exists.")
            return
        password = simpledialog.askstring("Signup", "Choose a password:", show='*')

        self.users[username] = {
            "password": password,
            "in_game_balance": DAILY_BONUS,
            "money_account": 0,
            "daily_deposit": {
                "date": datetime.now().strftime("%Y-%m-%d")
            }
        }
        save_users(self.users)
        messagebox.showinfo("Account Created", f"Welcome {username}!\nDaily bonus of ${DAILY_BONUS} added.")
        self.login_frame()

    def main_menu(self):
        self.clear()
        tk.Label(self.root, text="🎰 Slot Machine", font=("Arial", 16)).pack(pady=10)

        self.balance_lbl = tk.Label(self.root, font=("Arial", 12))
        self.update_balance_label()
        self.balance_lbl.pack()

        tk.Button(self.root, text="Play Slot", width=20, command=self.play_slot).pack(pady=5)
        tk.Button(self.root, text="Deposit", width=20, command=self.deposit).pack(pady=5)
        tk.Button(self.root, text="Withdraw", width=20, command=self.withdraw).pack(pady=5)
        tk.Button(self.root, text="Logout", width=20, command=self.logout).pack(pady=5)

    def update_balance_label(self):
        ig = self.current_user["in_game_balance"]
        real = self.current_user["money_account"]
        self.balance_lbl.config(text=f"In-game: ${ig} | Account: ${real}")

    def play_slot(self):
        lines = simpledialog.askinteger("Lines", f"Enter lines to bet on (1-{MAX_LINES}):", minvalue=1, maxvalue=MAX_LINES)
        if not lines:
            return
        bet = simpledialog.askinteger("Bet", f"Bet per line (${MIN_BET}-{MAX_BET}):", minvalue=MIN_BET, maxvalue=MAX_BET)
        if not bet:
            return

        total_bet = lines * bet
        if total_bet > self.current_user["in_game_balance"]:
            messagebox.showerror("Error", "Insufficient balance.")
            return

        self.current_user["in_game_balance"] -= total_bet
        spin = generate_spin()

        result = ""
        for r in range(ROWS):
            row_str = " | ".join(spin[c][r] for c in range(COLS))
            result += row_str + "\n"

        winnings, winning_lines = calculate_winnings(spin, lines, bet)
        self.current_user["in_game_balance"] += winnings

        save_users(self.users)
        self.update_balance_label()

        messagebox.showinfo("Results", f"{result}\nYou won ${winnings}\nWinning lines: {winning_lines if winning_lines else 'None'}")

    def deposit(self):
        real_balance = self.current_user["money_account"]
        amount = simpledialog.askinteger("Deposit", f"Real money balance: ${real_balance}\nEnter deposit amount:", minvalue=1, maxvalue=real_balance)
        if amount:
            self.current_user["money_account"] -= amount
            self.current_user["in_game_balance"] += amount
            save_users(self.users)
            self.update_balance_label()
            messagebox.showinfo("Success", f"Deposited ${amount} into in-game balance.")

    def withdraw(self):
        balance = self.current_user["in_game_balance"]
        amount = simpledialog.askinteger("Withdraw", f"In-game balance: ${balance}\nWithdraw amount:", minvalue=1, maxvalue=balance)
        if amount:
            self.current_user["in_game_balance"] -= amount
            self.current_user["money_account"] += amount
            save_users(self.users)
            self.update_balance_label()
            messagebox.showinfo("Success", f"Withdrew ${amount} to money account.")

    def logout(self):
        self.current_user = None
        self.login_frame()

if __name__ == "__main__":
    root = tk.Tk()
    app = SlotApp(root)
    root.mainloop()
