import os
import pandas as pd

def output_regular_parameters(dataframes_dict, output_directory, output_excel_file_path):
    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)
        
    # Sort worksheet names alphabetically, but keep 'Sets' at the beginning
    sorted_worksheet_names = ['Sets'] + sorted([name for name in dataframes_dict if name != 'Sets'])

    # Write to Excel file
    with pd.ExcelWriter(output_excel_file_path, engine='xlsxwriter', mode='w') as excel_writer:
        for worksheet_name in sorted_worksheet_names:
            df_to_output = dataframes_dict[worksheet_name]
            df_to_output.to_excel(excel_writer, sheet_name=worksheet_name, index=False)
