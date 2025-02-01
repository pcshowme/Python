import tkinter as tk
from tkinter import messagebox
import os

TODO_FILE = r"D:\_WorkSpace\TodoItems.dat"

class TodoApp:
    def __init__(self, master):
        self.master = master
        master.title("Todo List")

        self.listbox = tk.Listbox(master, width=50)
        self.listbox.pack(padx=10, pady=10)

        self.entry = tk.Entry(master, width=50)
        self.entry.pack(padx=10, pady=5)
        self.entry.bind("<Return>", lambda event: self.add_item())

        self.add_button = tk.Button(master, text="Add Item", command=self.add_item)
        self.add_button.pack(pady=5)

        self.delete_button = tk.Button(master, text="Delete Selected", command=self.delete_item)
        self.delete_button.pack(pady=5)

        self.load_items()

    def load_items(self):
        if os.path.exists(TODO_FILE):
            with open(TODO_FILE, "r") as file:
                for line in file:
                    line = line.strip()
                    if line:
                        self.listbox.insert(tk.END, line)

    def save_items(self):
        with open(TODO_FILE, "w") as file:
            for index in range(self.listbox.size()):
                file.write(self.listbox.get(index) + "\n")

    def add_item(self):
        item = self.entry.get().strip()
        if item:
            self.listbox.insert(tk.END, item)
            self.entry.delete(0, tk.END)
            self.save_items()
        else:
            messagebox.showwarning("Input Error", "Please enter a valid todo item.")

    def delete_item(self):
        selected = self.listbox.curselection()
        if selected:
            for index in reversed(selected):
                self.listbox.delete(index)
            self.save_items()
        else:
            messagebox.showwarning("Selection Error", "Please select an item to delete.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
