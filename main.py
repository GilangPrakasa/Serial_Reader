import tkinter as tk
import serial
import threading

class SerialReaderApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Serial Reader")
        self.geometry("400x300")

        self.baudrates = [9600, 19200, 38400, 57600, 115200]
        self.selected_baudrate = tk.StringVar(self)
        self.selected_baudrate.set(self.baudrates[0])

        self.available_ports = self.get_serial_ports()
        self.selected_port = tk.StringVar(self)
        if self.available_ports:
            self.selected_port.set(self.available_ports[0])
        else:
            self.selected_port.set("No ports available")

        self.create_widgets()

    def create_widgets(self):
        # Baudrate Option Menu
        baudrate_label = tk.Label(self, text="Select Baudrate:")
        baudrate_label.pack()
        baudrate_option_menu = tk.OptionMenu(self, self.selected_baudrate, *self.baudrates)
        baudrate_option_menu.pack()

        # COM Port Option Menu
        port_label = tk.Label(self, text="Select COM Port:")
        port_label.pack()
        port_option_menu = tk.OptionMenu(self, self.selected_port, *self.available_ports)
        port_option_menu.pack()

        # Serial Data Display Text Box
        self.serial_data_text = tk.Text(self, height=10, width=40)
        self.serial_data_text.pack()

        # Start Button
        start_button = tk.Button(self, text="Start Reading", command=self.start_reading)
        start_button.pack()

        # Quit Button
        quit_button = tk.Button(self, text="Quit", command=self.quit)
        quit_button.pack()

    def get_serial_ports(self):
        try:
            import serial.tools.list_ports
            ports = [port.device for port in serial.tools.list_ports.comports()]
            return ports
        except ImportError:
            return []

    def start_reading(self):
        baudrate = int(self.selected_baudrate.get())
        port = self.selected_port.get()

        try:
            self.serial_conn = serial.Serial(port, baudrate)
            self.thread = threading.Thread(target=self.read_serial_data)
            self.thread.daemon = True  # Daemonize the thread so it stops on application exit
            self.thread.start()
        except serial.SerialException as e:
            self.serial_data_text.insert(tk.END, f"Error: {e}\n")

    def read_serial_data(self):
        while True:
            if hasattr(self, 'serial_conn'):
                data = self.serial_conn.readline().decode().strip()
                self.serial_data_text.insert(tk.END, f"{data}\n")
                self.serial_data_text.see(tk.END)  # Scroll to the end

    def on_closing(self):
        if hasattr(self, 'serial_conn'):
            self.serial_conn.close()
        self.destroy()

if __name__ == "__main__":
    app = SerialReaderApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
