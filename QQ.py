import customtkinter,json,requests
import serial
import threading
import re
from datetime import datetime
from CTkMessagebox import CTkMessagebox

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# REMOVE ANSI ESCAPE CODES IN RAW SERIAL DATA
ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
# EXPECTED DATA
expected = []
mac = []

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("INJECTOR")
        # self.iconbitmap('assets/iconx.ico')

        # configure grid layout
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        self.thread = None
        self.running = False

        # FRAME 1
        self.FR1 = customtkinter.CTkFrame(self, width=200, corner_radius=0, border_width=0)
        self.FR1.grid(row=0, column=3, rowspan=4, sticky="nsew")
        self.FR1.grid_rowconfigure(10, weight=1)
        
        # BAUDRATES
        self.baudrates = ["9600","115200"]
        self.selected_baudrate = customtkinter.StringVar(self)
        self.selected_baudrate.set(self.baudrates[0])
        self.baudrate_option = customtkinter.CTkOptionMenu(self.FR1, width=180, values=self.baudrates, variable=self.selected_baudrate)
        self.baudrate_option.grid(row=0, column=0, padx=10, pady=10)
        self.baudrate_option.set("BAUDRATE")

        # COM PORTS
        self.available_ports = self.get_serial_ports()
        self.selected_port = customtkinter.StringVar(self)
        if self.available_ports:
            self.selected_port.set(self.available_ports[0])
        else:
            self.selected_port.set("No ports available")
        self.port_option = customtkinter.CTkOptionMenu(self.FR1, width=180, values=self.available_ports, variable=self.selected_port)
        self.port_option.grid(row=1, column=0, padx=10, pady=10)
        self.port_option.set("COM PORT")

        # START BUTTON
        self.start_button = customtkinter.CTkButton(self.FR1, width=180, text="START", command=self.start_reading)
        self.start_button.grid(row=2, column=0, padx=10, pady=10)

        # QUIT BUTTON
        self.quit_button = customtkinter.CTkButton(self.FR1, width=180, text="RESTART", command=self.restart)
        self.quit_button.grid(row=3, column=0, padx=10, pady=10)

        # FRAME 2
        self.FR2 = customtkinter.CTkFrame(self, width=0, corner_radius=0, border_width=0)
        self.FR2.grid(row=0, column=2, rowspan=4, sticky="nsew")
        self.FR2.grid_rowconfigure(10, weight=1)

        # self.label = customtkinter.CTkLabel(self.FR2, text="MONITORING", font=customtkinter.CTkFont(size=15, weight="bold"))
        # self.label.grid(row=0, column=1, padx=10, pady=10)

        self.serial_data = customtkinter.CTkTextbox(self.FR2, width=600, height=300, corner_radius=10)
        self.serial_data.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        # sys.stdout = StdoutRedirector(self.monitoring)

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
            self.running = True
            self.thread = threading.Thread(target=self.read_serial_data)
            self.thread.daemon = True  # Daemonize the thread so it stops on application exit
            self.thread.start()
        except serial.SerialException as e:
            self.serial_data.insert(customtkinter.END, f"Error: {e}\n")
    
    def stop_reading(self):
        self.serial_conn.close()
        baudrate = int(self.selected_baudrate.get())
        port = self.selected_port.get()
        self.serial_conn = serial.Serial(port, baudrate)
        

    def read_serial_data(self):
        while self.running:
            if hasattr(self, 'serial_conn'):
                data = self.serial_conn.readline().decode().strip()
                line_without_timestamp = re.sub(r'\(\d+\)\s*', '', data)
                line = ansi_escape.sub('', line_without_timestamp)
                if "W MSG:" in line:
                    print("START SERIAL READING")
                    while self.running:
                        data = self.serial_conn.readline().decode().strip()
                        line_without_timestamp = re.sub(r'\(\d+\)\s*', '', data)
                        line = ansi_escape.sub('', line_without_timestamp)
                        spliting = line.split()
                        if spliting:
                            spliting.pop(0)
                        text = ' '.join(spliting)
                        self.serial_data.insert(customtkinter.END, f"{text}\n")
                        self.serial_data.see(customtkinter.END)
                        if "STATE:" in text:
                            split = text.split(":")
                            state = split[1].strip()
                            expected.append(state)
                            print(expected)
                        if "MAC ADDRESS:" in text:
                            start_index = text.index(":") + 15
                            mac_address = text[start_index:].strip()
                            print(mac_address)
                            # mac.append(state)
                            # print(mac)

    def restart(self):
        self.stop_reading(timeout=5)
        self.serial_conn.close()
        self.serial_data.delete(0.0,"end")
        expected.clear()
        mac.clear()
        self.start_reading()

    def on_closing(self):
        if hasattr(self, 'serial_conn'):
            self.serial_conn.close()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()