import psutil
import customtkinter as ctk
from CTkTable import CTkTable


class TaskManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Custom Task Manager with CTkTable")
        self.geometry("800x400")

        # Table for displaying process data
        self.process_table = CTkTable(
            self,
            headers=["PID", "Name", "Memory (MB)"],
            data=[],
            width=780,
            height=300
        )
        self.process_table.pack(pady=10, padx=10, fill="both", expand=True)

        # Buttons for actions
        self.refresh_button = ctk.CTkButton(self, text="Refresh", command=self.update_process_table)
        self.refresh_button.pack(side="left", padx=20, pady=10)

        self.terminate_button = ctk.CTkButton(self, text="Terminate", command=self.terminate_selected_process)
        self.terminate_button.pack(side="right", padx=20, pady=10)

        self.update_process_table()

    def update_process_table(self):
        # Fetch and update process data
        process_data = []
        for process in psutil.process_iter(['pid', 'name', 'memory_info']):
            pid = process.info['pid']
            name = process.info['name']
            memory = process.info['memory_info'].rss / (1024 * 1024)  # Convert bytes to MB
            process_data.append([pid, name, f"{memory:.2f}"])

        # Update table data
        self.process_table.set_data(process_data)

    def terminate_selected_process(self):
        # Get selected row
        selected = self.process_table.get_selected_row()
        if selected:
            pid = selected[0]  # PID is the first column
            try:
                psutil.Process(int(pid)).terminate()
                ctk.CTkMessagebox.show_info(title="Success", message=f"Process {pid} terminated!")
                self.update_process_table()  # Refresh table after termination
            except Exception as e:
                ctk.CTkMessagebox.show_error(title="Error", message=f"Failed to terminate process {pid}: {e}")
        else:
            ctk.CTkMessagebox.show_warning(title="No Selection", message="Please select a process to terminate.")


if __name__ == "__main__":
    app = TaskManagerApp()
    app.mainloop()
