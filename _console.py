import customtkinter as ctk
import subprocess
import threading
import shlex
import glob
import re
import os

LOCATION = os.path.dirname(os.path.abspath(__file__))
os.chdir(LOCATION)

from _cfg import *

# Main Console Pane Class
class ConsolePane(ctk.CTkFrame):
    def __init__(self, parent, root, main):
        super().__init__(parent)
        self.parent = parent
        self.root = root
        self.main = main
        self.command_exec = ctk.StringVar(value='')
        self.saved_instructions = []
        self.counter = 0
        self.instruction_cache = ''
        self.instruction_moved = False
        self.path = ctk.StringVar(value=r"C:\ ")
        self.path_label = ctk.CTkLabel(self, textvariable=self.path, justify='left',
        anchor='w', wraplength=256, font=ctk.CTkFont("Consolas", 16),
        corner_radius=2, height=20)
        self.path_label.pack(fill='both', padx=5, pady=2)
        self.__add_ui()
        self.path_label.bind('<Configure>', lambda _:
        self.path_label.configure(wraplength=self.path_label.winfo_width()))
        self.inputs.bind("<Return>", lambda _: self.on_execution(self.command_exec.get()))
        self.inputs.bind("<Up>", lambda event: self.__load_instructions(event, self.inputs.get()))
        self.inputs.bind("<Down>", lambda event: self.__load_instructions(event, self.inputs.get()))

    def on_execution(self, cmd: str):
        cmd = cmd.strip()
        if cmd == '':
            return
        elif cmd == 'cls':
            self.output_box.clear_screen()
            self.command_exec.set('')
            return
        elif cmd == 'ls':
            cmd = "dir"
        elif 'cd ' in cmd[:3]:
            self.change_dir(cmd[3:])
            return
        elif '.s' in cmd[:3]:
            self.__exec_internal(cmd[3:])
            return
        self.saved_instructions.append(cmd)
        self.counter = 0
        self.command_exec.set('')
        self.instruction_moved = False
        self.output_box.update_output(f">>> {cmd}")
        self.thread(cmd, self.output_box)

    def change_dir(self, path: str):
        path = path.replace("\"", "").replace("\'", "").upper()
        self.path.set(os.path.abspath(path).upper())
        try:
            os.chdir(path)
        except Exception as e:
            self.output_box.update_output(f"Unknown Path: \"{self.path.get()}\"\n{e}")
        else:
            self.output_box.update_output(f"Directory Changed to \"{self.path.get()}\"")
        self.command_exec.set('')

    def __exec_internal(self, cmd: str):
        cmd = cmd.strip()
        args = cmd.split()
        try:
            match args[0]:
                case "d":
                    self.root.self_destruct()
                    self.output_box.update_output(f"Destructor Called")
                case _:
                    raise IndexError
        except IndexError:
            self.output_box.update_output(f"Incorrect Arguments {cmd}")
        self.command_exec.set('')

    def __load_instructions(self, event, passed_cmd: str):
        if len(self.saved_instructions) == 0:
            return
        if not self.instruction_moved:
            self.instruction_cache = passed_cmd
        self.instruction_moved = True
        if event.keysym == 'Up':
            self.counter -= 1
        elif event.keysym == 'Down':
            self.counter += 1
        if self.counter > -1:
            self.counter = 0
            self.command_exec.set(self.instruction_cache)
            return
        elif self.counter < -len(self.saved_instructions):
            self.counter = -len(self.saved_instructions)
        self.command_exec.set(self.saved_instructions[self.counter])

    def __add_ui(self):
        self.output_box = OutputBox(self)
        self.output_box.pack(expand=True, fill='both', padx=5, pady=(0, 5))
        self.inputs = InputBox(self)
        self.inputs.pack(fill='both', padx=5, pady=(0, 5))

    @staticmethod
    def exe(cmd: str, output_ref: 'OutputBox'):
        rc = -1
        cmd = shlex.split(cmd)
        try:
            output = subprocess.run(cmd, shell=True, capture_output=True)
            rc = output.returncode
            for text in output.stdout.decode('utf-8').split('\n'):
                output_ref.after(0, lambda: output_ref.update_output(text))
            if rc != 0:
                for text in output.stderr.decode('utf-8').split('\n'):
                    output_ref.after(0, lambda: output_ref.update_output(text))
        except Exception as e:
            output_ref.after(0, lambda: output_ref.update_output(str(e)))
        finally:
            output_ref.after(0, lambda:
            output_ref.update_output(f"Command {cmd[0]} Executed With Exit Code {rc}"))
            output_ref.after(0, output_ref.scroll_to_end)

    @staticmethod
    def thread(cmd: str, output_ref: 'OutputBox'):
        task_thd = threading.Thread(target=ConsolePane.exe,
                    args=(cmd,output_ref))
        task_thd.daemon = True
        task_thd.start()

