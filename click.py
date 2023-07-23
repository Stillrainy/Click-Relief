import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import Toplevel as tkToplevel
import hashlib
import datetime
import time
import random
import threading
import pyautogui
import pyperclip


class LoginDialog(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.title("Click Relief")
        self.geometry("200x100")

        self.label = tk.Label(self, text="Enter password:")
        self.label.pack(pady=5)

        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        self.submit_button = tk.Button(
            self, text="Submit", command=self.check_password)
        self.submit_button.pack(pady=5)

        self.protocol('WM_DELETE_WINDOW', self.on_closing)

    def check_password(self):
        entered_password = self.password_entry.get()

        if entered_password == self.master.password:
            self.destroy()
        else:
            messagebox.showerror("Error", "Incorrect password.")

    def on_closing(self):
        self.master.destroy()  # End the main program


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Click Relief v1.0 - 脑子露馅")
        menu = tk.Menu(self)
        self.config(menu=menu)
        about_menu = tk.Menu(menu)
        menu.add_cascade(label="帮助", menu=about_menu)
        about_menu.add_command(label="关于", command=self.show_about)
        self.createcommand('::tk::mac::ShowAbout', self.show_about)

        self.password = self.create_password()
        self.login()

        self.label_iter = tk.Label(self, text="Number of clicks:")
        self.label_iter.grid(row=0, column=0)

        self.iter_var = tk.StringVar()
        self.entry_iter = tk.Entry(self, textvariable=self.iter_var, width=10)
        self.entry_iter.grid(row=0, column=1)

        self.file_button = tk.Button(
            self, text="Choose File", command=self.select_file)
        self.file_button.grid(row=1, column=0)

        self.start_button = tk.Button(self, text="Start", command=self.start)
        self.start_button.grid(row=1, column=1)

        self.position_label = tk.Label(self, text="")
        self.position_label.grid(row=2, column=0, columnspan=3)

        self.progress = ttk.Progressbar(self, length=200)
        self.progress.grid(row=3, column=0, columnspan=3, padx=50, sticky='ew')

        self.progress_label = tk.Label(self, text="")
        self.progress_label.grid(row=4, column=0, columnspan=3)

        self.position = None
        self.filename = None

        self.minsize(300, 300)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        for i in range(5):
            self.rowconfigure(i, weight=1)

    def select_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")])
        if filename:
            self.filename = filename
            messagebox.showinfo(
                "Info", f"Selected file: {os.path.basename(self.filename)}")

    def login(self):
        login_dialog = LoginDialog(self)
        self.wait_window(login_dialog)

    def create_password(self):
        now = datetime.datetime.now()
        year, week, _ = now.isocalendar()
        password_str = f"{year}{week}"
        return hashlib.sha256(password_str.encode()).hexdigest()

    def start(self):
        if not self.filename:
            messagebox.showerror("Error", "No file selected.")
            return

        self.start_button["state"] = "disabled"
        messagebox.showinfo(
            "Info", "Move the cursor to the desired position and press 's'.")
        self.start_button.focus_set()  # set focus on start button

        self.bind('<s>', self.save_position)

    def save_position(self, event):
        self.position = pyautogui.position()
        self.position_label["text"] = f"Saved position: {self.position}"
        self.unbind('<s>')

        self.start_process()

    def start_process(self):
        t = threading.Thread(target=self.process)
        t.start()

    def process(self):
        if self.filename is None:
            messagebox.showerror("Error", "No file selected.")
            return

        with open(self.filename, 'r', encoding='utf-8') as f:  # 读取用户选定的文件
            lines = f.readlines()

        time.sleep(0.5)
        num_iter = int(self.iter_var.get())
        self.progress['maximum'] = num_iter
        start_time = time.time()

        for i in range(num_iter):
            pyautogui.doubleClick(self.position)
            line = random.choice(lines).strip()
            pyperclip.copy(line)
            pyautogui.hotkey('command')
            pyautogui.hotkey('command', 'v')
            pyautogui.press('enter')

            self.progress['value'] = i+1
            elapsed_time = time.time() - start_time
            remaining_time = elapsed_time * (num_iter - (i+1)) / (i+1)
            eta = datetime.timedelta(seconds=int(remaining_time))
            self.progress_label['text'] = f"Progress: {i+1}/{num_iter}, ETA: {eta}"
            self.update_idletasks()  # update GUI

            time.sleep(5)

        self.start_button["state"] = "normal"
        messagebox.showinfo("Info", "Process completed!")

    def show_about(self):
        tk.messagebox.showinfo("关于", "版本: 1.0\n作者: 脑子露馅")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
