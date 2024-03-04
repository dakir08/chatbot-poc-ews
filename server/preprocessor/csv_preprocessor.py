import os
import pandas as pd

class CSVPreProcessor:
    def get_csv_files(self, path):
        """Return a list of CSV file names in the given directory."""
        return [f for f in os.listdir(path) if f.endswith('.csv')]

    def format_row(self, row):
        """Format a DataFrame row into a combined text string."""
        return '; '.join([f'{col}:{val}' for col, val in row.items()])

    def read_and_transform_csv(self, path):
        """Read CSV files from a path and transform their rows into a specific format."""
        files = self.get_csv_files(path)
        data = []

        for file in files:
            # Read each CSV file
            df = pd.read_csv(os.path.join(path, file))

            # Process each row in the DataFrame
            for _, row in df.iterrows():
                formatted_row = self.format_row(row)
                data.append((file, formatted_row))

        df = pd.DataFrame(data, columns=['file_name', 'combined_text'])

        return df