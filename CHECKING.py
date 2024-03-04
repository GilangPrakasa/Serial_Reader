import csv

def check_text_in_csv(filename, column_index, text_to_check):
    try:
        with open(filename, 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[column_index] == text_to_check:
                    return True
            return False
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Example usage:
filename = 'generated_ids.csv'
column_index = 3  # Column index to check text in
text_to_check = 'Los Angeles'

if check_text_in_csv(filename, column_index, text_to_check):
    print(f"'{text_to_check}' exists in column {column_index} of '{filename}'.")
else:
    print(f"'{text_to_check}' does not exist in column {column_index} of '{filename}'.")
