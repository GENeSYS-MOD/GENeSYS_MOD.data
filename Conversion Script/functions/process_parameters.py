import os
import pandas as pd

regional_from_base = {
   "Par_CapitalCost", "Par_VariableCost", "Par_FixedCost", "Par_AvailabilityFactor",
   "Par_InputActivityRatio", "Par_OutputActivityRatio", "Par_EmissionPenaltyTagTech",
   "Par_ReserveMarginTagTechnology", "Par_EmissionActivityRatio", "Par_EmissionsPenalty",
   "Par_SpecifiedDemandDevelopment", "Par_RegionalModelPeriodEmission",
   "Par_ModelPeriodExogenousEmissio",
}

values_from_world = {
    "Par_CapitalCost", "Par_VariableCost", "Par_FixedCost", "Par_AvailabilityFactor",
    "Par_InputActivityRatio", "Par_OutputActivityRatio", "Par_EmissionPenaltyTagTech",
    "Par_ReserveMarginTagTechnology", "Par_EmissionActivityRatio",
    "Par_ReserveMarginTagFuel", "Par_ReserveMargin", "Par_MinStorageCharge",
    "Par_CapitalCostStorage", "Par_RegionalAnnualEmissionLimit",
    "Par_RegionalModelPeriodEmission", "Par_ModelPeriodExogenousEmissio",
    "Par_TotalAnnualMaxCapacity", "Par_SpecifiedDemandDevelopment",
    "Par_AnnualMaxNewCapacity", "Par_NewCapacityExpansionStop",
}

