import random
import string
from datetime import datetime

class UniqueIDGenerator:
    def __init__(self, txt_filename):
        self.existing_ids = set()
        self.txt_filename = txt_filename
        self.load_existing_ids()

    def load_existing_ids(self):
        try:
            with open(self.txt_filename, 'r') as file:
                for line in file:
                    # Assuming IDs are stored one per line
                    self.existing_ids.add(line.strip())
        except FileNotFoundError:
            # If the file does not exist, no existing IDs to load
            pass

    def generate_id(self):
        while True:
            new_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            if new_id not in self.existing_ids:
                self.existing_ids.add(new_id)
                return new_id

    def write_to_txt(self):
        with open(self.txt_filename, 'w') as file:
            for id in self.existing_ids:
                file.write(f"{id},{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")

class A:
    def __init__(self, txt_filename):
        self.id_generator = UniqueIDGenerator(txt_filename)

    def generate_unique_id(self):
        unique_id = self.id_generator.generate_id()
        print("Generated ID in Class A:", unique_id)
        return unique_id

class B:
    def __init__(self, txt_filename, existing_ids):
        self.id_generator = UniqueIDGenerator(txt_filename)
        self.existing_ids = existing_ids

    def write_unique_ids_to_txt(self):
        for id in self.existing_ids:
            self.id_generator.existing_ids.add(id)
        self.id_generator.write_to_txt()
        print("IDs written to file in Class B.")

# Example usage:
txt_filename = 'ids.txt'

# Create instances of Class A and Class B
a_instance = A(txt_filename)
existing_ids = []

# Generate unique IDs in Class A
for _ in range(5):
    id = a_instance.generate_unique_id()
    existing_ids.append(id)

# Write unique IDs to text file in Class B
b_instance = B(txt_filename, existing_ids)
b_instance.write_unique_ids_to_txt()
