import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
import re

HISTORY_FILE = "password_history.json"
MAX_HISTORY = 5

# --- Password Utilities ---
def generate_password(length=16):
    chars = string.ascii_letters + string.digits + string.punctuation
    password = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
        random.choice(string.punctuation),
    ]
    password += random.choices(chars, k=length - 4)
    random.shuffle(password)
    return "".join(password)

def check_password_strength(password):
    score = 0
    feedback = []

    length = len(password)
    if length >= 12:
        score += 20
        feedback.append("Excellent length")
    elif length >= 8:
        score += 15
        feedback.append("Good length")
    else:
        score += 5
        feedback.append("Too short")

    char_types = sum([
        bool(re.search(r'[a-z]', password)),
        bool(re.search(r'[A-Z]', password)),
        bool(re.search(r'\d', password)),
        bool(re.search(r'[^a-zA-Z0-9\s]', password)),
    ])

    score += char_types * 10
    feedback.append(f"{char_types} character types used")

    unique_ratio = len(set(password)) / length if length else 0
    if unique_ratio > 0.7:
        score += 15
    else:
        feedback.append("Try more unique characters")

    assessment = "Very Weak"
    if score >= 80:
        assessment = "Excellent"
    elif score >= 60:
        assessment = "Strong"
    elif score >= 40:
        assessment = "Medium"
    elif score >= 20:
        assessment = "Weak"

    return {"score": min(score, 100), "assessment": assessment, "feedback": feedback}

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f)
    except:
        pass

# --- GUI App ---
class PasswordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Master")
        self.root.geometry("500x600")

        self.setup_ui()
        self.update_history()

    def setup_ui(self):
        self.entry = ttk.Entry(self.root, font=("Arial", 14), width=30)
        self.entry.pack(pady=10)

        frame = ttk.Frame(self.root)
        frame.pack(pady=10)

        ttk.Button(frame, text="Generate", command=self.generate_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Check Strength", command=self.check_strength).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Copy", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)

        self.progress = ttk.Progressbar(self.root, length=300, mode="determinate")
        self.progress.pack(pady=10)

        self.result_label = ttk.Label(self.root, text="", font=("Arial", 12))
        self.result_label.pack(pady=5)

        self.feedback_label = ttk.Label(self.root, text="", font=("Arial", 10), wraplength=450, justify="left")
        self.feedback_label.pack(pady=5)

        ttk.Label(self.root, text="Password History:", font=("Arial", 12, "bold")).pack(pady=(20, 5))
        self.history_frame = ttk.Frame(self.root)
        self.history_frame.pack()

    def generate_password(self):
        pwd = generate_password()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, pwd)
        self.check_strength()
        self.add_to_history(pwd)

    def check_strength(self):
        pwd = self.entry.get()
        if not pwd:
            messagebox.showwarning("Warning", "Enter or generate a password first.")
            return
        result = check_password_strength(pwd)
        self.progress["value"] = result["score"]
        self.result_label.config(text=f"Strength: {result['assessment']}")
        self.feedback_label.config(text="\n".join(["• " + f for f in result["feedback"]]))

    def copy_to_clipboard(self):
        pwd = self.entry.get()
        if pwd:
            self.root.clipboard_clear()
            self.root.clipboard_append(pwd)
            messagebox.showinfo("Copied", "Password copied to clipboard.")
        else:
            messagebox.showwarning("Warning", "Nothing to copy.")

    def add_to_history(self, pwd):
        history = load_history()
        if pwd not in history:
            history.insert(0, pwd)
            if len(history) > MAX_HISTORY:
                history = history[:MAX_HISTORY]
            save_history(history)
        self.update_history()

    def update_history(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        history = load_history()
        if not history:
            ttk.Label(self.history_frame, text="No history yet.").pack()
        for pwd in history:
            row = ttk.Frame(self.history_frame)
            row.pack(pady=2, fill="x", padx=5)
            ttk.Label(row, text=pwd, font=("Courier", 10)).pack(side="left")
            ttk.Button(row, text="Copy", command=lambda p=pwd: self.copy_specific(p)).pack(side="right")

    def copy_specific(self, pwd):
        self.root.clipboard_clear()
        self.root.clipboard_append(pwd)
        messagebox.showinfo("Copied", "Password copied from history.")

# --- Run ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordApp(root)
    root.mainloop()
