import os
import pandas as pd
from datetime import datetime

def find_matching_sheets(excel_file_path, base_directory, data_dict):
    """
    Finds the sheets in the original Excel file that have corresponding folders
    in the base directory, and provides a list of CSV files in those folders along with their headers.
    Also transforms the CSV data by removing columns after the "Value" column and converting "Region.1" to "Region2".
    Compares the headers of the transformed Excel data and CSV data, and merges the data based on specified rules.
    
    Parameters:
    excel_file_path (str): The path to the Excel file.
    base_directory (str): The path to the base directory containing folders named after the sheets.
    data_dict (dict): The dictionary containing transformed Excel data frames.
    
    Returns:
    list: A list of tuples with CSV file names and their headers.
    """
    # Use a context manager to ensure the Excel file is properly closed after reading
    with pd.ExcelFile(excel_file_path) as excel_file:
        # Read the Excel file to get the sheet names
        sheet_names = excel_file.sheet_names
        
        # List to store CSV file info
        csv_files_info = []
        processed_sheets = 0
        
        # Check for each sheet name if there is a corresponding folder
        for sheet_name in sheet_names:
            # Skip the first sheet named "Sets"
            if sheet_name == "Sets":
                continue

            print(f"Processing sheet: {sheet_name}")

            folder_path = os.path.join(base_directory, sheet_name)
            if os.path.isdir(folder_path):
                # Look for CSV files in the folder
                for file_name in os.listdir(folder_path):
                    if file_name.endswith('.csv'):
                        csv_path = os.path.join(folder_path, file_name)
                        df_csv = pd.read_csv(csv_path)
                        
                        # Save additional columns to be retained later
                        additional_columns = df_csv.columns[df_csv.columns.get_loc('Value')+1:]
                        additional_df = df_csv[additional_columns].copy()
                        additional_df.index = df_csv.index
                        
                        # Remove all columns after the "Value" column for comparison
                        if 'Value' in df_csv.columns:
                            value_index = df_csv.columns.get_loc('Value')
                            df_csv_for_comparison = df_csv.iloc[:, :value_index+1]
                        
                        # Convert "Region.1" headers to "Region2"
                        df_csv_for_comparison.columns = [col.replace('Region.1', 'Region2') for col in df_csv_for_comparison.columns]
                        
                        # Get the transformed Excel data for the corresponding sheet
                        df_excel = data_dict.get(sheet_name)
                        
                        # Skip if Excel data is empty
                        if df_excel.empty:
                            print(f"Excel data for sheet '{sheet_name}' is empty. Skipping merge.")
                            continue
                        
                        # Drop rows with NaN values in the Excel data for sheets containing Region 2
                        if any(col in df_excel.columns for col in ["Region2"]):
                            df_excel.dropna(inplace=True)
                        
                        # Check if there are still NaN values in the Excel data
                        if df_excel.isna().any().any():
                            raise ValueError(f"Cells without entries exist in the sheet '{sheet_name}'. Please ensure that this is intended.")
                        
                        # Convert Excel data to match CSV data types
                        for col in df_excel.columns:
                            if col in df_csv_for_comparison.columns:
                                df_excel[col] = df_excel[col].astype(df_csv_for_comparison[col].dtype)
                        
                        # Compare headers
                        headers_csv = df_csv_for_comparison.columns.tolist()
                        headers_excel = df_excel.columns.tolist()
                        
                        if set(headers_csv) != set(headers_excel):
                            raise ValueError(f"Header mismatch in sheet '{sheet_name}':\n"
                                             f"CSV headers: {headers_csv}\n"
                                             f"Excel headers: {headers_excel}")
                        
                        # Ensure the merge columns are of the same type
                        df_excel = df_excel[headers_csv]

                        merge_columns = headers_excel[:-1]
                        for col in merge_columns:
                            if df_csv_for_comparison[col].dtype != df_excel[col].dtype:
                                df_csv_for_comparison[col] = df_csv_for_comparison[col].astype(df_excel[col].dtype)
                        
                        # Merge data according to specified rules
                        merged_df = pd.merge(df_csv_for_comparison, df_excel, how='outer', on=merge_columns, suffixes=('_csv', '_excel'))
                        
                        # Update values and additional columns from Excel where both entries exist, otherwise keep existing or append new
                        def update_row(row, unit_values, current_date, additional_df):
                            if pd.notna(row['Value_excel']) and row['Value_excel'] != row['Value_csv']:
                                row['Value'] = row['Value_excel']
                                if len(unit_values) == 1:
                                    row['Unit'] = unit_values[0]
                                else:
                                    row['Unit'] = "UNIT MISSING"
                                row['Source'] = "Automatically generated entry, please add source!"
                                row['Updated at'] = current_date
                                row['Updated by'] = "Automatically generated entry, please add!"
                            else:
                                row['Value'] = row['Value_csv']
                                for col in additional_columns:
                                    if row.name in additional_df.index:
                                        row[col] = additional_df.at[row.name, col]
                                    else:
                                        row[col] = None
                            return row
                        
                        unit_values = df_csv['Unit'].unique()
                        current_date = datetime.now().strftime("%d.%m.%Y")
                        merged_df = merged_df.apply(update_row, axis=1, unit_values=unit_values, current_date=current_date, additional_df=additional_df)
                        
                        # Add "Unnamed:..." columns with empty values to merged_df
                        unnamed_columns = [col for col in additional_columns if col.startswith('Unnamed:')]
                        for col in unnamed_columns:
                            if col not in merged_df.columns:
                                merged_df[col] = ""
                        
                        # Select only existing columns
                        valid_columns = [col for col in df_csv.columns if col in merged_df.columns]
                        merged_df = merged_df[valid_columns]
                        
                        # Save the updated CSV file
                        merged_df.to_csv(csv_path, index=False)
                        
                        # Update the csv_files_info with transformed data
                        csv_files_info.append((file_name, merged_df.columns.tolist()))

                        # Increment the processed sheets counter
                        processed_sheets += 1

                        # Exit after processing the specified number of sheets for easier debugging
                        #num_sheets_to_process = 2
                        #if processed_sheets >= num_sheets_to_process:
                            #return csv_files_info
    
    return csv_files_info
