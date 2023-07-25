import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import Toplevel as tkToplevel
from PIL import Image, ImageTk
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
        self.title("验证")
        self.geometry("500x300")

        self.label = tk.Label(self, text="输入密码:")
        self.label.pack(pady=5)

        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        self.submit_button = tk.Button(
            self, text="提交", command=self.check_password)
        self.submit_button.pack(pady=5)

        self.protocol('WM_DELETE_WINDOW', self.on_closing)

    def check_password(self):
        entered_password = self.password_entry.get()

        if entered_password == self.master.password:
            self.destroy()
        else:
            messagebox.showerror("Error", "密码错误")

    def on_closing(self):
        self.master.destroy()  # End the main program


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("弹幕助手 v1.1 - 脑子露馅")
        menu = tk.Menu(self)
        self.config(menu=menu)
        about_menu = tk.Menu(menu)
        menu.add_cascade(label="帮助", menu=about_menu)
        about_menu.add_command(label="关于", command=self.show_about)

        self.password = self.create_password()
        self.login()

        self.label_iter = tk.Label(self, text="点击次数:")
        self.label_iter.grid(row=0, column=0)

        self.iter_var = tk.StringVar()
        self.entry_iter = tk.Entry(self, textvariable=self.iter_var, width=10)
        self.entry_iter.grid(row=0, column=1)

        self.file_button = tk.Button(
            self, text="选择文件", command=self.select_file)
        self.file_button.grid(row=1, column=0)

        self.start_button = tk.Button(self, text="开始", command=self.start)
        self.start_button.grid(row=1, column=1)

        self.position_label = tk.Label(self, text="")
        self.position_label.grid(row=2, column=0, columnspan=3)

        self.progress = ttk.Progressbar(self, length=200)
        self.progress.grid(row=3, column=0, columnspan=3, padx=50, sticky='ew')

        self.progress_label = tk.Label(self, text="")
        self.progress_label.grid(row=4, column=0, columnspan=3)

        self.position = None
        self.filename = None

        self.minsize(800, 600)
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
                "Info", f"使用文件: {os.path.basename(self.filename)}")

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
            messagebox.showerror("Error", "缺少文本文件")
            return

        self.start_button["state"] = "disabled"
        messagebox.showinfo(
            "Info", "移动鼠标到目标位置然后按's'来确认")
        self.start_button.focus_set()  # set focus on start button

        self.bind('<s>', self.save_position)

    def save_position(self, event):
        self.position = pyautogui.position()
        self.position_label["text"] = f"点击位置: {self.position}"
        self.unbind('<s>')

        self.start_process()

    def start_process(self):
        t = threading.Thread(target=self.process)
        t.start()

    def process(self):
        if self.filename is None:
            messagebox.showerror("Error", "缺少文本文件")
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
            pyautogui.hotkey('ctrl')
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.press('enter')

            self.progress['value'] = i+1
            elapsed_time = time.time() - start_time
            remaining_time = elapsed_time * (num_iter - (i+1)) / (i+1)
            eta = datetime.timedelta(seconds=int(remaining_time))
            self.progress_label['text'] = f"进度: {i+1}/{num_iter}, 剩余时间: {eta}"
            self.update_idletasks()  # update GUI

            time.sleep(5)

        self.start_button["state"] = "normal"
        messagebox.showinfo("Info", "任务完成!")

    def show_about(self):
        about_window = tk.Toplevel(self)
        about_window.title("关于")
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))

        image_path = os.path.join(application_path, 'about.png')
        image = Image.open(image_path)
        image = image.resize((800, 800), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        about_window.geometry(f"{image.width}x{image.height}")
        about_window.resizable(False, False)
        label = tk.Label(about_window, image=photo)
        label.image = photo
        label.pack()


if __name__ == "__main__":
    app = Application()
    app.mainloop()
