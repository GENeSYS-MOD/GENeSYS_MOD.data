import os
import pandas as pd
# Function to read csv files sequentially from the directory as dataframe
def process_files(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('csv'):
                file_path = os.path.join(root, file)
                df = pd.read_csv(file_path)
                yield df, file_path