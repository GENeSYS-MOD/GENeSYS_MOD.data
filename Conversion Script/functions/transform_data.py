import pandas as pd

def transform_wide_to_long(df, id_vars, value_vars, var_name='Year'):
    if value_vars:
        long_df = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name=var_name, value_name='Value')

        if var_name == 'Region2' and 'Region' in long_df.columns:
            cols = list(long_df.columns)
            region_idx = cols.index('Region')
            cols.insert(region_idx + 1, cols.pop(cols.index(var_name)))
            long_df = long_df[cols]

        return long_df
    else:
        return df

def transform_data(data, sets_data):
    valid_years = sets_data[sets_data.iloc[:, 0] == 'Year'].iloc[1:].dropna().values.flatten().tolist()
    valid_regions = sets_data[sets_data.iloc[:, 0] == 'Region'].iloc[1:].dropna().values.flatten().tolist()

    transformed_data = {}
    for sheet_name, df in data.items():
        if 'Value' in df.columns:
            transformed_data[sheet_name] = df
        else:
            id_vars = [col for col in df.columns if col not in valid_years + valid_regions]
            if any(col in valid_years for col in df.columns):
                value_vars = [col for col in df.columns if col in valid_years]
                transformed_data[sheet_name] = transform_wide_to_long(df, id_vars, value_vars, var_name='Year')
            elif any(col in valid_regions for col in df.columns):
                value_vars = [col for col in df.columns if col in valid_regions]
                transformed_data[sheet_name] = transform_wide_to_long(df, id_vars, value_vars, var_name='Region2')
            else:
                transformed_data[sheet_name] = df

    return transformed_data
