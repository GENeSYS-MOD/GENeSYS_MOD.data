import os
import pandas as pd

def process_regular_parameters(csv_file_path, unique_values_concatenated, output_format, scenario_option, debugging_output, data_base_region):
    # Compute and truncate worksheet_name to ensure it doesn't exceed 31 characters
    worksheet_name = os.path.splitext(os.path.basename(csv_file_path))[0]
    if len(worksheet_name) > 31:
        worksheet_name = worksheet_name[:31]
    
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(csv_file_path, delimiter=',')
    
    # Delete empty lines 
    df.dropna(how='all', inplace=True)

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

            # Handling of 'All' entries
            df_scenario = process_all_year(df_scenario, unique_values_concatenated)
            df_scenario = process_all_fuel(df_scenario, unique_values_concatenated)
            df_scenario = process_all_technology(df_scenario, unique_values_concatenated)
            df_scenario = process_all_mode(df_scenario, unique_values_concatenated)

            # Get the index of the "Value" column in each DataFrame
            value_col_index = df.columns.get_loc("Value")
            value_col_index_scenario = df_scenario.columns.get_loc("Value")

            # Drop all columns that come after the "Value" column
            df = df.iloc[:, :(value_col_index + 1)]
            df_scenario = df_scenario.iloc[:, :(value_col_index_scenario + 1)]  
            
            # Save column order before processing
            col_ordr = df.columns.tolist()

            # Identify common columns excluding 'Value'
            common_cols = [col for col in df.columns if col in df_scenario.columns and col != 'Value']

            # Ensure consistent data types before merging by converting to string
            for col in common_cols:
                df[col] = df[col].apply(lambda x: str(int(x)) if isinstance(x, (int, float)) and float(x).is_integer() else str(x))
                df_scenario[col] = df_scenario[col].apply(lambda x: str(int(x)) if isinstance(x, (int, float)) and float(x).is_integer() else str(x))
            
            # Merge on common columns excluding 'Value', updating 'Value' from df_scenario
            df = df.merge(df_scenario, on=common_cols, how='left', suffixes=('', '_updated'))
            df['Value'] = df['Value_updated'].combine_first(df['Value'])
            df.drop('Value_updated', axis=1, inplace=True)

            # Append any additional rows from df_scenario
            additional_rows = df_scenario[~df_scenario[common_cols].apply(tuple,1).isin(df[common_cols].apply(tuple,1))]
            df = pd.concat([df, additional_rows], ignore_index=True)

            # Ensure the column order is the same as originally
            df = df[col_ordr]

            data_overwritten = True

    # Handling of 'All' entries
    df = process_all_year(df, unique_values_concatenated)
    df = process_all_fuel(df, unique_values_concatenated)
    df = process_all_technology(df, unique_values_concatenated)
    df = process_all_mode(df, unique_values_concatenated)

    # Set regional values, if only value given for base-region
    if worksheet_name in [
       "Par_CapitalCost", 
       "Par_VariableCost", 
       "Par_FixedCost", 
       "Par_AvailabilityFactor", 
       "Par_InputActivityRatio", 
       "Par_OutputActivityRatio", 
       "Par_EmissionPenaltyTagTech", 
       "Par_ReserveMarginTagTechnology", 
       "Par_EmissionActivityRatio", 
       "Par_EmissionsPenalty",
       "Par_SpecifiedDemandDevelopment",
       "Par_RegionalModelPeriodEmission",
       "Par_ModelPeriodExogenousEmissio"]:
        df = set_regional_values_from_base(df, unique_values_concatenated, data_base_region)
    
    # Set values, if no regional data available
    if worksheet_name in [
        "Par_CapitalCost",
        "Par_VariableCost",
        "Par_FixedCost",
        "Par_AvailabilityFactor",
        "Par_InputActivityRatio",
        "Par_OutputActivityRatio",
        "Par_EmissionPenaltyTagTech",
        "Par_ReserveMarginTagTechnology",
        "Par_EmissionActivityRatio",
        "Par_ReserveMarginTagFuel",
        "Par_ReserveMargin",
        "Par_MinStorageCharge",
        "Par_CapitalCostStorage",
        "Par_RegionalAnnualEmissionLimit",
        "Par_RegionalModelPeriodEmission",
        "Par_ModelPeriodExogenousEmissio",
        "Par_TotalAnnualMaxCapacity",
        "Par_SpecifiedDemandDevelopment",
        "Par_AnnualMaxNewCapacity"
        ]:
        df = set_values_from_world(df, unique_values_concatenated)

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

