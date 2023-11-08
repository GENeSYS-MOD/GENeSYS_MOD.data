import pandas as pd
from data.sheet_names import sheet_mod, sheet_no_mod
from disaggregation import DataRaw, Trade
import math


pd.options.mode.chained_assignment = None


'''class Aggregate(DataRaw):
    def call_method(self, df, df_final):
       """
       Calls function according to config.yaml
       :return dataframe to write in csv format
       """
       
       # Trade sheets are processed differently
       if 'Trade' in self.name:
           df_raw = Trade(df=df, name=self.name, new_market_area=self.new_market_area,
                          old_market_area=self.old_market_area, config=self.config)
           if self.name in ['Par_TradeRoute', 'Par_TradeCosts']:
               self.df = df_raw.insert_row_col_sum()
               self.df = self.df.apply(lambda x: x.apply(lambda y: str(y).replace('.', ',')))
           
           elif self.name == 'Par_TradeCapacityGrowthCosts':
               self.df = df_raw.insert_row_col_copy(level=1)
               self.df = self.df.apply(lambda x: x.apply(lambda y: str(y).replace('.', ',')))
               
           elif self.name == 'Par_GrowthRateTradeCapacity':
               self.df = df_raw.insert_row_col_copy(level=2)
               self.df = self.df.apply(lambda x: x.apply(lambda y: str(y).replace('.', ',')))
           
       else:

           self.df = df
       
           # insert rows based on old market area
       
           m = self.new_market_area
           self.sum_(m)
       
       self.df = self.df.apply(lambda x: x.apply(lambda y: str(y).replace('.', ',')))       
       self.write_csv(df_final)
   
       return self.df    
   
    def sum_(self, m):
        """
        Inserts rows based on old market area
        """
        # insert with one index
         
        if len(self.config[self.name]['Index']) == 1:
            temp_final = [0]
            for area in self.old_market_area: 
                temp = self.df.loc[area].values.flatten()
                temp_final+=temp
            self.df.loc[m] = temp_final

        # insert with multiindex
        else:
            df_temp = pd.DataFrame()
            for area in self.old_market_area:
                temp = self.df[self.df.index.isin([area], level=0)]
                df_temp = pd.concat([df_temp,temp])
            df_temp = df_temp.sum(level=1) # sum at level 1 of multi-index
            df_temp = df_temp.reset_index()
            df_temp.insert(0, '', m) # Insert a column to assign name to a new region, may be changes in future
            self.df = self.df.reset_index() # reset multindex so that appending the dataframes don't cause any issue
            column_names = self.df.columns.tolist()
            df_temp.rename(columns=dict(zip(df_temp.columns, column_names)), inplace=True)
            
            self.df = pd.concat([self.df, df_temp],axis=0, ignore_index=True)
            self.df = self.df.reset_index(drop=True)
            #print(self.df.head())
        return self.df

class aggregateTrade(Trade):
         
    def __init__(self, df, name, new_market_area, old_market_area, config):
        self.name = name
        self.new_market_area = new_market_area
        self.old_market_area = old_market_area
        self.config = config
        self.route_df = pd.DataFrame
        self.df = df
        
    def insert_row_col_sum(self):
        """
        Inserts rows based on old market area
        """
        m = self.new_market_area
        # insert new col
        temp_df = pd.DataFrame()
        for area in self.old_market_area:
            temp_df[area] = self.df[area]
            
        temp_df[m] = temp_df.sum(axis=1)
        temp_df = temp_df[[m]]
        
        self.df.insert(loc=len(self.df.columns), column=m, value=temp_df.values)
        
        # insert row with multiindex
       
        print('multiindex is True')
        df_temp = pd.DataFrame()
        for area in self.old_market_area:
                
            temp = self.df[self.df.index.isin([area], level=1)]
                
            df_temp = pd.concat([df_temp,temp],axis=0, ignore_index=True)
        
                
        #df_temp = df_temp.sum(level=1) # sum at level 1 of multi-index
        df_temp = df_temp.groupby(level=0, axis=0).sum()
        df_temp = df_temp.reset_index()
            
        df_temp.insert(1, '', m) # Insert a column to assign name to a new region, may be changes in future
        self.df = self.df.reset_index() # reset multindex so that appending the dataframes don't cause any issue
        column_names = self.df.columns.tolist()
        df_temp.rename(columns=dict(zip(df_temp.columns, column_names)), inplace=True)
        
        self.df = pd.concat([self.df, df_temp],axis=0, ignore_index=True)
        self.df = self.df.reset_index(drop=True)

        return self.df
    
    def insert_row_col_copy(self, level):
        """
        Inserts rows based on old market area
        """
        m = self.new_market_area
        # insert with one index
        for area in self.old_market_area:
            # insert with multiindex
            self.df.insert(loc=len(self.df.columns), column=m, value=self.df[area].values) # insert column
            df_temp = self.df[self.df.index.isin([area], level=level)] # insert row
            df_temp.rename({area: m}, inplace=True, level=level)
            self.df = pd.concat([self.df, df_temp],axis=0, ignore_index=True)
            self.df = self.df.reset_index(drop=True)
            break
        return self.df'''
    
