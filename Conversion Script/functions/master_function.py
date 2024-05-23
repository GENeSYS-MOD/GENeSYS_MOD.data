import pandas as pd
import os
from functions.compare_update_csv import update_or_append_csv
from functions.transform_data import transform_wide_to_long  # Ensure this import is correct

def process_excel_to_csv(excel_path, data_folder):
    # Load the Excel file within a context manager to ensure it's properly closed
    with pd.ExcelFile(excel_path) as xls:
        # Read the "Sets" sheet to get valid dimension headers and regions
        sets_data = pd.read_excel(xls, sheet_name='Sets', header=None)
        valid_dimensions = sets_data.iloc[0].tolist()
        known_regions = sets_data.iloc[:, 0].dropna().tolist()  # Assuming regions are listed in the first column

        # Process only the specified sheet
        sheet_name = 'Par_GrowthRateTradeCapacity'
        print(f"Processing sheet: {sheet_name}")
        data = pd.read_excel(xls, sheet_name)

        # Check if there is a 'Value' column
        if 'Value' in data.columns:
            transformed_data = data
        else:
            # Identify id_vars and value_vars
            id_vars = [col for col in data.columns if col in valid_dimensions]
            value_vars = [col for col in data.columns if col not in id_vars]

            # Ensure 'Year' is included in id_vars if it exists
            if 'Year' in data.columns and 'Year' not in id_vars:
                id_vars.append('Year')
                value_vars.remove('Year')

            # Specific case handling for Region columns based on known regions
            if any(col in known_regions for col in value_vars):
                id_vars = [col for col in data.columns if col in valid_dimensions]
                value_vars = [col for col in data.columns if col in known_regions]
                melted_column_name = 'Region2'
            else:
                melted_column_name = 'Variable'

            # Ensure only valid value_vars are passed
            value_vars = [var for var in value_vars if var in data.columns]

            # Debugging: Print identified id_vars, value_vars, and DataFrame columns
            print("Identified id_vars:", id_vars)
            print("Identified value_vars:", value_vars)
            print("DataFrame columns before melting:", data.columns)

            transformed_data = transform_wide_to_long(data, id_vars=id_vars, value_vars=value_vars, var_name=melted_column_name)

        # Debugging: print the headers of the transformed data
        print("Headers of the transformed data:", transformed_data.columns)

        # Define the path to the CSV file
        parameter_folder = os.path.join(data_folder, f"{sheet_name}")
        if not os.path.exists(parameter_folder):
            os.makedirs(parameter_folder)
        csv_path = os.path.join(parameter_folder, f"{sheet_name}.csv")

        # Update or append the CSV file
        update_or_append_csv(csv_path, transformed_data)

    print("Finished processing the specified sheet.")
    return
