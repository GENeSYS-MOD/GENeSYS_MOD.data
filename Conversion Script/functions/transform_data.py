import pandas as pd

def transform_wide_to_long(df, id_vars, value_vars):
    long_df = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name='Year', value_name='Value')
    return long_df
