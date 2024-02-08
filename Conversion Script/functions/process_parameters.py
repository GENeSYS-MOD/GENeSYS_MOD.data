import os
import pandas as pd

def process_regular_parameters(csv_file_path, unique_values_concatenated, output_format, scenario_option):
    # Compute and truncate worksheet_name to ensure it doesn't exceed 31 characters
    worksheet_name = os.path.splitext(os.path.basename(csv_file_path))[0]
    if len(worksheet_name) > 31:
        worksheet_name = worksheet_name[:31]

    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(csv_file_path, delimiter=',')

    # Initialize data_overwritten as False
    data_overwritten = False


    # Check if a subdirectory for the scenario exists and read additional CSV file
    scenario_folder_path = os.path.join(os.path.dirname(csv_file_path), scenario_option)
    if os.path.exists(scenario_folder_path) and os.path.isdir(scenario_folder_path):
        scenario_csv_file = os.path.join(scenario_folder_path, os.path.basename(csv_file_path))
        if os.path.exists(scenario_csv_file):
            df_scenario = pd.read_csv(scenario_csv_file, delimiter=',')

            # Get the index of the "Value" column in each DataFrame
            value_col_index = df.columns.get_loc("Value")
            value_col_index_scenario = df_scenario.columns.get_loc("Value")

            # Drop all columns that come after the "Value" column
            df = df.iloc[:, :(value_col_index + 1)]
            df_scenario = df_scenario.iloc[:, :(value_col_index_scenario + 1)]  

            # Identify common columns excluding 'Value'
            common_cols = [col for col in df.columns if col in df_scenario.columns and col != 'Value']
            
            # Merge on common columns excluding 'Value', updating 'Value' from df_scenario
            df = df.merge(df_scenario, on=common_cols, how='left', suffixes=('', '_updated'))
            df['Value'] = df['Value_updated'].combine_first(df['Value'])
            df.drop('Value_updated', axis=1, inplace=True)

            # Append any additional rows from df_scenario
            additional_rows = df_scenario[~df_scenario[common_cols].apply(tuple,1).isin(df[common_cols].apply(tuple,1))]
            df = pd.concat([df, additional_rows], ignore_index=True)

            data_overwritten = True

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

    # Get the index of the "Value" column
    value_col_index = df.columns.get_loc("Value")

    # Keep all columns up to and including the "Value" column
    df = df.iloc[:, :(value_col_index + 1)]

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

    return df_pivot, worksheet_name, data_overwritten