def process_all_year(df, unique_values_concatenated):
    # Check if 'Year' column exists
    if 'Year' in df.columns:
        
        # Identify rows where 'Year' originally had the value 'All'
        all_rows = df[df['Year'] == 'All'].copy()
    
        # Define the replacement years
        replacement_years = unique_values_concatenated['Year'].dropna().astype(int).astype(str)

        # Get the index of the "Value" column in the DataFrame
        value_col_index = df.columns.get_loc("Value")

        # Drop all columns that come after the "Value" column
        df = df.iloc[:, :(value_col_index + 1)]

        # Identify columns to check for duplicates (excluding the 'Value' column)
        columns_to_check = [col for col in df.columns if col != 'Value']

        # Create a set of existing row signatures for fast duplicate detection
        existing_keys = set(
            tuple(row) for row in df[columns_to_check].itertuples(index=False, name=None)
        )

        # Create new rows by repeating the 'All' rows with different years
        new_rows = []
        for _, row in all_rows.iterrows():
            for year in replacement_years:
                new_row = row.copy()
                new_row['Year'] = year

                # Check if a similar row already exists
                key = tuple(new_row[col] for col in columns_to_check)
                if key not in existing_keys:
                    new_rows.append(new_row)
                    existing_keys.add(key)

        # Convert new rows to DataFrame if there are new rows to append
        if new_rows:
            new_rows_df = pd.DataFrame(new_rows)
            
            # Append the new rows to the original dataframe
            df = df[df['Year'] != 'All'].copy()  # Drop original rows with 'All' in 'Year'
            df = pd.concat([df, new_rows_df], ignore_index=True)

        # Data conversions and handling NaNs
        df.loc[:, 'Year'] = pd.to_numeric(df['Year'], errors='coerce', downcast='integer')
        df = df.dropna(subset=['Year'])  # Dropping NaNs in 'Year'
    
    return df

def process_all_fuel(df, unique_values_concatenated):
    # Check if 'Fuel' column exists
    if 'Fuel' in df.columns:

        # Identify rows where 'Fuel' originally had the value 'All'
        all_rows = df[df['Fuel'] == 'All']

        # Define the replacement fuels and drop NaN values
        replacement_fuels = unique_values_concatenated['Fuel'].dropna()

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
                df_filtered = df.iloc[:, :(value_col_index + 1)]

                # Identify columns to check for duplicates (excluding the 'Value' column)
                columns_to_check = [col for col in df_filtered.columns if col != 'Value']

                if not columns_to_check:  # If there are no columns to check, skip
                    new_rows.append(new_row)
                    continue

                # Compare the existing rows to the new row excluding the 'Value' column
                match_condition = (df_filtered[columns_to_check] == new_row[columns_to_check].to_dict()).all(axis=1)

                # Only append the new row if it doesn't already exist
                if not match_condition.any():
                    new_rows.append(new_row)

        # Convert new rows to DataFrame if there are new rows to append
        if new_rows:
            new_rows_df = pd.DataFrame(new_rows)

            # Append the new rows to the original dataframe, excluding the rows where 'Fuel' is 'All'
            df = df[df['Fuel'] != 'All'].copy()  # Drop original rows with 'All' in 'Fuel'
            df = pd.concat([df, new_rows_df], ignore_index=True)

    return df

def process_all_technology(df, unique_values_concatenated):
    # Check if 'Technology' column exists
    if 'Technology' in df.columns:

        # Identify rows where 'Technology' originally had the value 'All'
        all_rows = df[df['Technology'] == 'All']

        # Define the replacement technologies and drop NaN values
        replacement_technologies = unique_values_concatenated['Technology'].dropna()

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
                df_filtered = df.iloc[:, :(value_col_index + 1)]

                # Identify columns to check for duplicates (excluding the 'Value' column)
                columns_to_check = [col for col in df_filtered.columns if col != 'Value']

                if not columns_to_check:  # If there are no columns to check, skip
                    new_rows.append(new_row)
                    continue

                # Compare the existing rows to the new row excluding the 'Value' column
                match_condition = (df_filtered[columns_to_check] == new_row[columns_to_check].to_dict()).all(axis=1)

                # Only append the new row if it doesn't already exist
                if not match_condition.any():
                    new_rows.append(new_row)

        # Convert new rows to DataFrame if there are new rows to append
        if new_rows:
            new_rows_df = pd.DataFrame(new_rows)

            # Append the new rows to the original dataframe, excluding the rows where 'Technology' is 'All'
            df = df[df['Technology'] != 'All'].copy()  # Drop original rows with 'All' in 'Technology'
            df = pd.concat([df, new_rows_df], ignore_index=True)

    return df

