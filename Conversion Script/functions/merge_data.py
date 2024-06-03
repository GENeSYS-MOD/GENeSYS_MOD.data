import os
import pandas as pd

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
    # Read the Excel file to get the sheet names
    excel_file = pd.ExcelFile(excel_file_path)
    sheet_names = excel_file.sheet_names
    
    # List to store CSV file info
    csv_files_info = []
    
    # Check for each sheet name if there is a corresponding folder
    for sheet_name in sheet_names:
        folder_path = os.path.join(base_directory, sheet_name)
        if os.path.isdir(folder_path):
            # Look for CSV files in the folder
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.csv'):
                    csv_path = os.path.join(folder_path, file_name)
                    df_csv = pd.read_csv(csv_path)
                    
                    # Remove all columns after the "Value" column
                    if 'Value' in df_csv.columns:
                        value_index = df_csv.columns.get_loc('Value')
                        df_csv = df_csv.iloc[:, :value_index+1]
                    
                    # Convert "Region.1" headers to "Region2"
                    df_csv.columns = [col.replace('Region.1', 'Region2') for col in df_csv.columns]
                    
                    # Get the transformed Excel data for the corresponding sheet
                    df_excel = data_dict.get(sheet_name)
                    
                    # Compare headers
                    headers_csv = df_csv.columns.tolist()
                    headers_excel = df_excel.columns.tolist()
                    
                    if headers_csv != headers_excel:
                        raise ValueError(f"Header mismatch in sheet '{sheet_name}':\n"
                                         f"CSV headers: {headers_csv}\n"
                                         f"Excel headers: {headers_excel}")
                    
                    # Merge data according to specified rules
                    merged_df = pd.merge(df_csv, df_excel, how='outer', on=headers_excel[:-1], suffixes=('_csv', '_excel'))
                    
                    # Update values from Excel where both entries exist, otherwise keep existing or append new
                    merged_df['Value'] = merged_df['Value_excel'].combine_first(merged_df['Value_csv'])
                    merged_df = merged_df[headers_excel]
                    
                    # Save the updated CSV file
                    merged_df.to_csv(csv_path, index=False)
                    
                    # Update the csv_files_info with transformed data
                    csv_files_info.append((file_name, merged_df.columns.tolist()))
                    
                    # Exit after processing the first sheet for easier debugging
                    return csv_files_info
    
    return csv_files_info
