import os
import pandas as pd

def output_timeseries(filtered_data, output_excel_directory, output_excel_file_path_timeseries):
    # Determine the output directory based on the file format
    output_directory = output_excel_directory
    output_file_path = output_excel_file_path_timeseries

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)
    # Open the ExcelWriter
    with pd.ExcelWriter(output_file_path, engine='xlsxwriter', mode='w') as writer:
        for sheet_name, df in filtered_data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)