import pandas as pd

def read_excel(file_path):
    return pd.read_excel(file_path, sheet_name=None)
