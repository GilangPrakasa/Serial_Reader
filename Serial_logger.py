import customtkinter,serial,threading,re,time,datetime,sys,re,csv,time,os.path
from datetime import datetime
from CTkMessagebox import CTkMessagebox

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# REMOVE ANSI ESCAPE CODES IN RAW SERIAL DATA
ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
# EXPECTED DATA
expected = []
mac = []

header_text_csv = [
        "DATE",
        "INSPECTOR",
        "ID-COBOX",
        "MAC",
        "BUZZER",
        "LED",
        "BUTTON",
        "FLASH-AVR",
        "RTC",
        "NOR-FLASH",
        "RSSI",
        "PWM 30",
        "PWM 70",
        "PWM 100",
        "DURATION CHECKING"
        ]

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("SERIAL LOGGER")

        # configure grid layout
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # FRAME 1
        self.FR1 = customtkinter.CTkFrame(self, width=200, corner_radius=0, border_width=0)
        self.FR1.grid(row=10, column=4, sticky="nsew")
        self.FR1.grid_rowconfigure(10, weight=1)
        
        # BAUDRATES
        self.label_baud = customtkinter.CTkLabel(self.FR1, text="BAUDRATE", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label_baud.grid(row=7, column=0, padx=10, pady=10, sticky="W")

        self.baudrates = ["115200","9600"]
        self.selected_baudrate = customtkinter.StringVar(self)
        self.selected_baudrate.set(self.baudrates[0])
        self.baudrate_option = customtkinter.CTkOptionMenu(self.FR1, width=150, values=self.baudrates, variable=self.selected_baudrate)
        self.baudrate_option.grid(row=7, column=1, padx=10, pady=10)
        # self.baudrate_option.set("BAUDRATE")

        # COM PORTS
        self.label_port = customtkinter.CTkLabel(self.FR1, text="PORT", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label_port.grid(row=8, column=0, padx=10, pady=10, sticky="W")

        self.available_ports = self.get_serial_ports()
        self.selected_port = customtkinter.StringVar(self)
        if self.available_ports:
            self.selected_port.set(self.available_ports[0])
        else:
            self.selected_port.set("No ports available")
        self.port_option = customtkinter.CTkOptionMenu(self.FR1, width=150, values=self.available_ports, variable=self.selected_port)
        self.port_option.grid(row=8, column=1, padx=10, pady=10)
        # self.port_option.set("COM PORT")

        # START BUTTON
        self.start_button = customtkinter.CTkButton(self.FR1, width=300, text="START APP", command=self.start_reading)
        self.start_button.grid(row=7, column=2, columnspan=2, padx=10, pady=10)

        # RESTART BUTTON
        self.restart_button = customtkinter.CTkButton(self.FR1, width=300, text="START READING", command=self.stop_reading)
        self.restart_button.grid(row=8, column=2, columnspan=2, padx=10, pady=10)

        # TEXT BOX
        self.serial_data = customtkinter.CTkTextbox(self.FR1, width=600, height=300, corner_radius=10)
        self.serial_data.grid(row=0, column=0,columnspan=4,padx=10, pady=10, sticky="nsew")


        # CHECKLIST BUZZER LED BUTTON FLASH-AVR RTC NOR-FLASH MAC RSSI RUN30 RUN70 RUN100
        self.buzzer = customtkinter.StringVar(value="FAIL")
        self.buzzer = customtkinter.CTkCheckBox(self.FR1, text="BUZZER", text_color="yellow", variable=self.buzzer, onvalue="PASS", offvalue="FAIL")
        self.buzzer.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        self.led = customtkinter.StringVar(value="FAIL")
        self.led = customtkinter.CTkCheckBox(self.FR1, text="LED", text_color="yellow", variable=self.led, onvalue="PASS", offvalue="FAIL")
        self.led.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.button = customtkinter.StringVar(value="FAIL")
        self.button = customtkinter.CTkCheckBox(self.FR1, text="BUTTON", text_color="yellow", variable=self.button, onvalue="PASS", offvalue="FAIL")
        self.button.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.rtc = customtkinter.StringVar(value="FAIL")
        self.rtc = customtkinter.CTkCheckBox(self.FR1, text="RTC", text_color="yellow", variable=self.rtc, onvalue="PASS", offvalue="FAIL")
        self.rtc.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        
        self.nor = customtkinter.StringVar(value="FAIL")
        self.nor = customtkinter.CTkCheckBox(self.FR1, text="NOR-FLASH", text_color="yellow", variable=self.nor, onvalue="PASS", offvalue="FAIL")
        self.nor.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.pwm30 = customtkinter.StringVar(value="FAIL")
        self.pwm30 = customtkinter.CTkCheckBox(self.FR1, text="RUN-30", text_color="yellow", variable=self.pwm30, onvalue="PASS", offvalue="FAIL")
        self.pwm30.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.pwm70 = customtkinter.StringVar(value="FAIL")
        self.pwm70 = customtkinter.CTkCheckBox(self.FR1, text="RUN-70", text_color="yellow", variable=self.pwm70, onvalue="PASS", offvalue="FAIL")
        self.pwm70.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        self.pwm100 = customtkinter.StringVar(value="FAIL")
        self.pwm100 = customtkinter.CTkCheckBox(self.FR1, text="RUN-100", text_color="yellow", variable=self.pwm100, onvalue="PASS", offvalue="FAIL")
        self.pwm100.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        
        self.avr = customtkinter.CTkOptionMenu(self.FR1, width=150, values=["PASS","FAIL"])
        self.avr.grid(row=1, column=2, padx=10, pady=10, sticky="W")
        self.avr.set("FLASH-AVR")

        self.mac = customtkinter.CTkEntry(self.FR1, width=150, placeholder_text="MAC-ADDRESS")
        self.mac.grid(row=2, column=2, padx=10, pady=10, sticky="W")

        self.rssi = customtkinter.CTkEntry(self.FR1, width=150, placeholder_text="RSSI-VALUE")
        self.rssi.grid(row=3, column=2, padx=10, pady=10, sticky="W")

        self.id = customtkinter.CTkEntry(self.FR1, width=150, placeholder_text="ID-COBOX")
        self.id.grid(row=4, column=2, padx=10, pady=10, sticky="W")

        self.btn_text = customtkinter.StringVar()
        self.inspector_btn = customtkinter.CTkButton(self.FR1, width=150, textvariable=self.btn_text, command=self.set_inspector)
        self.inspector_btn.grid(row=1, column=3, padx=10, pady=10)
        self.btn_text.set("Set Inspector")

        self.save = customtkinter.CTkButton(self.FR1, width=150, text="SAVE", command=self.save_result)
        self.save.grid(row=2, column=3, padx=10, pady=10)

        
    def get_serial_ports(self):
        try:
            import serial.tools.list_ports
            ports = [port.device for port in serial.tools.list_ports.comports()]
            return ports
        except ImportError:
            return []

    def start_reading(self):
        self.start_button.configure(state="disabled")
        self.serial_reader = SerialReader(self)
        self.serial_reader.start_reading()

    def stop_reading(self):
        if hasattr(self, 'serial_reader'):
            self.serial_reader.stop_reading()
    def set_inspector(self):
        dialog = customtkinter.CTkInputDialog(text="Siapa anda ?", title="Set Inspector")
        self.user_input = dialog.get_input()
        self.btn_text.set(f"{app.user_input}")

    def save_result(self):
        # TIMER
        self.t = self.serial_reader.get_start_time()
        end_time = time.time()
        elapsed_time = end_time - self.t
        stopwatch = "{:.2f}".format(elapsed_time)
        self.serial_data.insert("end", f"{stopwatch}\n")
        data_text = [
            f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            f"{self.user_input}",
            f"{self.id.get()}",
            f"{self.mac.get()}",
            f"{self.buzzer.get()}",
            f"{self.led.get()}",
            f"{self.button.get()}",
            f"{self.avr.get()}",
            f"{self.rtc.get()}",
            f"{self.nor.get()}",
            f"{self.rssi.get()}",
            f"{self.pwm30.get()}",
            f"{self.pwm70.get()}",
            f"{self.pwm100.get()}",
            f"{stopwatch}"
            ]
        state_empty = ""
        if state_empty in data_text:
            CTkMessagebox(title="Message",width=150,height=100,message="Something is empty",icon="assets/icon.png", option_1="ok")
        else: 
            header_text = header_text_csv
            date_now = datetime.now().strftime("%d.%m.%Y")
            date_month = datetime.now().strftime("%m.%Y")
            check_file = os.path.isfile(f"{date_month}.csv")
            csv_file_path = f"{date_month}.csv"
            if check_file == False:
                with open(csv_file_path, mode='a', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(header_text)

            with open(csv_file_path, mode='a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(data_text)
                self.mac.delete(0,20)
                self.rssi.delete(0,20)
                self.id.delete(0,20)
                self.buzzer.deselect()
                self.led.deselect()
                self.button.deselect()
                self.rtc.deselect()
                self.nor.deselect()
                self.pwm30.deselect()
                self.pwm70.deselect()
                self.pwm100.deselect()
                self.avr.set("FLASH-AVR")
                self.btn_text.set("Set Inspector")

class SerialReader:
    def __init__(self, app):
        self.app = app
        self.serial_port = None
        self.is_reading = False
        self.read_thread = None

    def start_reading(self):
        baudrate = int(self.app.selected_baudrate.get())
        port = self.app.selected_port.get()
        try:
            self.serial_port = serial.Serial(port, baudrate)
            self.is_reading = True
            self.read_thread = threading.Thread(target=self.read_serial)
            self.read_thread.daemon = True
            self.read_thread.start()
        except serial.SerialException as e:
            print("Error opening serial port:", e)
            CTkMessagebox(title="Message",width=150,height=100,message="Restart application",icon="assets/icon.png", option_1="ok")
            # self.stop_reading()
            # pass

    def read_serial(self):
        while self.is_reading:
            if self.serial_port.in_waiting > 0:
                data = self.serial_port.readline().decode().strip()
                line_without_timestamp = re.sub(r'\(\d+\)\s*', '', data)
                line = ansi_escape.sub('', line_without_timestamp)
                spliting = line.split()
                if spliting:
                    spliting.pop(0)
                text = ' '.join(spliting)
                self.app.serial_data.insert(customtkinter.END, f"{text}\n")
                self.app.serial_data.see(customtkinter.END)
                if "STATE:" in text:
                    split = text.split(":")
                    state = split[1].strip()
                    expected.append(state)
                    print(expected)
                if "MAC ADDRESS:" in text:
                    start_index = text.index(":") + 15
                    mac_address = text[start_index:].strip()
                    print(mac_address)

    def stop_reading(self):
        if self.is_reading:
            self.is_reading = False
            if self.read_thread:
                self.read_thread.join()
            if self.serial_port:
                self.serial_port.close()
        self.app.serial_data.delete(0.0,"end")
        expected.clear()
        mac.clear()
        self.start_time = time.time()
        self.start_reading()

    def get_start_time(self):
        return self.start_time

if __name__ == "__main__":
    app = App()
    app.mainloop()
