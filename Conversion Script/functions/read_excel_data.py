import pandas as pd

def read_excel_data(excel_file_path):
    """
    Reads data from an Excel file, ignoring the first sheet named "Sets"
    and reading all other sheets that begin with "Par_".
    
    Parameters:
    excel_file_path (str): The path to the Excel file.
    
    Returns:
    dict: A dictionary where the keys are sheet names and the values are data frames.
    """
    # Use a context manager to ensure the Excel file is properly closed after reading
    with pd.ExcelFile(excel_file_path) as excel_file:
        # Read the "Sets" sheet to get the headers
        sets_df = pd.read_excel(excel_file, sheet_name="Sets")
        
        # Get the headers from the first row of the "Sets" sheet
        sets_headers = sets_df.columns.tolist()
        
        # Convert numeric columns to integers and remove null values
        for col in sets_headers:
            if sets_df[col].dtype in ['float64', 'int64']:
                sets_df[col] = sets_df[col].dropna().astype(int).astype(str).str.strip()
            else:
                sets_df[col] = sets_df[col].dropna().astype(str).str.strip()
        
        # Dictionary to store the data frames
        data_dict = {}
        
        # Iterate through the sheet names
        for sheet_name in excel_file.sheet_names:
            # Ignore the "Sets" sheet and only read sheets that begin with "Par_"
            if sheet_name != "Sets" and sheet_name.startswith("Par_"):
                # Read the sheet into a data frame
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                if not df.empty:
                    # Remove rows where "Region" is "World"
                    if "Region" in df.columns:
                        df = df[df["Region"] != "World"]
                    
                    # Compare headers with the sets_headers, excluding "Value" header
                    headers = df.columns.tolist()
                    uncommon_headers = [header for header in headers if header not in sets_headers and header != 'Value']
                    
                    if uncommon_headers:
                        # Check if all uncommon headers are in a single column of the "Sets" sheet
                        for col in sets_headers:
                            sets_column_data = sets_df[col].dropna().tolist()
                            if all(header in sets_column_data for header in uncommon_headers):
                                # Determine var_name based on whether col is "Region"
                                var_name = "Region2" if col == "Region" else col
                                # Melt the DataFrame from wide to long format
                                df = df.melt(id_vars=[h for h in headers if h not in uncommon_headers], 
                                             value_vars=uncommon_headers, 
                                             var_name=var_name, 
                                             value_name='Value')
                                break
                
                # Store the data frame in the dictionary with the sheet name as the key
                data_dict[sheet_name] = df
    
    return data_dict