# Console Input Box Class
class InputBox(ctk.CTkEntry):
    def __init__(self, parent: ConsolePane):
        super().__init__(parent, textvariable=parent.command_exec, font=ctk.CTkFont("Consolas", 14))
        self.parent = parent
        self.dropdown = None
        self.hide_autocomplete = False
        self.ac = 1
        self.bindtags((str(self), str(self.parent.root), 'all'))
        self.parent.root.bind("<Configure>", self.hide_dropdown)
        self.bind("<KeyRelease>", self.on_key_release)
        self.bind("<Escape>", self.hide_dropdown)
        self.bind("<Tab>", self.tab_event)

    def on_key_release(self, event):
        if self.dropdown: self.dropdown.destroy()
        if event.keysym == 'Escape': return
        if not self.ac: return
        current_input = self.get()
        path_part = self.extract_path(current_input)
        if not path_part:
            if self.dropdown:
                self.dropdown.destroy()
                self.dropdown = None
            return
        suggestions = self.get_path_suggestions(path_part)
        if suggestions:
            self.show_dropdown(suggestions)
            self.update_geometry(suggestions)

    def show_dropdown(self, suggestions):
        if self.dropdown: self.dropdown.destroy()
        if not self.ac: return
        self.dropdown = ctk.CTkToplevel(self.parent.main.parent)
        self.dropdown.wm_overrideredirect(True)
        #self.update_geometry(suggestions)
        sframe = ctk.CTkScrollableFrame(self.dropdown, corner_radius=5)
        for suggestion in suggestions:
            button = ctk.CTkButton(sframe, text=suggestion, anchor="w",
            command=lambda s=suggestion: self.complete_path(s), corner_radius=0,
            fg_color='transparent', hover_color="#3A3A3A", font=ctk.CTkFont(
            "Consolas", 14)); button.pack(fill="x")
        sframe.pack(expand=True, fill='both')

    def update_geometry(self, suggestions):
        entry_x = self.winfo_rootx()
        entry_y = self.winfo_rooty()
        dropdown_height = min(len(suggestions), 5) * 40
        dropdown_y = entry_y - dropdown_height
        geometry = f"{self.winfo_width()-10}x{dropdown_height}+{entry_x + 5}+{dropdown_y - 10}"
        try: self.dropdown.geometry(geometry)
        except Exception as _:
            if self.dropdown:
                self.dropdown.destroy()

    def complete_path(self, selected_path):
        current_input = self.get()
        path_part = self.extract_path(current_input)
        if path_part:
            new_input = current_input.replace(path_part, selected_path)
            self.delete(0, "end")
            self.insert(0, new_input)
        if self.dropdown: self.dropdown.destroy()

    def hide_dropdown(self, _):
        if self.dropdown: self.dropdown.destroy() ; self.dropdown = None
        self.hide_autocomplete = True

    def tab_event(self, _):
        if a := self.get_path_suggestions(self.get()):
            self.complete_path(a[0])

    def disable(self):
        if self.dropdown: self.dropdown.destroy()
        self.ac = 0

    def enable(self):
        self.ac = 1

    @staticmethod
    def get_path_suggestions(current_input):
        matched = re.search(r"[a-zA-Z]:\\[^:]*$|(\.{1,2}[\\/])?[^:\s]*$", current_input)
        if not matched: return []
        current_path = matched.group()
        directory, partial_name = os.path.split(current_path)
        directory = directory or "./"
        try: all_entries = glob.glob(os.path.join(directory, "*"))
        except Exception as e: print(e); return []
        filtered_entries = [entry for entry in all_entries
        if partial_name.lower() in os.path.basename(entry).lower()]
        folders = sorted([entry for entry in filtered_entries if
        os.path.isdir(entry)], key=lambda x: x.lower())
        files = sorted([entry for entry in filtered_entries if
        not os.path.isdir(entry)], key=lambda x: x.lower())
        return folders + files

    @staticmethod
    def extract_path(input_text):
        matched = re.search(r"[a-zA-Z]:\\[^:]*$|(\.{1,2}[\\/])[^:\s]*$", input_text)
        return matched.group() if matched else None

