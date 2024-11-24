import customtkinter as ctk
import threading
import CTkTable
import psutil
import os

LOCATION = os.path.dirname(os.path.abspath(__file__))
os.chdir(LOCATION)

class Manager(ctk.CTkFrame):
    def __init__(self, parent, root):
        super().__init__(parent)
        self.parent = parent
        self.root = root

class Table(CTkTable.CTkTable):
    def __init__(self, parent: Manager):
        super().__init__(parent)

    @staticmethod
    def get_process_data():
        #pdata = []
        for process in psutil.process_iter():
            if process.is_running():
                print(process.pid, process.name(), process.memory_info().rss//1048576, process.cpu_percent(interval=None))

Table.get_process_data()





