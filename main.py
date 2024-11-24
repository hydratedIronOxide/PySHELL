import customtkinter as ctk
import subprocess
import hashlib
import os

# Initialization
LOCATION = os.path.dirname(os.path.abspath(__file__))
from _console import ConsolePane, Controls
from _cfg import *

# Setting Up
os.chdir(LOCATION)
CONFIG_PATH = os.path.abspath("data.json")
HWID = subprocess.run('wmic csproduct get uuid', capture_output=True).stdout.split(b'\n')[1].decode('utf-8').strip()
PID = os.getpid()

# Main Application Class
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        #self.auth_window = Auth(self)
        #self.auth_window.pack(expand=True, fill='both')
        self.start()
        self.mainloop()  # Start GUI

    # Start
    def start(self):
        #self.auth_window.pack_forget()
        #self.main_window = MainWindow(self)
        #self.main_window.pack(expand=True, fill='both')
        self.add_tab_console()
        os.chdir("C:\\")

    # TEST
    def add_tab_console(self):
        self.geometry("800x600+0x0")
        self.minsize(800, 600)
        self.resizable(True, True)
        self.title("Python Shell")
        self.console_pane = ConsolePane(self, self, self)
        self.console_control = Controls(self, self, self)
        self.console_pane.pack(expand=True, fill='both', side='left', padx=(0,2))
        self.console_control.pack(fill='both', side='left', padx=(2,0))

    # Utility methods
    @staticmethod
    def self_destruct() -> None:
        #os.remove(LOCATION)
        exit()

    @staticmethod
    def check_password(pwd: str) -> bool:
        entered = hashlib.sha256(pwd.encode()).hexdigest()
        with open(f"{os.getenv('APPDATA')}\\pyshell_token", 'r') as f:
            file = f.read().split("\n")
        return (file[0], file[1]) == (HWID, entered)

# Authentication Class
class Auth(ctk.CTkFrame):
    def __init__(self, parent: App):
        super().__init__(parent, fg_color='transparent')
        self.parent = parent
        self.counter = 0
        self.parent.title("Enter Password")
        self.parent.geometry("400x200")
        self.parent.resizable(False, False)
        self.entered_password = ctk.StringVar(value='')
        textbox = ctk.CTkEntry(self, textvariable=self.entered_password, show='•')
        button = ctk.CTkButton(self, command=self.check_password, text='Verify')
        textbox.pack(expand=True, anchor='s', pady=10)
        button.pack(expand=True, anchor='n', pady=10)

    def check_password(self):
        if not self.entered_password.get(): return
        #if self.counter == 3: App.self_destruct()
        if App.check_password(self.entered_password.get()):
            self.parent.start()
        else:
            self.counter += 1
            self.entered_password.set('')
            self.wrong_password()

    def wrong_password(self):
        label = ctk.CTkLabel(self, text="Wrong Password!", text_color='#D20103')
        label.place(relx=0.5, rely=0.9, anchor='center')
        self.after(3000, label.place_forget)

# Main Window Class
class MainWindow(ctk.CTkTabview):
    def __init__(self, parent: App):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.parent.geometry("800x600+0x0")
        self.parent.minsize(800, 600)
        self.parent.resizable(True, True)
        self.parent.title("Python Shell")
        self.add_tab_console()

    def add_tab_console(self):
        self.console_container = self.add("Console")
        self.console_container.configure(bg_color="transparent")
        self.console_pane = ConsolePane(self.console_container, self.parent, self)
        self.console_control = Controls(self.console_container, self.parent, self)
        self.console_pane.pack(expand=True, fill='both', side='left', padx=(0,2))
        self.console_control.pack(fill='both', side='left', padx=(2,0))

    def add_tab_task(self):
        self.task_container = self.add("TaskMgr")
        self.console_container.configure(bg_color="transparent")

# RUN
if __name__ == '__main__':
    App()
