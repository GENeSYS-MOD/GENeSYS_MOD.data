import os
from functions.read_excel import read_excel
from functions.transform_data import transform_wide_to_long
from functions.compare_update_csv import update_or_append_csv

def process_excel_to_csv(excel_path, data_folder):
    sheets = read_excel(excel_path)
    
    for sheet_name, data in sheets.items():
        if sheet_name.startswith('Par_'):
            # Assume the last 7 columns are year columns, and others are identifiers
            id_vars = data.columns[:-7].tolist()
            value_vars = data.columns[-7:].tolist()  # Adjust this based on actual year columns
            transformed_data = transform_wide_to_long(data, id_vars=id_vars, value_vars=value_vars)

            # Debugging step: Print transformed data columns
            print(f"Transformed data for sheet {sheet_name}:")
            print(transformed_data.columns)

            parameter_folder = os.path.join(data_folder, f"{sheet_name}")
            csv_path = os.path.join(parameter_folder, f"{sheet_name}.csv")
            update_or_append_csv(csv_path, transformed_data)
