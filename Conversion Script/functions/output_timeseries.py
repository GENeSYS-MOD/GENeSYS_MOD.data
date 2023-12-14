import os
import pandas as pd

def output_timeseries(filtered_data, output_excel_directory, output_excel_file_path_timeseries, output_csv_directory, output_file_format):
    # Determine the output directory based on the file format
    if output_file_format == 'excel':
        output_directory = output_excel_directory
        output_file_path = output_excel_file_path_timeseries
    else:
        output_directory = output_csv_directory

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    if output_file_format == 'excel':
        # Check if the Excel file exists to decide on the mode
        mode = 'a' if os.path.exists(output_file_path) else 'w'

        # Open the ExcelWriter
        with pd.ExcelWriter(output_file_path, engine='openpyxl', mode=mode) as writer:
            for sheet_name, df in filtered_data.items():
                if mode == 'a' and sheet_name in writer.book.sheetnames:
                    del writer.book[sheet_name]
                df.to_excel(writer, sheet_name=sheet_name, index=False)

    else:
        for file_name, df in filtered_data.items():
            output_file_path = os.path.join(output_directory, f"{file_name}.csv")
            df.to_csv(output_file_path, index=False)
