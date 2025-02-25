import customtkinter,serial,threading,re,time,datetime,re,csv,time,os.path,csv,random,string
from datetime import datetime
from CTkMessagebox import CTkMessagebox

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# REMOVE ANSI ESCAPE CODES IN RAW SERIAL DATA
ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
# EXPECTED DATA
expected = []
mac = []

date_month = datetime.now().strftime("%m_%Y")
csv_uid = f'ID_BOARD.csv'

header_text_csv = [
        "DATE",
        "UID BOARD",
        "INSPECTOR",
        "ID-COBOX",
        "MAC",
        "RUN BUTTON",
        "FLASH AVR",
        "WDT",
        "DISPLAY BUTTON",
        "BUZZER",
        "LED",
        "RTC",
        "NOR FLASH",
        "RSSI",
        "PWM 30",
        "PWM 70",
        "PWM 100",
        "RSSI VALUE",
        "AVR STATE",
        "STATUS",
        "NOTE",
        "DURATION CHECKING"
        ]

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.uid_generator = UniqueIDGenerator(csv_uid)
        # configure window
        self.title("HARDWARE CHECKER")
        self.iconbitmap('assets/iconx.ico')
        self.resizable(False,False)

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
        self.start_button.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

        # RESTART BUTTON
        self.restart_button = customtkinter.CTkButton(self.FR1, width=300, text="START READING", command=self.stop_reading)
        self.restart_button.grid(row=10, column=0, columnspan=2, padx=10, pady=10)

        # TEXT BOX
        self.serial_data = customtkinter.CTkTextbox(self.FR1, width=600, height=400, corner_radius=10)
        self.serial_data.grid(row=0, column=0,columnspan=4,padx=10, pady=10, sticky="nsew")


        # CHECKLIST BUZZER LED BUTTON FLASH-AVR RTC NOR-FLASH MAC RSSI RUN30 RUN70 RUN100
        self.button = customtkinter.StringVar(value="FAIL")
        self.button = customtkinter.CTkCheckBox(self.FR1, text="RUN BUTTON", text_color="yellow", variable=self.button, onvalue="PASS", offvalue="FAIL")
        self.button.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.flash_avr = customtkinter.StringVar(value="FAIL")
        self.flash_avr = customtkinter.CTkCheckBox(self.FR1, text="FlashAVR", text_color="yellow", variable=self.flash_avr, onvalue="PASS", offvalue="FAIL")
        self.flash_avr.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.wdt = customtkinter.StringVar(value="FAIL")
        self.wdt = customtkinter.CTkCheckBox(self.FR1, text="WDT", text_color="yellow", variable=self.wdt, onvalue="PASS", offvalue="FAIL")
        self.wdt.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.disp_button = customtkinter.StringVar(value="FAIL")
        self.disp_button = customtkinter.CTkCheckBox(self.FR1, text="DISP BUTTON", text_color="yellow", variable=self.disp_button, onvalue="PASS", offvalue="FAIL")
        self.disp_button.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        self.buzzer = customtkinter.StringVar(value="FAIL")
        self.buzzer = customtkinter.CTkCheckBox(self.FR1, text="BUZZER", text_color="yellow", variable=self.buzzer, onvalue="PASS", offvalue="FAIL")
        self.buzzer.grid(row=5, column=0, padx=10, pady=10, sticky="w")
        
        self.led = customtkinter.StringVar(value="FAIL")
        self.led = customtkinter.CTkCheckBox(self.FR1, text="LED", text_color="yellow", variable=self.led, onvalue="PASS", offvalue="FAIL")
        self.led.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        self.rtc = customtkinter.StringVar(value="FAIL")
        self.rtc = customtkinter.CTkCheckBox(self.FR1, text="RTC", text_color="yellow", variable=self.rtc, onvalue="PASS", offvalue="FAIL")
        self.rtc.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.nor = customtkinter.StringVar(value="FAIL")
        self.nor = customtkinter.CTkCheckBox(self.FR1, text="NOR-FLASH", text_color="yellow", variable=self.nor, onvalue="PASS", offvalue="FAIL")
        self.nor.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.rssi_c = customtkinter.StringVar(value="FAIL")
        self.rssi_c = customtkinter.CTkCheckBox(self.FR1, text="RSSI VALUE", text_color="yellow", variable=self.rssi_c, onvalue="PASS", offvalue="FAIL")
        self.rssi_c.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        self.pwm30 = customtkinter.StringVar(value="FAIL")
        self.pwm30 = customtkinter.CTkCheckBox(self.FR1, text="RUN-30", text_color="yellow", variable=self.pwm30, onvalue="PASS", offvalue="FAIL")
        self.pwm30.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        self.pwm70 = customtkinter.StringVar(value="FAIL")
        self.pwm70 = customtkinter.CTkCheckBox(self.FR1, text="RUN-70", text_color="yellow", variable=self.pwm70, onvalue="PASS", offvalue="FAIL")
        self.pwm70.grid(row=5, column=1, padx=10, pady=10, sticky="w")

        self.pwm100 = customtkinter.StringVar(value="FAIL")
        self.pwm100 = customtkinter.CTkCheckBox(self.FR1, text="RUN-100", text_color="yellow", variable=self.pwm100, onvalue="PASS", offvalue="FAIL")
        self.pwm100.grid(row=6, column=1, padx=10, pady=10, sticky="w")

        self.label_avr = customtkinter.CTkLabel(self.FR1, text="AVR STATUS", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label_avr.grid(row=1, column=2, padx=10, pady=10, sticky="W")

        self.avr_value = customtkinter.StringVar()
        self.avr = customtkinter.CTkEntry(self.FR1, width=150, text_color="red", placeholder_text="AVR", textvariable=self.avr_value)
        self.avr.configure(state="disabled")
        self.avr.grid(row=1, column=3, padx=10, pady=10, sticky="W")
        self.avr_value.set("None")

        self.label_mac = customtkinter.CTkLabel(self.FR1, text="MAC ADDRESS", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label_mac.grid(row=2, column=2, padx=10, pady=10, sticky="W")

        self.mac_value = customtkinter.StringVar()
        self.mac = customtkinter.CTkEntry(self.FR1, width=150, text_color="red", placeholder_text="MAC-ADDRESS", textvariable=self.mac_value)
        self.mac.configure(state="disabled")
        self.mac.grid(row=2, column=3, padx=10, pady=10, sticky="W")
        self.mac_value.set("None")

        self.label_rssi = customtkinter.CTkLabel(self.FR1, text="RSSI VALUE", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label_rssi.grid(row=3, column=2, padx=10, pady=10, sticky="W")

        self.rssi_value = customtkinter.StringVar()
        self.rssi = customtkinter.CTkEntry(self.FR1, width=150, text_color="red", placeholder_text="RSSI-VALUE", textvariable=self.rssi_value)
        self.rssi.configure(state="disabled")
        self.rssi.grid(row=3, column=3, padx=10, pady=10, sticky="W")
        self.rssi_value.set("None")

        self.label_uid = customtkinter.CTkLabel(self.FR1, text="UID CODE", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label_uid.grid(row=4, column=2, padx=10, pady=10, sticky="W")

        self.uid_value = customtkinter.StringVar()
        self.uid = customtkinter.CTkEntry(self.FR1, width=150, text_color="red", placeholder_text="UID", textvariable=self.uid_value)
        # self.uid.configure(state="disabled")
        self.uid.grid(row=4, column=3, padx=10, pady=10, sticky="W")
        self.uid_value.set("None")

        self.label_id = customtkinter.CTkLabel(self.FR1, text="ID COBOX", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label_id.grid(row=5, column=2, padx=10, pady=10, sticky="W")

        self.id = customtkinter.CTkEntry(self.FR1, width=150, placeholder_text="ID COBOX")
        self.id.grid(row=5, column=3, padx=10, pady=10, sticky="W")

        self.label_inspector = customtkinter.CTkLabel(self.FR1, text="INSPECTOR", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label_inspector.grid(row=6, column=2, padx=10, pady=10, sticky="W")

        self.btn_text = customtkinter.StringVar()
        self.inspector_btn = customtkinter.CTkButton(self.FR1, width=150, textvariable=self.btn_text, command=self.set_inspector)
        self.inspector_btn.grid(row=6, column=3, padx=10, pady=10, sticky="W")
        self.inspector_btn.configure(fg_color="red")
        self.btn_text.set("Set Inspector")

        self.label_status = customtkinter.CTkLabel(self.FR1, text="STATUS", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label_status.grid(row=7, column=2, padx=10, pady=10, sticky="w")

        self.status = ["None","PASS","REPAIR"]

        self.status = customtkinter.CTkOptionMenu(self.FR1, width=150, values=["None","PASS","REPAIR"])
        self.status.grid(row=7, column=3, padx=10, pady=10, sticky="W")
        self.status.set("None")

        self.label_note = customtkinter.CTkLabel(self.FR1, text="NOTE", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label_note.grid(row=8, column=2, padx=10, pady=10, sticky="W")

        self.note = customtkinter.CTkEntry(self.FR1, width=150, placeholder_text="NOTE")
        self.note.grid(row=8, column=3, padx=10, pady=10, sticky="W")

        self.save = customtkinter.CTkButton(self.FR1, width=300, text="SAVE", command=self.save_result)
        self.save.grid(row=9, column=2,columnspan=2, padx=10, pady=10)

        self.exit = customtkinter.CTkButton(self.FR1, width=300, text="EXIT", command=self.on_closing)
        self.exit.grid(row=10, column=2,columnspan=2, padx=10, pady=10)

        self.trademark = customtkinter.CTkLabel(self.FR1, text="CONTACT: mahesa.gilang@efishery.com",width=15,height=15, font=customtkinter.CTkFont(size=12,weight="normal"))
        self.trademark.grid(row=11, column=0, columnspan=4, padx=5, pady=5, sticky="W")
        
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
            self.uid_value.set("None")
            self.uid.configure(text_color="red")
            self.serial_reader.stop_reading()
    
    def set_inspector(self):
        dialog = customtkinter.CTkInputDialog(text="Siapa anda ?", title="Set Inspector")
        self.user_input = dialog.get_input()
        self.btn_text.set(f"{self.user_input}")
        x = str(self.user_input)
        if "None" in x:
            CTkMessagebox(title="Message",width=150,height=100,message="ISI DULU INSPECTOR OY!!!!",icon="assets/icon.png", option_1="ok")
            self.inspector_btn.configure(fg_color="red")
        else:
            self.inspector_btn.configure(fg_color="green")

    def generate_id(self):
        self.new_id = self.uid_generator.generate_id()
        return self.new_id

    def write_uid(self):
        self.uid_generator.write_to_csv()
        return

    def save_result(self):
        try:
        # TIMER
            self.t = self.serial_reader.get_start_time()
            end_time = time.time()
            elapsed_time = end_time - self.t
            stopwatch = "{:.2f}".format(elapsed_time)
            data_text = [
                f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                f"{self.uid.get()}",
                f"{self.user_input}",
                f"{self.id.get()}",
                f"{self.mac.get()}",
                f"{self.button.get()}",
                f"{self.flash_avr.get()}",
                f"{self.wdt.get()}",
                f"{self.disp_button.get()}",
                f"{self.buzzer.get()}",
                f"{self.led.get()}",
                f"{self.rtc.get()}",
                f"{self.nor.get()}",
                f"{self.rssi_c.get()}",
                f"{self.pwm30.get()}",
                f"{self.pwm70.get()}",
                f"{self.pwm100.get()}",
                f"{self.rssi_value.get()}",
                f"{self.avr.get()}",
                f"{self.status.get()}",
                f"{self.note.get()}",
                f"{stopwatch}"
                # f"stopwatch"
                ]
            if 'Jancuk' in data_text or 'Jancuk2' in data_text:
                CTkMessagebox(title="Message",width=150,height=100,message="Something was empty & fail",icon="assets/icon.png", option_1="ok")
                # return False
            else:
                if self.uid.get() == self.new_id: 
                    self.write_uid()
                    self.serial_data.insert("end", f"UID APPEND {self.new_id}\n")
                    pass
                self.serial_data.insert("end", f"\n")
                self.serial_data.insert("end", f"ELAPSED TIME :{stopwatch} SECONDS\n")
                header_text = header_text_csv
                check_file = os.path.isfile(f"DATA_QC_FIRMWARE_{date_month}.csv")
                csv_file_path = f"DATA_QC_FIRMWARE_{date_month}.csv"
                if check_file == False:
                    with open(csv_file_path, mode='a', newline='') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow(header_text)
                with open(csv_file_path, mode='a', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(data_text)
                    self.button.deselect()
                    self.flash_avr.deselect()
                    self.wdt.deselect()
                    self.disp_button.deselect()
                    self.buzzer.deselect()
                    self.led.deselect()
                    self.rtc.deselect()
                    self.nor.deselect()
                    self.rssi_c.deselect()
                    self.pwm30.deselect()
                    self.pwm70.deselect()
                    self.pwm100.deselect()
                    self.avr_value.set("None")
                    self.avr.configure(text_color="red")
                    self.mac_value.set("None")
                    self.mac.configure(text_color="red")
                    self.rssi_value.set("None")
                    self.rssi.configure(text_color="red")
                    self.uid_value.set("None")
                    self.uid.configure(text_color="red")
                    self.id.delete(0,20)  
                    # self.btn_text.set("Set Inspector")
                    self.note.delete(0,50)
                    self.status.set("None")
        except:
            CTkMessagebox(title="Message",width=150,height=100,message="GALAT",icon="assets/icon.png", option_1="ok")
            # pass

    def on_closing(self):
        if hasattr(self, 'serial_conn'):
            self.serial_conn.close()
        self.destroy()

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
            self.serial_port = serial.Serial(port, baudrate,timeout=5)
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
                if "verified correctly!" in text:
                    self.app.avr_value.set("AVR PASS")
                    self.app.avr.configure(text_color="yellow")
                if "[FAIL]" in text:
                    self.app.avr_value.set("AVR FAIL")
                    self.app.avr.configure(text_color="red")
                if "MAC ADDRESS:" in text:
                    start_index = text.index(":") + 15
                    mac_address = text[start_index:].strip()
                    if mac_address:
                        print(mac_address)
                        self.app.mac_value.set(f"{mac_address}")
                        self.app.mac.configure(text_color="yellow")
                    else:
                        print("No match found")
                        self.app.mac_value.set("Failed")
                        self.app.mac.configure(text_color="red")
                if "AksesPoin_eFishery:" in text:
                    pattern = r'-\d+ dBm \[.*\]'
                    match = re.search(pattern, text)
                    if match:
                        rssi_value = match.group(0)
                        print(rssi_value)
                        self.app.rssi_value.set(f"{rssi_value}")
                        self.app.rssi.configure(text_color="yellow")
                    else:
                        print("No match found")
                        self.app.rssi_value.set("Failed")
                        self.app.rssi.configure(text_color="red")
                if "TEST FINISHED" in text:
                    self.check_uid = self.app.uid.get()
                    if self.check_uid == "None":
                        self.unique_id =  self.app.generate_id()
                        print("Generated ID:",  self.unique_id)
                        self.app.uid_value.set(f"{ self.unique_id}")
                        self.app.uid.configure(text_color="yellow")
                    else:
                        print("ID: CHECKED",  self.check_uid)
                                  
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
    
class UniqueIDGenerator:
    def __init__(self, csv_filename):
        self.existing_ids = set()
        self.csv_filename = csv_filename
        self.load_existing_ids()

    def load_existing_ids(self):
        try:
            with open(self.csv_filename, 'r', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    self.existing_ids.add(row[0])  # Assuming ID is in the first column
        except FileNotFoundError:
            # If the file does not exist, no existing IDs to load
            pass

    def generate_id(self):
        while True:
            self.new_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            if self.new_id not in self.existing_ids:
                self.existing_ids.add(self.new_id)
                return self.new_id

    def check_text_in_csv(self):
        try:
            with open(self.csv_filename, 'r', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == self.new_id:
                        return True
                return False
        except FileNotFoundError:
            # print(f"File '{self.csv_filename}' not found.")
            return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def write_to_csv(self):
        if self.check_text_in_csv():
            print(f"UID {self.new_id} ALREADY EXIST, PLEASE RESTART READING")
            CTkMessagebox(title="Message",width=150,height=100,message=f"UID {self.new_id} ALREADY EXIST, PLEASE RESTART READING",icon="assets/icon.png", option_1="ok")
        else:
            with open(self.csv_filename, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([self.new_id,datetime.now().strftime("%d/%m/%Y")])

if __name__ == "__main__":
    app = App()
    app.mainloop()
