import pandas as pd

def transform_wide_to_long(df, id_vars, value_vars, var_name='Region2'):
    if value_vars:
        # If value_vars exist, perform the melt operation
        long_df = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name=var_name, value_name='Value')

        # Debugging: Print the columns of the melted DataFrame
        print("Columns after melting:", long_df.columns)

        # Reorder columns to place 'Region2' immediately after 'Region'
        if 'Region' in long_df.columns and var_name in long_df.columns:
            cols = list(long_df.columns)
            region_idx = cols.index('Region')
            cols.insert(region_idx + 1, cols.pop(cols.index(var_name)))
            long_df = long_df[cols]

        return long_df
    else:
        # If no value_vars are present, return the DataFrame as is
        return df