def process_all_mode(df, unique_values_concatenated):
    if 'Mode_of_operation' in df.columns:

        # Identify rows where 'Mode_of_operation' originally had the value 'All'
        all_rows = df[df['Mode_of_operation'] == 'All']

        # Define the replacement values and drop NaNs
        replacement_mode = unique_values_concatenated['Mode_of_operation'].dropna()

        # Create new rows by repeating the 'All' rows with different Mode_of_operation values
        new_rows = []
        for _, row in all_rows.iterrows():
            for mode in replacement_mode:
                new_row = row.copy()
                new_row['Mode_of_operation'] = mode

                # Get the index of the "Value" column
                value_col_index = df.columns.get_loc("Value")

                # Work only with columns up to and including 'Value'
                df_filtered = df.iloc[:, :(value_col_index + 1)]

                # Define columns to check for duplicates (excluding 'Value')
                columns_to_check = [col for col in df_filtered.columns if col != 'Value']

                if not columns_to_check:
                    new_rows.append(new_row)
                    continue

                # Check if similar row already exists
                match_condition = (df_filtered[columns_to_check] == new_row[columns_to_check].to_dict()).all(axis=1)

                if not match_condition.any():
                    new_rows.append(new_row)

        # Append new rows to the DataFrame
        if new_rows:
            new_rows_df = pd.DataFrame(new_rows)
            df = df[df['Mode_of_operation'] != 'All'].copy()
            df = pd.concat([df, new_rows_df], ignore_index=True)

        # Convert and clean Mode_of_operation column
        df['Mode_of_operation'] = pd.to_numeric(df['Mode_of_operation'], errors='coerce')
        df = df.dropna(subset=['Mode_of_operation'])

    return df

def set_regional_values_from_base(df, unique_values_concatenated, data_base_region):
    # Check if 'Region' column exists
    if 'Region' in df.columns:
        
        # Identify rows where 'Region' originally had the value of data_base_region
        base_rows = df[df['Region'] == data_base_region].copy()

        # Define the replacement regions
        replacement_regions = unique_values_concatenated['Region'].dropna().astype(str)

        # Get the index of the "Value" column in the DataFrame
        value_col_index = df.columns.get_loc("Value")

        # Drop all columns that come after the "Value" column
        df = df.iloc[:, :(value_col_index + 1)]

        # Identify columns to check for duplicates (excluding the 'Value' column)
        columns_to_check = [col for col in df.columns if col != 'Value']

        # Create a set of existing row signatures for fast duplicate detection
        existing_keys = set(
            tuple(row) for row in df[columns_to_check].itertuples(index=False, name=None)
        )

        # Create new rows by repeating the base rows with different regions
        new_rows = []
        for _, row in base_rows.iterrows():
            for region in replacement_regions:
                if row['Value'] == 0:
                    continue  # Skip creation if the value is zero

                new_row = row.copy()
                new_row['Region'] = region

                # Check if a similar row already exists
                key = tuple(new_row[col] for col in columns_to_check)
                if key not in existing_keys:
                    new_rows.append(new_row)
                    existing_keys.add(key)

        # Convert new rows to DataFrame if there are new rows to append
        if new_rows:
            new_rows_df = pd.DataFrame(new_rows)
            
            # Append the new rows to the original dataframe
            df = pd.concat([df, new_rows_df], ignore_index=True)
            
    return df

def set_values_from_world(df, unique_values_concatenated):

    # Nur aktiv werden, wenn es die Region-Spalte gibt
    if 'Region' in df.columns:
    
        # Identify rows where 'Region' originally had the value 'World'
        world_rows = df[df['Region'] == 'World'].copy()

        # Define the replacement regions
        replacement_regions = unique_values_concatenated['Region'].dropna().astype(str)

        # Get the index of the "Value" column in the DataFrame
        value_col_index = df.columns.get_loc("Value")

        # Drop all columns that come after the "Value" column
        df = df.iloc[:, :(value_col_index + 1)]

        # Identify columns to check for duplicates (excluding the 'Value' column)
        columns_to_check = [col for col in df.columns if col != 'Value']

        # Create a set of existing row signatures for fast duplicate detection
        existing_keys = set(
            tuple(row) for row in df[columns_to_check].itertuples(index=False, name=None)
        )

        # Create new rows by repeating the 'World' rows with different regions
        new_rows = []
        for _, row in world_rows.iterrows():
            for region in replacement_regions:
                new_row = row.copy()
                new_row['Region'] = region

                # Check if a similar row already exists
                key = tuple(new_row[col] for col in columns_to_check)
                if key not in existing_keys:
                    new_rows.append(new_row)
                    existing_keys.add(key)

        # Convert new rows to DataFrame if there are new rows to append
        if new_rows:
            new_rows_df = pd.DataFrame(new_rows)

            # Append the new rows to the original dataframe
            df = df[df['Region'] != 'World'].copy()  # Drop original rows with 'World' in 'Region'
            df = pd.concat([df, new_rows_df], ignore_index=True)
    
    return df