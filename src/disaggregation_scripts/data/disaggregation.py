import pandas as pd
from data.sheet_names import sheet_mod, sheet_no_mod
import math


pd.options.mode.chained_assignment = None


pd.options.mode.chained_assignment = None


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
            if self.name == 'Par_TradeRoute':
                self.df = df_raw.trade_route()
                self.df = self.df.apply(lambda x: x.apply(lambda y: str(y).replace('.', ',')))
            elif self.name == 'Par_TradeCosts':
                self.df_route = df_raw.trade_route()
                self.df = df_raw.trade_costs(df_route=self.df_route)
                self.df = self.df.apply(lambda x: x.apply(lambda y: str(y).replace('.', ',')))
            elif self.name == 'Par_TradeCapacity':
                self.df = df_raw.trade_capacity()
                self.df = self.df.apply(lambda x: x.apply(lambda y: str(y).replace('.', ',')))
            elif self.name in ['Par_TradeCapacityGrowthCosts', 'Par_GrowthRateTradeCapacity']:
                self.df = df_raw.df
                self.df = self.df.apply(lambda x: x.apply(lambda y: str(y).replace('.', ',')))

        else:
            self.df = df

            for m in self.new_market_area:
                # insert rows based on old market area
                self.copy_rows(m)

                if self.config[self.name]['Method'] == 'divide':
                    self.divide(m)

                elif self.config[self.name]['Method'] == 'insert':
                    self.insert(m)

        self.df = self.df.apply(lambda x: x.apply(lambda y: str(y).replace('.', ',')))       
        self.write_csv(df_final)

        return self.df

    def copy_rows(self, m):
        """
        Inserts rows based on old market area
        """
        # insert with one index
        if len(self.config[self.name]['Index']) == 1:
            self.df.loc[m] = self.df.loc[self.old_market_area].values.flatten().tolist()
            

        # insert with multiindex
        else:
            df_temp = self.df[self.df.index.isin([self.old_market_area], level=0)]
            df_temp.rename({self.old_market_area: m}, inplace=True, level=0)
            self.df = pd.concat([self.df, df_temp])

        return self.df

    def insert(self, m):
        if len(self.config[self.name]['Index']) == 1:
            self.df.loc[m] = self.config[self.name]['Value'][m]
            #print('insert',self.df.head())
        # TODO not sure if this works
        else:
            for f in self.config[self.name]['Value'].keys():
                self.df.loc[(m, f)] = self.df.loc[(self.old_market_area, f)]
        #print('insert',self.df.head())
        
        return self.df

    def divide(self, m):

        self.df[self.df.index.isin([m], level=0)] = self.df[self.df.index.isin([m], level=0)].multiply(self.config[self.name]['Value'][m])
        
        return self.df

    def write_csv(self, df_final):
        """Write sheet of dataframe to csv and remove unnamed cols"""

        # remove unnamed cols
        
        
        self.df.columns = self.df.columns.astype(str)
        self.df = self.df.loc[:, ~self.df.columns.str.contains('Unnamed', na=False)]
        self.df = self.df.reset_index()#(level=[0,1])
        
        df_temp = self.df.transpose()
        df_temp = df_temp.reset_index()
        df_temp = df_temp.transpose()
        self.df = pd.concat([df_final, df_temp], axis=0)
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
        self.insert_row_col()

    def insert_row_col(self):
        """
        Insert new cols and rows for new market areas with zero values
        df: dataframe
        """

        for m in self.new_market_area:
            # insert new cols
            self.df.insert(loc=len(self.df.columns), column=m, value=0)

            # insert new rows according to index i
            if len(self.config[self.name]['Index']) == 3:
                df_temp = self.df.loc[(slice(None), slice(None), self.old_market_area), :]
                df_temp.rename({self.old_market_area: m}, inplace=True, level=2)

            else:
                df_temp = self.df[self.df.index.isin([self.old_market_area], level=1)]
                df_temp.rename({self.old_market_area: m}, inplace=True, level=1)

            self.df = pd.concat([df_temp, self.df])

    def trade_route(self):

        self.df[self.df.index.isin([self.new_market_area], level=1)] = 0
        self.df.loc[('ETS', self.new_market_area), :] = 1 # need to correct, for eg. SE1-SE1 should be 0

        for k in self.config[self.name]['Value'].keys():
            node_from = k.split('-')[0]
            node_to = k.split('-')[1]
            self.df.loc[(slice(None), node_from), node_to] = self.config[self.name]['Value'][k]

        self.route_df = self.df
        return self.df

    def trade_costs(self, df_route):

        # set values for new market areas to 0
        self.df[self.df.index.isin([self.new_market_area], level=1)] = 0
        #print(self.new_market_area)

        # add row distance for market area
        df_temp = df_route[df_route.index == ('Power', self.new_market_area)]
        df_temp.rename({'Power': 'Distance'}, inplace=True)
        self.df = pd.concat([df_temp, self.df])

        for area in self.new_market_area:
            # iterate through fuels and calculate costs
            for f in self.df[self.df.index.isin([self.new_market_area], level=1)].index.get_level_values(0):
                print(f)
                distance = self.df.loc[('Power', area)].tolist()
                # TODO use apply function here
                if f in ['Hardcoal', 'Biomass']:
                    self.df.loc[(f, area)] = [((0.0014 * x + 13.97) / 1.15) * (10 ** 12) / (1000 * 29308) / 1000000 for x
                                               in distance]
                elif f == ['Oil', 'H2', 'Biofuel']:
                    self.df.loc[(f, area)] = [
                        math.exp(7.032824 + 1 * 0.622482) * ((x / 1.852) ** 0.40303) / (1.15 * 0.0059) / 1000000 for x in
                        distance]
                elif f in ['Power', 'ETS']:
                    self.df.loc[(f, area)] = [0 if x > 0 else 0.01 for x in distance]
                elif f in ['LH2', 'LSG', 'LNG', 'LBG', 'Powerfuel']:
                    self.df.loc[(f, area)] = [
                        (math.exp(7.032824 + 1 * 0.622482) * ((x / 1.852) ** 0.40303)) / (1.15 * 0.0059) / 1000000 for x in
                        distance]
                elif 'Gas' in f:
                    self.df.loc[(f, area)] = [x * 0.00003215271 for x in distance]

        return self.df

    def trade_capacity(self):

        # insert values from config for defined fuels
        for f in self.config[self.name]['Value'].keys():
            for k in self.config[self.name]['Value'][f].keys():
                node_from = k.split('-')[0]
                node_to = k.split('-')[1]
                self.df.loc[(f, node_from), node_to] = self.config[self.name]['Value'][f][k]
        return self.df



    

