# read_Settings_file.py
import pandas as pd
import os
import numpy as np  # For using np.nan


def read_settings_file(file_path, output_csv_directory, scenario_option, output_format):
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

    # Check if output directory exists, if not, create it
    if not os.path.exists(output_csv_directory):
        os.makedirs(output_csv_directory)
    
    # Create a CSV file containing unique values
    unique_values_csv_file_path = os.path.join(output_csv_directory, f"Sets_{scenario_option}.csv")
    unique_values_concatenated.to_csv(unique_values_csv_file_path, index=False, decimal='.') 
    
    if "Region" in unique_values_concatenated.columns:
        unique_values_concatenated["Region2"] = unique_values_concatenated["Region"]
    
    # Set the Output Format value in the first row
    if not unique_values_concatenated.empty:
        # Initialize the new column with NaNs
        unique_values_concatenated.loc[:, 'Output Format'] = np.nan
        unique_values_concatenated['Output Format'] = unique_values_concatenated['Output Format'].astype('object')
        unique_values_concatenated.at[0, 'Output Format'] = output_format
    
    # Return the concatenated DataFrame of unique values
    return unique_values_concatenated
