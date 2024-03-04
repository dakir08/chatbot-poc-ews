import json
import os
import re


def normalize_spaces(array):
    normalized_array = []
    for item in array:
        # Replace multiple spaces with a single space
        normalized_item = re.sub(r'\s+', ' ', item)
        normalized_array.append(normalized_item)
    return normalized_array

def append_to_json_file(file_path, dict_data):
    # Check if the file exists
    if not os.path.isfile(file_path):
        # Create the file with an empty array
        with open(file_path, 'w') as file:
            json.dump([], file)

    # Read the current data from the file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Append the new dictionary to the array
    data.append(dict_data)

    # Write the updated data back to the file
    with open(file_path, 'w') as file:
        json.dump(data, file)