def process_regular_parameters(csv_file_path, unique_values_concatenated, rounding_df, output_format, scenario_option, debugging_output, data_base_region, interpolate_missing_values):
    # Compute and truncate worksheet_name to ensure it doesn't exceed 31 characters
    worksheet_name = os.path.splitext(os.path.basename(csv_file_path))[0][:31]
    
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(csv_file_path)
    
    # Delete empty lines 
    df.dropna(how='all', inplace=True)

    # Initialize data_overwritten as False
    data_overwritten = False
    if debugging_output:
        print("File being processed:"+csv_file_path)

    # Check if a subdirectory for the scenario exists and read additional CSV file
    scenario_folder_path = os.path.join(os.path.dirname(csv_file_path), scenario_option)
    if os.path.exists(scenario_folder_path) and os.path.isdir(scenario_folder_path):
        scenario_csv_file = os.path.join(scenario_folder_path, os.path.basename(csv_file_path))
        if os.path.exists(scenario_csv_file):
            df_scenario = pd.read_csv(scenario_csv_file)

            # Drop all columns that come after the "Value" column
            df = trim_after_value(df)
            df_scenario = trim_after_value(df_scenario)
            
            # Interpolate missing yearly values
            if interpolate_missing_values and "Year" in df_scenario.columns:
                target_years = unique_values_concatenated["Year"].dropna()
                df_scenario = interpolate_missing_year_values(df_scenario, target_years)

            # Handling of 'All' entries
            df_scenario = process_all_year(df_scenario, unique_values_concatenated)
            df_scenario = process_all_fuel(df_scenario, unique_values_concatenated)
            df_scenario = process_all_technology(df_scenario, unique_values_concatenated)
            df_scenario = process_all_mode(df_scenario, unique_values_concatenated)

            # Identify common columns excluding 'Value'
            common_cols = [col for col in df.columns if col in df_scenario.columns and col != 'Value']

            # Ensure consistent data types before merging by converting to string
            for col in common_cols:
                df[col] = df[col].apply(lambda x: str(int(x)) if isinstance(x, (int, float)) and float(x).is_integer() else str(x))
                df_scenario[col] = df_scenario[col].apply(lambda x: str(int(x)) if isinstance(x, (int, float)) and float(x).is_integer() else str(x))
            
            # Merge on common columns excluding 'Value', updating 'Value' from df_scenario
            df = df.merge(df_scenario, on=common_cols, how='left', suffixes=('', '_updated'))
            vu = df["Value_updated"]
            df["Value"] = vu.where(vu.notna(), df["Value"])
            df.drop(columns=["Value_updated"], inplace=True)


            ## Determine additional rows from df_scenario that are not already present in df

            base_keys = set(df[common_cols].itertuples(index=False, name=None))

            scenario_keys = df_scenario[common_cols].itertuples(index=False, name=None)
            mask = list(map(lambda k: k not in base_keys, scenario_keys))

            additional_rows = df_scenario.loc[mask].copy()

            if not additional_rows.empty:
                # Ensure the column structure matches the original DataFrame
                additional_rows = additional_rows.reindex(columns=df.columns)

                # Remove completely empty rows (if any)
                additional_rows = additional_rows.dropna(axis=0, how="all")

                # Append additional rows to the main DataFrame
                df = pd.concat([df, additional_rows], ignore_index=True)

            data_overwritten = True

    # Interpolate missing yearly values
    if interpolate_missing_values and "Year" in df.columns:
        target_years = unique_values_concatenated["Year"].dropna()
        df = interpolate_missing_year_values(df, target_years)

    # Handling of 'All' entries
    df = process_all_year(df, unique_values_concatenated)
    df = process_all_fuel(df, unique_values_concatenated)
    df = process_all_technology(df, unique_values_concatenated)
    df = process_all_mode(df, unique_values_concatenated)

    # Set regional values, if only value given for base-region
    if worksheet_name in regional_from_base:
        df = set_regional_values_from_base(df, unique_values_concatenated, data_base_region)
    
    # Set values, if no regional data available
    if worksheet_name in values_from_world:
        df = set_values_from_world(df, unique_values_concatenated)

    # Rename columns with .1, .2, etc. naming convention
    for col in df.columns:
        if '.' in col:
            base_name, counter = col.split('.')
            new_col_name = f"{base_name}{int(counter) + 1}"  # Add 1 because we start from the first duplicate
            df.rename(columns={col: new_col_name}, inplace=True)

    # Keep all columns up to and including the "Value" column
    df = trim_after_value(df)

    # Apply rounding thresholds (rules loaded once from settings file)
    df = apply_rounding_thresholds(df, worksheet_name, rounding_df)

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
    if 'Year' not in df.columns:
        return df

    # Define replacement years
    replacements = (unique_values_concatenated['Year'].dropna().astype(int).astype(str))

    # Expand 'All' rows
    df = expand_all(df, 'Year', replacements)

    # Convert Year column to numeric and remove invalid entries
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce', downcast='integer')
    df = df.dropna(subset=['Year'])

    return df


def process_all_fuel(df, unique_values_concatenated):
    
    # Check if 'Fuel' column exists
    if 'Fuel' not in df.columns:
        return df

    # Define replacement fuels and exclude ETS
    replacements = unique_values_concatenated['Fuel'].dropna()
    replacements = replacements[replacements != "ETS"]

    # Expand 'All' rows
    df = expand_all(df, 'Fuel', replacements)

    return df


def process_all_technology(df, unique_values_concatenated):
    
    # Check if 'Technology' column exists
    if 'Technology' not in df.columns:
        return df

    # Define replacement technologies
    replacements = unique_values_concatenated['Technology'].dropna()

    # Expand 'All' rows
    df = expand_all(df, 'Technology', replacements)

    return df


def process_all_mode(df, unique_values_concatenated):
    
    # Check if 'Mode_of_operation' column exists
    if 'Mode_of_operation' not in df.columns:
        return df

    # Define replacement mode values
    replacements = unique_values_concatenated['Mode_of_operation'].dropna()

    # Expand 'All' rows
    df = expand_all(df, 'Mode_of_operation', replacements)

    # Convert Mode_of_operation to numeric and remove invalid entries
    df['Mode_of_operation'] = pd.to_numeric(df['Mode_of_operation'], errors='coerce')
    df = df.dropna(subset=['Mode_of_operation'])

    return df

