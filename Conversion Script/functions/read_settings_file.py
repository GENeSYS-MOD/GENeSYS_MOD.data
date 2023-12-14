# read_Settings_file.py
import pandas as pd
import os

def read_settings_file(file_path, output_csv_directory):
    # Open the Excel file using the provided file path
    xls = pd.ExcelFile(file_path, engine='openpyxl')
    
    # Get the list of sheet names in the Excel file
    sheets_to_read = xls.sheet_names
    
    unique_values_concatenated = pd.DataFrame()
    column_list = []
    
    # Read sheets and store them in the dictionary
    for sheet_name in sheets_to_read:
        data_frame = xls.parse(sheet_name)
    
        filtered_df = data_frame[data_frame.iloc[:, 1] == 1] # Assuming the second column is indexed at 1 (0-based index)
    
        column_list.append(filtered_df.columns[0]) # Collect column header for each set sheet
       
        unique_values = pd.DataFrame(filtered_df.iloc[:, 0].unique())  # Assuming the first column is indexed at 0 (0-based index)
        
        unique_values_concatenated = pd.concat([unique_values_concatenated, unique_values], axis=1)
    
    # Close the Excel file
    xls.close()    
    
    # Need to put header to the DataFrame
    unique_values_concatenated.columns = column_list
    
    # Create a CSV file containing unique values
    unique_values_csv_file_path = os.path.join(output_csv_directory, 'Sets.csv')
    unique_values_concatenated.to_csv(unique_values_csv_file_path, index=False, decimal='.') 
    
    if "Region" in unique_values_concatenated.columns:
        unique_values_concatenated["Region2"] = unique_values_concatenated["Region"]
    
    # Return the concatenated DataFrame of unique values
    return unique_values_concatenated
