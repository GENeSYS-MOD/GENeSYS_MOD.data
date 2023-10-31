import yaml
#from data.aggregate import DataRaw, Trade
from data.disaggregation import DataRaw, Trade
from data.combine_data import get_file_list, combine_xlsx
#import data.read_config as conf


FILENAME = "/Users/shwetat/Projects/Ocean_grid/Inputdata/NO_disagg_GradualDevelopment_oE_v492.xlsx"
NAME_MARKET_AREAS = ['SE1', 'SE2']
OLD_MARKET_AREA = ['SE']

# TO COMBINE FILES
PATH_TO_CSV = "/Users/shwetat/Projects/Ocean_grid/Havnett_repo/csvs/"
FILE_EXTENSION = "csv"
COMBINE_FILE_NAME = "Data_Europe_GradualDevelopment_NNS0_vtest.xlsx"
COLUMNS_TO_DROP = []
#PATH_TO_YAML = "Users/shwetat/Projects/Ocean_grid/Havnett_repo/Data_Processing_GENeSYS-MOD/Disaggregation/disaggregation_GENeSYS_MOD/config.yaml"

def read_yaml():
    with open("/Users/shwetat/Projects/Ocean_grid/Havnett_repo/Data_Processing_GENeSYS-MOD/Disaggregation/disaggregation_GENeSYS_MOD/config.yaml", 'r') as config:
        return yaml.safe_load(config)



def run_disaggregation():

    configs = read_yaml()

    df = DataRaw(filepath=FILENAME,
                  outputpath = PATH_TO_CSV,
                  new_market_area=NAME_MARKET_AREAS,
                  old_market_area=OLD_MARKET_AREA,
                  config=configs)
  
def run_combine():    
    all_filenames = get_file_list(path_to_csvs=PATH_TO_CSV,
                                  file_extension=FILE_EXTENSION)
    combine_xlsx(path_to_csvs=PATH_TO_CSV,
                  all_filenames=all_filenames,
                  output_file=COMBINE_FILE_NAME)
    
if __name__ == "__main__":
    run_disaggregation()
    #run_combine()
    
'''

FILENAME = "/Users/shwetat/Projects/Ocean_grid/Havnett_repo/csvs/Data_Europe_GradualDevelopment_NNS0_vtest.xlsx"
NAME_MARKET_AREA = 'SE_NEW'
OLD_MARKET_AREAS = ['SE1', 'SE2']

# TO COMBINE FILES
PATH_TO_CSV = "/Users/shwetat/Projects/Ocean_grid/Havnett_repo/csvs/"
FILE_EXTENSION = "csv"
COMBINE_FILE_NAME = "Data_Europe_GradualDevelopment_NNS0_vtest_aggregate.xlsx"
COLUMNS_TO_DROP = []


def read_yaml():
    with open("/Users/shwetat/Projects/Ocean_grid/Havnett_repo/Data_Processing_GENeSYS-MOD/Disaggregation/disaggregation_GENeSYS_MOD/config_combine.yaml", 'r') as config:
        return yaml.safe_load(config)
        

def run_disaggregation():

    configs = read_yaml()
    #print(configs)
    df = DataRaw(filepath=FILENAME,
                 outputpath = PATH_TO_CSV,
                 new_market_area=NAME_MARKET_AREA,
                 old_market_area=OLD_MARKET_AREAS,
                 config=configs)

def run_combine():    
    all_filenames = get_file_list(path_to_csvs=PATH_TO_CSV,
                                  file_extension=FILE_EXTENSION)
    combine_xlsx(path_to_csvs=PATH_TO_CSV,
                  all_filenames=all_filenames,
                  output_file=COMBINE_FILE_NAME)

if __name__ == "__main__":
    run_disaggregation()
    run_combine()'''
