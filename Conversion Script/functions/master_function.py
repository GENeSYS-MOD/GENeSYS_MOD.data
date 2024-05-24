import os
from functions.read_excel import read_excel
from functions.transform_data import transform_data
from functions.compare_update_csv import update_or_append_csv

def process_excel_to_csv(excel_file_path, data_folder_path):
    # Read Excel file
    data, sets_data = read_excel(excel_file_path)

    # Transform data
    transformed_data = transform_data(data, sets_data)

    # Process each sheet
    sheet_counter = 0
    for sheet_name, df in transformed_data.items():
        if sheet_name == 'Sets':
            continue  # Skip the Sets sheet itself

        print(f"Processing sheet: {sheet_name}")
        parameter_folder = os.path.join(data_folder_path, f"{sheet_name}")
        csv_path = os.path.join(parameter_folder, f"{sheet_name}.csv")

        if os.path.exists(parameter_folder):
            update_or_append_csv(csv_path, df)

        sheet_counter += 1
        if sheet_counter >= 1:
            print("Processed one sheet, stopping for easier checks.")
            break

    print("Finished processing the specified sheets.")