class DataRaw:

    def __init__(self, filepath, outputpath, new_market_area, old_market_area, config):
        self.filepath = filepath
        self.outputpath = outputpath
        self.new_market_area = new_market_area
        self.old_market_area = old_market_area
        self.config = config
        self.name = None
        self.dic_sheets = {}
        self.df = pd.DataFrame
        self.process_excel()

    
    # apply the function to all cells in the DataFrame
    #df = df.applymap(replace_decimal)

    def process_excel(self):

        """
        Iterate through Excel sheets and make dictionary
        """
        
        for sheet in sheet_no_mod:
            self.name = sheet
            print(self.name)
            # df = pd.read_excel(self.filepath,
            #                         sheet_name=sheet,
            #                         engine='openpyxl')
            # df.to_csv(self.outputpath + f'{self.name}.csv', sep=';', index=False, header=True)
            
            # Need to remove later
            df_first = pd.read_excel(self.filepath,
                                    sheet_name=sheet,
                                    engine='openpyxl', header=None)
            
            r = 5
            df_final = df_first.iloc[:r] #shweta
            df_final = df_final.apply(lambda x: x.apply(lambda y: str(y).replace('.0', '')))
            df_raw = df_first.iloc[r:]
            df_raw = df_raw.apply(lambda x: x.apply(lambda y: str(y).replace('.', ',')))
            df = pd.concat([df_final, df_raw], axis=0)
            
            df.to_csv((self.outputpath + f'{self.name}.csv'), sep=';', index=False, header=False)
        
        for sheet in sheet_mod:
            self.name = sheet
            print(self.name)
            # TODO flaw in input data, Par_ModelPeriodActivityMaxLimit starts with row 4
            r = 3 if sheet == "Par_ModelPeriodActivityMaxLimit" else 4
            
            df_first = pd.read_excel(self.filepath,
                                   sheet_name=sheet,
                                   engine='openpyxl', header=None)
            
            
            df_raw = pd.read_excel(self.filepath,
                                   sheet_name=sheet,
                                   skiprows=r,#shweta
                                   engine='openpyxl', decimal=",")
            
            df_final = df_first.iloc[:r, :1] #shweta
  
            # delete empty cols and rows
            df = self.remove_blank_rows(df_raw)

            # set one or multidimensional index
            df.set_index(self.set_multiindex(df=df), inplace=True)
            
            
            # store in dict
            self.dic_sheets[self.name] = self.call_method(df, df_final) #shweta

        return self.dic_sheets

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

    def set_multiindex(self, df):
        """
        :param df: dataframe/Users/shwetat/Projects/Ocean_grid/Havnett_repo/Data_Processing_GENeSYS-MOD/Preprocessing/preprocess_GradualDevelopmentSheets.ipynb
        :return index for dataframe multiindex or index
        :type df: dataframe
        """
        return list(df.columns[self.config[self.name]['Index']])

    def call_method(self, df, df_final):

        """
        Calls function according to config.yaml
        :return dataframe to write in csv format
        """
        
        # Trade sheets are processed differently
        if 'Trade' in self.name:
            df_raw = Trade(df=df, name=self.name, new_market_area=self.new_market_area,
                           old_market_area=self.old_market_area, config=self.config)
            if self.name in ['Par_TradeRoute', 'Par_TradeCosts']:
                self.df = df_raw.insert_row_col_sum()
                self.df = self.df.apply(lambda x: x.apply(lambda y: str(y).replace('.', ',')))
            
            elif self.name == 'Par_TradeCapacityGrowthCosts':
                self.df = df_raw.insert_row_col_copy(level=1)
                self.df = self.df.apply(lambda x: x.apply(lambda y: str(y).replace('.', ',')))
                
            elif self.name == 'Par_GrowthRateTradeCapacity':
                self.df = df_raw.insert_row_col_copy(level=2)
                self.df = self.df.apply(lambda x: x.apply(lambda y: str(y).replace('.', ',')))
            
        else:

            self.df = df
        
            # insert rows based on old market area
        
            m = self.new_market_area
            self.sum_(m)
        
        self.df = self.df.apply(lambda x: x.apply(lambda y: str(y).replace('.', ',')))       
        self.write_csv(df_final)
    
        return self.df
    
    def sum_(self, m):
        """
        Inserts rows based on old market area
        """
        # insert with one index
         
        if len(self.config[self.name]['Index']) == 1:
            temp_final = [0]
            for area in self.old_market_area: 
                temp = self.df.loc[area].values.flatten()
                temp_final+=temp
            self.df.loc[m] = temp_final

        # insert with multiindex
        else:
            df_temp = pd.DataFrame()
            for area in self.old_market_area:
                temp = self.df[self.df.index.isin([area], level=0)]
                df_temp = pd.concat([df_temp,temp])
            df_temp = df_temp.sum(level=1) # sum at level 1 of multi-index
            df_temp = df_temp.reset_index()
            df_temp.insert(0, '', m) # Insert a column to assign name to a new region, may be changes in future
            self.df = self.df.reset_index() # reset multindex so that appending the dataframes don't cause any issue
            column_names = self.df.columns.tolist()
            df_temp.rename(columns=dict(zip(df_temp.columns, column_names)), inplace=True)
            
            self.df = pd.concat([self.df, df_temp],axis=0, ignore_index=True)
            self.df = self.df.reset_index(drop=True)
            #print(self.df.head())
        return self.df

    

    def write_csv(self, df_final):
        """Write sheet of dataframe to csv and remove unnamed cols"""

        # remove unnamed cols
        self.df.columns = self.df.columns.astype(str)
        #self.df = self.df.loc[:, ~self.df.columns.str.contains('Unnamed', na=False)]
        self.df = self.df.reset_index()#(level=[0,1])
        
        df_temp = self.df.transpose()
        df_temp = df_temp.reset_index()
        df_temp = df_temp.transpose()
        #if 'index' in df_temp.columns:
            #df_temp = df_temp.drop(columns=['index'])
        self.df = pd.concat([df_final, df_temp], axis=0, ignore_index=True)
        #self.df = self.df.apply(lambda x: x.replace('.',','))
        return self.df.to_csv(path_or_buf=(self.outputpath + f'{self.name}.csv'), sep=';', index=False, header=False, decimal=',')
    
    