# Console Output Box Class
class OutputBox(ctk.CTkTextbox):
    def __init__(self, parent: ConsolePane):
        super().__init__(parent, state="disabled", wrap='none', font=ctk.CTkFont("Consolas", 16))
        self.parent = parent
        self.bind("<MouseWheel>", self.scroll)

    def update_output(self, text: str):
        self.configure(state="normal")
        self.insert(ctk.END, f"\n{text}")
        self.configure(state="disabled")

    def clear_screen(self):
        self.configure(state="normal")
        self.delete(1.0, ctk.END)
        self.configure(state="disabled")

    def scroll_to_end(self):
        self.see(ctk.END)

    def scroll(self, event):
        def __(*_):
            nonlocal horiz_scroll, scroll, scrolled
            if abs(scrolled) > abs(event.delta) // 105:
                return
            if horiz_scroll:
                self.xview_scroll(scroll, 'units')
            else:
                self.yview_scroll(scroll, 'units')
            scrolled += 1
            self.after(5, __)
        scrolled = 0
        horiz_scroll = (event.state & 0x1) != 0
        scroll = -1 if event.delta > 0 else 1
        __()

# Console Pane Controls Class
class Controls(ctk.CTkFrame):
    def __init__(self, parent, root, main):
        super().__init__(parent)
        self.parent = parent
        self.root = root
        self.main = main
        self.load_qp()
        self.__add_ui()

    def __add_ui(self):
        self.__ui_quickpath()
        self.__ui_sel_file()
        self.__ui_settings()
        self.__ui_util()

    def __ui_quickpath(self):
        frame = ctk.CTkFrame(self, fg_color='#313131')
        frame.columnconfigure(1, uniform='a', weight=1)
        frame.rowconfigure(0, uniform='a', weight=2)
        frame.rowconfigure(1, uniform='a', weight=3)
        ctk.CTkLabel(frame, text="QuickPath", justify='left', anchor='w').grid(
        column=0, row=0, sticky="we", padx=5)
        self.quickpath = ctk.CTkOptionMenu(frame, values=self.qp_list, command=self.select_qp)
        self.quickpath.grid(column=0, row=1, sticky='ew', padx=5, pady=5)
        frame.pack(fill="both", padx=5, pady=5)

    def __ui_sel_file(self):
        frame = ctk.CTkFrame(self, fg_color='#313131')
        frame.columnconfigure(1, uniform='a')
        frame.rowconfigure(0, uniform='a', weight=2)
        frame.rowconfigure(1, uniform='a', weight=3)
        ctk.CTkLabel(frame, text="Open Location", justify='left', anchor='w').grid(
        column=0, row=0, sticky="we", padx=5)
        select_file = ctk.CTkButton(frame, text="Select", command=self.select_file)
        select_file.grid(column=0, row=1, padx=5, pady=5, sticky='ew')
        frame.pack(fill="both", padx=5, pady=5)

    def __ui_settings(self):
        self.path_ac_state = ctk.IntVar(value=1)
        frame = ctk.CTkFrame(self, fg_color='#313131')
        frame.columnconfigure(1, uniform='a')
        frame.rowconfigure(0, uniform='a', weight=2)
        frame.rowconfigure([1], uniform='a', weight=3)
        ctk.CTkLabel(frame, text="Configure", justify='left', anchor='w').grid(
        column=0, row=0, sticky="we", padx=5)
        ac_switch = ctk.CTkSwitch(frame, text="Path Hinting", variable=
        self.path_ac_state, onvalue=1, offvalue=0, command=self.configure_ac)
        ac_switch.grid(column=0, row=1, sticky='ew', padx=5, pady=5)
        frame.pack(fill="both", padx=5, pady=5)

    def __ui_util(self):
        frame = ctk.CTkFrame(self, fg_color='#313131')
        frame.columnconfigure(1, uniform='a')
        frame.rowconfigure(0, uniform='a', weight=2)
        frame.rowconfigure([1,2], uniform='a', weight=3)
        ctk.CTkLabel(frame, text="Tools", justify='left', anchor='w').grid(
        column=0, row=0, sticky="we", padx=5)
        export = ctk.CTkButton(frame, text="Export Output", command=self.select_file)
        export.grid(column=0, row=1, sticky='ew', padx=5, pady=5)
        cls = ctk.CTkButton(frame, text="Clear Screen", command=
        self.main.console_pane.output_box.clear_screen, fg_color="#e23636", hover_color="#8e0000")
        cls.grid(column=0, row=2, sticky='ew', padx=5, pady=5)
        frame.pack(fill="both", padx=5, pady=5)

    def select_qp(self, path):
        try: self.main.console_pane.change_dir(Cfg(0)[path])
        except Exception as e: print(e)

    def select_file(self):
        path = ctk.filedialog.askdirectory(mustexist=True, title="Select Folder")
        if path: self.main.console_pane.change_dir(path)

    def load_qp(self):
        self.qp_list = Cfg(0).k().copy()

    def configure_ac(self):
        if self.path_ac_state.get():
            self.main.console_pane.inputs.enable()
        else:
            self.main.console_pane.inputs.disable()
