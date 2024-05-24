import pandas as pd

def read_excel(file_path):
    with pd.ExcelFile(file_path) as xls:
        data = {sheet_name: pd.read_excel(xls, sheet_name) for sheet_name in xls.sheet_names if sheet_name != 'Sets'}
        sets_data = pd.read_excel(xls, sheet_name='Sets', header=None)
    return data, sets_data
