import tkinter as tk
from tkinter import messagebox
import csv
import random
import string
from datetime import datetime

class UniqueIDGeneratorApp:
    def __init__(self, master, csv_filename):
        self.master = master
        self.csv_filename = csv_filename
        self.unique_id_generator = UniqueIDGenerator(csv_filename)

        self.generate_button = tk.Button(master, text="Generate ID", command=self.generate_id)
        self.generate_button.pack()

        self.write_button = tk.Button(master, text="Write to CSV", command=self.write_to_csv)
        self.write_button.pack()

    def generate_id(self):
        new_id = self.unique_id_generator.generate_id()
        if new_id:
            messagebox.showinfo("Generated ID", f"New ID generated: {new_id}")
        else:
            messagebox.showwarning("Duplicate ID", "Unable to generate a unique ID.")

    def write_to_csv(self):
        if self.unique_id_generator.write_to_csv():
            messagebox.showinfo("Write to CSV", "IDs written to CSV file")
        else:
            messagebox.showwarning("Write to CSV", "No new IDs to write to CSV file")

class UniqueIDGenerator:
    def __init__(self, csv_filename):
        self.existing_ids = set()
        self.csv_filename = csv_filename
        self.load_existing_ids()

    def load_existing_ids(self):
        try:
            with open(self.csv_filename, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    # Assuming IDs are in the first column
                    self.existing_ids.add(row[0])
        except FileNotFoundError:
            # If the file does not exist, no existing IDs to load
            pass

    def generate_id(self):
        new_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if new_id not in self.existing_ids:
            self.existing_ids.add(new_id)
            return new_id
        else:
            return None

    def write_to_csv(self):
        new_ids_written = False
        with open(self.csv_filename, 'a', newline='') as file:
            writer = csv.writer(file)
            for id in self.existing_ids:
                writer.writerow([id])
                new_ids_written = True
        return new_ids_written

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Unique ID Generator")

    csv_filename = "generated_ids.csv"
    app = UniqueIDGeneratorApp(root, csv_filename)

    root.mainloop()
