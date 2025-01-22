import os
import pandas as pd

def process_regular_parameters(csv_file_path, unique_values_concatenated, output_format, scenario_option, debugging_output):
    # Compute and truncate worksheet_name to ensure it doesn't exceed 31 characters
    worksheet_name = os.path.splitext(os.path.basename(csv_file_path))[0]
    if len(worksheet_name) > 31:
        worksheet_name = worksheet_name[:31]

    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(csv_file_path, delimiter=',')

    # Initialize data_overwritten as False
    data_overwritten = False
    if debugging_output == True:
        print("File being processed:"+csv_file_path)

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

    # Replace rows containing 'All' in the 'Year' column
    if 'Year' in df.columns:
        
        # Identify rows where 'Year' originally had the value 'All'
        all_rows = df[df['Year'] == 'All']
    
        # Define the replacement years
        replacement_years = unique_values_concatenated['Year']
        replacement_years = replacement_years.dropna()
        replacement_years = replacement_years.astype(int)
        replacement_years = replacement_years.astype(str)

        # Create new rows by repeating the 'All' rows with different years
        new_rows = []
        for _, row in all_rows.iterrows():
            for year in replacement_years:
                new_row = row.copy()
                new_row['Year'] = year
                
                # Get the index of the "Value" column in each DataFrame
                value_col_index = df.columns.get_loc("Value")

                # Drop all columns that come after the "Value" column
                df = df.iloc[:, :(value_col_index + 1)]

                # Check if a similar row already exists
                columns_to_check = [col for col in df.columns if col != 'Value']

                is_duplicate = ((df[columns_to_check] == new_row[columns_to_check].to_dict()).all(axis=1)).any()               

                # Only add the new row if it's not a duplicate
                if not is_duplicate:
                    new_rows.append(new_row)

        # Convert new rows to DataFrame if there are new rows to append
        if new_rows:
            new_rows_df = pd.DataFrame(new_rows)
            
            # Append the new rows to the original dataframe
            df = df[df['Year'] != 'All'].copy()  # Drop original rows with 'All' in 'Year'
            df = pd.concat([df, new_rows_df], ignore_index=True)

        # Data conversions and handling NaNs
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce', downcast='integer')
        dh = df.dropna(subset=['Year']) # Dropping NaNs in 'Year'

    # Replace rows containing 'All' in the 'Fuel' column
    if 'Fuel' in df.columns:

        # Identify rows where 'Fuel' originally had the value 'All'
        all_rows = df[df['Fuel'] == 'All']

        # Define the replacement fuels
        replacement_fuels = unique_values_concatenated['Fuel']
        replacement_fuels = replacement_fuels.dropna()

        # Create new rows by repeating the 'All' rows with different fuels
        new_rows = []
        for _, row in all_rows.iterrows():
            for fuel in replacement_fuels:
                # Create a copy of the original row and replace the 'Fuel' value
                new_row = row.copy()
                new_row['Fuel'] = fuel

                # Get the index of the "Value" column in each DataFrame
                value_col_index = df.columns.get_loc("Value")

                # Drop all columns that come after the "Value" column
                df = df.iloc[:, :(value_col_index + 1)]

                # Check if a similar row already exists
                columns_to_check = [col for col in df.columns if col not in ['Value']]

                if not columns_to_check:  # If there are no columns to check, skip
                    new_rows.append(new_row)
                    continue

                # Compare the existing rows to the new row excluding the 'Value' column
                match_condition = (df[columns_to_check] == new_row[columns_to_check].to_dict()).all(axis=1)

                # Only append the new row if it doesn't already exist
                if not match_condition.any():
                    new_rows.append(new_row)

        # Convert new rows to DataFrame if there are new rows to append
        if new_rows:
            new_rows_df = pd.DataFrame(new_rows)

            # Append the new rows to the original dataframe
            df = df[df['Fuel'] != 'All'].copy()  # Drop original rows with 'All' in 'Fuel'
            df = pd.concat([df, new_rows_df], ignore_index=True)

    # Replace rows containing 'All' in the 'Technology' column
    if 'Technology' in df.columns:

        # Identify rows where 'Technology' originally had the value 'All'
        all_rows = df[df['Technology'] == 'All']

        # Define the replacement technologies
        replacement_technologies = unique_values_concatenated['Technology']
        replacement_technologies = replacement_technologies.dropna()

        # Create new rows by repeating the 'All' rows with different technologies
        new_rows = []
        for _, row in all_rows.iterrows():
            for tech in replacement_technologies:
                # Create a copy of the original row and replace the 'Technology' value
                new_row = row.copy()
                new_row['Technology'] = tech

                # Get the index of the "Value" column in each DataFrame
                value_col_index = df.columns.get_loc("Value")

                # Drop all columns that come after the "Value" column
                df = df.iloc[:, :(value_col_index + 1)]

                # Check if a similar row already exists
                columns_to_check = [col for col in df.columns if col not in ['Value']]

                if not columns_to_check:  # If there are no columns to check, skip
                    new_rows.append(new_row)
                    continue

                # Compare the existing rows to the new row excluding the 'Value' column
                match_condition = (df[columns_to_check] == new_row[columns_to_check].to_dict()).all(axis=1)

                # Only append the new row if it doesn't already exist
                if not match_condition.any():
                    new_rows.append(new_row)

        # Convert new rows to DataFrame if there are new rows to append
        if new_rows:
            new_rows_df = pd.DataFrame(new_rows)

            # Append the new rows to the original dataframe
            df = df[df['Technology'] != 'All'].copy()  # Drop original rows with 'All' in 'Technology'
            df = pd.concat([df, new_rows_df], ignore_index=True)

    if 'Mode_of_operation' in df.columns:
        df['Mode_of_operation'] = df['Mode_of_operation'].astype('Int64', errors='ignore')
        df = df.dropna(subset=['Mode_of_operation'])  # Dropping NaNs in 'Mode_of_operation'

        # Identify rows where 'Technology' originally had the value 'All'
        all_rows = df[df['Mode_of_operation'] == 'All']

        # Define the replacement technologies
        replacement_technologies = unique_values_concatenated['Mode_of_operation']
        replacement_technologies = replacement_technologies.dropna()

        # Create new rows by repeating the 'All' rows with different technologies
        new_rows = []
        for _, row in all_rows.iterrows():
            for tech in replacement_technologies:
                # Create a copy of the original row and replace the 'Technology' value
                new_row = row.copy()
                new_row['Mode_of_operation'] = tech

                # Get the index of the "Value" column in each DataFrame
                value_col_index = df.columns.get_loc("Value")

                # Drop all columns that come after the "Value" column
                df = df.iloc[:, :(value_col_index + 1)]

                # Check if a similar row already exists
                columns_to_check = [col for col in df.columns if col not in ['Value']]

                if not columns_to_check:  # If there are no columns to check, skip
                    new_rows.append(new_row)
                    continue

                # Compare the existing rows to the new row excluding the 'Value' column
                match_condition = (df[columns_to_check] == new_row[columns_to_check].to_dict()).all(axis=1)

                # Only append the new row if it doesn't already exist
                if not match_condition.any():
                    new_rows.append(new_row)

        # Convert new rows to DataFrame if there are new rows to append
        if new_rows:
            new_rows_df = pd.DataFrame(new_rows)

            # Append the new rows to the original dataframe
            df = df[df['Mode_of_operation'] != 'All'].copy()  # Drop original rows with 'All' in 'Technology'
            df = pd.concat([df, new_rows_df], ignore_index=True)



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