def trim_after_value(df: pd.DataFrame, value_col: str = "Value") -> pd.DataFrame:
    if value_col not in df.columns:
        return df
    i = df.columns.get_loc(value_col)
    return df.iloc[:, : i + 1]

def expand_all(df: pd.DataFrame, column: str, replacements) -> pd.DataFrame:
    
    # Check if column exists
    if column not in df.columns:
        return df

    # Drop all columns that come after the "Value" column
    df_trim = trim_after_value(df, "Value")

    # Identify rows where the column originally had the value 'All'
    all_rows = df_trim[df_trim[column] == "All"]
    if all_rows.empty:
        return df

    # Define the replacement values and drop NaNs
    repl = pd.Series(replacements).dropna().unique()
    if len(repl) == 0:
        return df

    # Define columns to check for duplicates (excluding 'Value')
    columns_to_check = [c for c in df_trim.columns if c != "Value"]

    # Create a set of existing row signatures for fast duplicate detection
    existing_keys = set(
        df_trim[columns_to_check].itertuples(index=False, name=None)
    ) if columns_to_check else set()

    # Create new rows by repeating the 'All' rows with different years
    new_rows = []
    for r in all_rows.itertuples(index=False, name=None):
        row_dict = dict(zip(df_trim.columns, r))
        for v in repl:
            new_row = row_dict.copy()
            new_row[column] = v

            # Check if a similar row already exists
            if not columns_to_check:
                new_rows.append(new_row)
            else:
                key = tuple(new_row[col] for col in columns_to_check)
                if key not in existing_keys:
                    new_rows.append(new_row)
                    existing_keys.add(key)

    if not new_rows:
        return df

    new_rows_df = pd.DataFrame(new_rows)

    # Remove original rows where column == 'All'
    df_no_all = df[df[column] != "All"].copy()

    # Align new rows to original column structure
    new_rows_df = new_rows_df.reindex(columns=df_no_all.columns)

    return pd.concat([df_no_all, new_rows_df], ignore_index=True)

def set_regional_values_from_base(df, unique_values_concatenated, data_base_region):
    # Check if 'Region' column exists
    if 'Region' in df.columns:
        
        # Identify rows where 'Region' originally had the value of data_base_region
        base_rows = df[df['Region'] == data_base_region].copy()

        # Define the replacement regions
        replacement_regions = unique_values_concatenated['Region'].dropna().astype(str)

        # Drop all columns that come after the "Value" column
        df = trim_after_value(df)

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

    if 'Region' in df.columns:
    
        # Identify rows where 'Region' originally had the value 'World'
        world_rows = df[df['Region'] == 'World'].copy()

        # Define the replacement regions
        replacement_regions = unique_values_concatenated['Region'].dropna().astype(str)

        # Drop all columns that come after the "Value" column
        df = trim_after_value(df)

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

def apply_rounding_thresholds(df: pd.DataFrame, worksheet_name: str, rounding_df: pd.DataFrame | None) -> pd.DataFrame:
    if rounding_df is None or df.empty or "Value" not in df.columns:
        return df
    
    # Find rule for this parameter, otherwise fallback to default '*'
    rule_row = rounding_df[rounding_df["Parameter"] == worksheet_name]
    if rule_row.empty:
        rule_row = rounding_df[rounding_df["Parameter"] == "*"]
        if rule_row.empty:
            return df

    threshold = rule_row.iloc[0]["Threshold"]
    replace_with = rule_row.iloc[0]["Replace with"]

    # Skip if rule is incomplete
    if pd.isna(threshold) or pd.isna(replace_with):
        return df

    # Ensure Value is numeric for the comparison
    values = pd.to_numeric(df["Value"], errors="coerce")

    mask = values.abs() < float(threshold)
    df.loc[mask, "Value"] = float(replace_with)

    return df

