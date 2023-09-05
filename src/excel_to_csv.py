'''
The scritp is to read the excel workbook, and save each sheet in 
the workbook as csv to a folder.
'''

import pandas as pd
from sheet_names import sheet_no_mod

class DataRaw:

    def __init__(self, filepath, outputpath):
        self.filepath = filepath
        self.outputpath = outputpath
        self.name = None
        self.dic_sheets = {}
        self.df = pd.DataFrame
        self.process_excel()
    
    """
    @parameters: filepath
    :outputpath
    """
    def process_excel(self):

            """
            Iterate through Excel sheets and make dictionary
            """
            for sheet in sheet_no_mod:
                self.name = sheet
                print(self.name)
               
                df_first = pd.read_excel(self.filepath,
                                        sheet_name=sheet,
                                        engine='openpyxl', header=None)

                r = 5
                df_final = df_first.iloc[:r] #shweta
                df_final = df_final.apply(lambda x: x.apply(lambda y: str(y).replace('.0', '')))
                df_raw = df_first.iloc[r:]
                df_raw = self.remove_blank_rows(df_raw)
                df_raw = df_raw.apply(lambda x: x.apply(lambda y: str(y).replace('.', ',')))
                df = pd.concat([df_final, df_raw], axis=0)
                df.replace('nan', '', inplace=True) # remove 'nan' with nothing
                df.to_csv((self.outputpath + f'{self.name}.csv'), sep=';', index=False, header=False)

                
    def remove_blank_rows(self, df):
        """
        :param df pandas dataframe from excel sheet
        :return: dataframe with removed nan values
        """
        # remove blank rows
        try:
            df = df.loc[0:df[df.isnull().all(axis=1) == True].index.tolist()[0] - 1]
        except IndexError:
            pass

        return df
