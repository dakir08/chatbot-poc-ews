
import json
import pandas as pd


class JsonPreprocessor:
    def __init__(self, file_path):
        self.__file_path = file_path

    def join_content(self):
        with open(self.__file_path, 'r') as file:
            data = json.load(file)

        # Update each dictionary in the array
        for entry in data:
            if 'content' in entry:
                # Join the items in 'content' with a semicolon and add as a new key
                entry["combined_content"] = ';; '.join(entry['content'])

        # Write the updated data back to the file
        with open(self.__file_path, 'w') as file:
            json.dump(data, file)

    def to_dataframe(self):
        return pd.read_json(self.__file_path)