class Trade:

    def __init__(self, df, name, new_market_area, old_market_area, config):
        self.name = name
        self.new_market_area = new_market_area
        self.old_market_area = old_market_area
        self.config = config
        self.route_df = pd.DataFrame
        self.df = df
        #self.insert_row_col()
        
    def insert_row_col_sum(self):
        """
        Inserts rows based on old market area
        """
        m = self.new_market_area
        # insert new col
        temp_df = pd.DataFrame()
        for area in self.old_market_area:
            temp_df[area] = self.df[area]
            
        temp_df[m] = temp_df.sum(axis=1)
        temp_df = temp_df[[m]]
        
        self.df.insert(loc=len(self.df.columns), column=m, value=temp_df.values)
        
        # insert row with multiindex
       
        print('multiindex is True')
        df_temp = pd.DataFrame()
        for area in self.old_market_area:
                
            temp = self.df[self.df.index.isin([area], level=1)]
                
            df_temp = pd.concat([df_temp,temp],axis=0, ignore_index=True)
        
                
        #df_temp = df_temp.sum(level=1) # sum at level 1 of multi-index
        df_temp = df_temp.groupby(level=0, axis=0).sum()
        df_temp = df_temp.reset_index()
            
        df_temp.insert(1, '', m) # Insert a column to assign name to a new region, may be changes in future
        self.df = self.df.reset_index() # reset multindex so that appending the dataframes don't cause any issue
        column_names = self.df.columns.tolist()
        df_temp.rename(columns=dict(zip(df_temp.columns, column_names)), inplace=True)
        
        self.df = pd.concat([self.df, df_temp],axis=0, ignore_index=True)
        self.df = self.df.reset_index(drop=True)

        return self.df
    
    def insert_row_col_copy(self, level):
        """
        Inserts rows based on old market area
        """
        m = self.new_market_area
        # insert with one index
        for area in self.old_market_area:
            # insert with multiindex
            self.df.insert(loc=len(self.df.columns), column=m, value=self.df[area].values) # insert column
            df_temp = self.df[self.df.index.isin([area], level=level)] # insert row
            df_temp.rename({area: m}, inplace=True, level=level)
            self.df = pd.concat([self.df, df_temp],axis=0, ignore_index=True)
            self.df = self.df.reset_index(drop=True)
            break
        return self.df