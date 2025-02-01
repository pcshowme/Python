import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont
import os

TODO_FILE = r"D:\_WorkSpace\TodoItems.dat"

class TodoApp:
    def __init__(self, master):
        self.master = master
        master.title("Todo List")

        self.custom_font = tkFont.Font(family="Helvetica", size=12)

        master.rowconfigure(0, weight=1)
        master.rowconfigure(1, weight=0)
        master.rowconfigure(2, weight=0)
        master.rowconfigure(3, weight=0)
        master.rowconfigure(4, weight=0)
        master.rowconfigure(5, weight=0)
        master.columnconfigure(0, weight=1)

        # Listbox for todo items
        self.listbox = tk.Listbox(master, font=self.custom_font)
        self.listbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Entry widget
        self.entry = tk.Entry(master, font=self.custom_font)
        self.entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.entry.bind("<Return>", lambda event: self.add_item())

        # Add button
        self.add_button = tk.Button(master, text="Add Item", font=self.custom_font, command=self.add_item)
        self.add_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Delete button
        self.delete_button = tk.Button(master, text="Delete Selected", font=self.custom_font, command=self.delete_item)
        self.delete_button.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Font size slider
        self.font_slider = tk.Scale(master, from_=8, to=30, orient="horizontal",
                                    label="Font Size", command=self.update_font_size)
        self.font_slider.set(12)
        self.font_slider.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        # Frame for reorder buttons
        reorder_frame = tk.Frame(master)
        reorder_frame.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        reorder_frame.columnconfigure(0, weight=1)
        reorder_frame.columnconfigure(1, weight=1)

        self.move_up_button = tk.Button(reorder_frame, text="Move Up", font=self.custom_font, command=self.move_item_up)
        self.move_up_button.grid(row=0, column=0, padx=5, sticky="ew")

        self.move_down_button = tk.Button(reorder_frame, text="Move Down", font=self.custom_font, command=self.move_item_down)
        self.move_down_button.grid(row=0, column=1, padx=5, sticky="ew")

        self.load_items()

    def update_font_size(self, val):
        new_size = int(val)
        self.custom_font.configure(size=new_size)

    def load_items(self):
        if os.path.exists(TODO_FILE):
            with open(TODO_FILE, "r") as file:
                for line in file:
                    item = line.strip()
                    if item:
                        self.listbox.insert(tk.END, item)

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

    def move_item_up(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            if index > 0:
                text = self.listbox.get(index)
                self.listbox.delete(index)
                new_index = index - 1
                self.listbox.insert(new_index, text)
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(new_index)
                self.save_items()

    def move_item_down(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            if index < self.listbox.size() - 1:
                text = self.listbox.get(index)
                self.listbox.delete(index)
                new_index = index + 1
                self.listbox.insert(new_index, text)
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(new_index)
                self.save_items()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
