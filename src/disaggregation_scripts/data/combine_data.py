import os
import pandas as pd

# Functions to combine csvs into 1 xlsx file
def get_file_list(path_to_csvs, file_extension):
    """
    Calls function to get list of all csv files
    :para path_to_csv: path to csv folder
    :para file_extension: csv in this case
    :return list of csv file names
    """
    filenames = []
    for file in os.listdir(path_to_csvs):
        if file.endswith(file_extension):
            filenames.append(file)
    return filenames
    
def combine_xlsx(path_to_csvs, all_filenames, output_file):  
    """
    Calls function to combine csv files
    :para path_to_csv: path to csv folder
    :para all_filenames: list of csv files in the folder
    :para output_file: name and extension of output file
    :return list of csv file names
    """
    print(path_to_csvs)
    writer = pd.ExcelWriter(path_to_csvs + output_file) 
    for csvfilename in all_filenames: 
        print("Loading "+ csvfilename)
        df = pd.read_csv(path_to_csvs + csvfilename, sep=';', encoding='utf-8')
        # df_final =  df1.iloc[:4, :1]
        # df_t = df1[4:]
        # df_t = df_t.apply(lambda x: x.apply(lambda y: str(y).replace('.', ',')))
        # df = pd.concat([df_final, df_t], axis=0)
        for j in range(len(df.columns)):
            if j == 0:
                print('do nothing')
            else:
                old = df.columns[j]
                new = ''
                df = df.rename(columns = {old:new})
        df.to_excel(writer, sheet_name=csvfilename[:-4], index=False, header=True)
        
        print("done")
        #break
    writer.save()
    print("task completed")