def interpolate_missing_year_values(df, target_years):
 
    if df is None or df.empty or "Year" not in df.columns or "Value" not in df.columns:
        return df

    df = trim_after_value(df)

    # Keep original (including 'All' rows)
    df_orig = df.copy()

    # Identify 'All' rows in Year (case-insensitive)
    year_as_str = df_orig["Year"].astype(str)
    is_all_mask = year_as_str.str.strip().str.upper() == "ALL"

    # DataFrame to operate on (exclude 'All' rows)
    df_numeric = df_orig.loc[~is_all_mask].copy()

    # Convert Year and Value only in the numeric-working copy
    df_numeric["Year"] = pd.to_numeric(df_numeric["Year"], errors="coerce")
    df_numeric = df_numeric.dropna(subset=["Year"])
    if df_numeric.empty:
        # Nothing numeric to work with; return original unchanged
        return df_orig

    df_numeric["Year"] = df_numeric["Year"].astype(int)
    df_numeric["Value"] = pd.to_numeric(df_numeric["Value"], errors="coerce")

    # Prepare target years (ints)
    target_years = sorted({int(y) for y in pd.Series(target_years).dropna().astype(int)})
    if not target_years:
        return df_orig

    # Grouping columns are all except Year and Value
    group_cols = [c for c in df_numeric.columns if c not in ("Year", "Value")]

    new_rows = []

    
    # Early skip: if no target year is missing in any numeric part, skip.
    if target_years:
        if group_cols:
            total_groups = df_numeric.groupby(group_cols, dropna=False).ngroups
            present_counts = (
                df_numeric[df_numeric["Year"].isin(target_years)]
                .groupby(group_cols, dropna=False)["Year"]
                .nunique()
            )

            if (present_counts.size == total_groups) and (present_counts.min() == len(target_years)):
                return df_orig
        else:
            existing_years = set(df_numeric["Year"].dropna().astype(int).unique())
            if set(target_years).issubset(existing_years):
                return df_orig

    # Build groups
    if group_cols:
        groups = df_numeric.groupby(group_cols, dropna=False, sort=False)
    else:
        groups = [(None, df_numeric)]

    for group_key, g in groups:
        # numeric values for interpolation
        g_val_num = pd.to_numeric(g["Value"], errors="coerce")

        # need at least two known points to interpolate
        known_mask = g_val_num.notna()
        if known_mask.sum() < 2:
            continue

        known_years = g.loc[known_mask, "Year"].astype(int)
        min_y = int(known_years.min())
        max_y = int(known_years.max())

        # consider only target years inside [min_y, max_y] (no extrapolation)
        years_in_range = [y for y in target_years if min_y <= y <= max_y]
        if not years_in_range:
            continue

        # Build Year-indexed series for interpolation
        s = pd.Series(g_val_num.values, index=g["Year"].values)

        # Collapse duplicate years (take first non-null)
        if s.index.duplicated().any():
            s = s.groupby(level=0).first()

        existing_years = set(int(y) for y in s.index.tolist())
        missing_years = [y for y in years_in_range if y not in existing_years]
        if not missing_years:
            continue

        # Reindex only to union of existing_years + missing_years and interpolate
        reindex_index = sorted(existing_years.union(missing_years))
        s2 = s.reindex(reindex_index)
        s2 = s2.interpolate(method="index", limit_area="inside")

        for y in missing_years:
            v = s2.get(y, pd.NA)
            if pd.isna(v):
                continue

            # Build row dict with the group's values (if any)
            row = {}
            if group_cols:
                gk = group_key if isinstance(group_key, tuple) else (group_key,)
                row.update(dict(zip(group_cols, gk)))
            row["Year"] = int(y)
            row["Value"] = float(v)

            new_rows.append(row)

    # If we created new rows, append them to the ORIGINAL df (which still contains 'All' rows)
    if new_rows:
        df_new = pd.concat([df_orig, pd.DataFrame(new_rows)], ignore_index=True)
        return df_new

    return df_orig