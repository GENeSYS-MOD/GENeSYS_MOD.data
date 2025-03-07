import os
from read_csv_from_directory import process_files

# This function is to process files which require no change in the original data 
def process_unchanged_files(config, main_folder, output_path):
    unchanged_files = config['parameters']['unchanged_files'] 
    for df, file_path in process_files(main_folder):
        param_name = os.path.splitext(os.path.basename(file_path))[0]
        if param_name in unchanged_files:
            file_path = os.path.join(output_path, f'{param_name}.csv')
            df.to_csv(file_path)