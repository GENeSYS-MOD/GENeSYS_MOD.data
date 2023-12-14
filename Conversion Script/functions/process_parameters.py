import os
import pandas as pd

def process_regular_parameters(csv_file_path, unique_values_concatenated, output_format):
    # Compute and truncate worksheet_name to ensure it doesn't exceed 31 characters
    worksheet_name = os.path.splitext(os.path.basename(csv_file_path))[0]
    if len(worksheet_name) > 31:
        worksheet_name = worksheet_name[:31]

    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(csv_file_path, delimiter=',')

    # Data conversions and handling NaNs
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce', downcast='integer')
        df = df.dropna(subset=['Year'])  # Dropping NaNs in 'Year'

    if 'Mode_of_operation' in df.columns:
        df['Mode_of_operation'] = df['Mode_of_operation'].astype('Int64', errors='ignore')
        df = df.dropna(subset=['Mode_of_operation'])  # Dropping NaNs in 'Mode_of_operation'

    # Rename columns with .1, .2, etc. naming convention
    for col in df.columns:
        if '.' in col:
            base_name, counter = col.split('.')
            new_col_name = f"{base_name}{int(counter) + 1}"  # Add 1 because we start from the first duplicate
            df.rename(columns={col: new_col_name}, inplace=True)

    # Filter DataFrame based on unique_values_concatenated
    columns_to_keep = [col for col in df.columns if col in unique_values_concatenated.columns or col == 'Value']
    df = df[columns_to_keep]

    for header in unique_values_concatenated.columns:
        if header in df.columns:
            df = df[df[header].isin(unique_values_concatenated[header])]    
    
    # Initialize df_pivot
    df_pivot = df  # Default to original DataFrame

    if output_format == 'wide':
        # Determine the pivot column
        pivot_column = 'Region2' if 'Region2' in df.columns and 'Region' in df.columns else 'Year'    
    
        # Pivot the DataFrame if the pivot column exists
        if pivot_column in df.columns:
            # Pivot the DataFrame
            df_pivot = df.pivot(index=[col for col in df.columns if col not in [pivot_column, 'Value']],
                            columns=pivot_column, values='Value').reset_index()

            # Flatten MultiIndex columns (if any)
            df_pivot.columns = ['_'.join(map(str, col)).strip() if isinstance(col, tuple) else str(col) for col in df_pivot.columns.values]

            # Replace NaNs with empty strings for better readability
            df_pivot.replace('nan', '', inplace=True)

    return df_pivot, worksheet_name
