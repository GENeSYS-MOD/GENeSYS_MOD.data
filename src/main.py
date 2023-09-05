'''
The script is defining parameter
'''

from excel_to_csv import DataRaw

FILENAME = "/Users/shwetat/Projects/Ocean_grid/Inputdata/NO_disagg_GradualDevelopment_oE_v492.xlsx"

FILE_EXTENSION = "csv"

PATH_TO_CSV = "/Users/shwetat/Projects/Ocean_grid/Havnett_repo/csvs/"

DataRaw(filepath=FILENAME, outputpath = PATH_TO_CSV)