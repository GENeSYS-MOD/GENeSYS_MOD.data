import yaml
from data.aggregate import DataRaw
from data.combine_data import get_file_list, combine_xlsx
#import data.read_config as conf

FILENAME = "/Users/shwetat/Projects/Ocean_grid/Havnett_repo/csvs/Data_Europe_GradualDevelopment_NNS0_vtest.xlsx"
OLD_MARKET_AREA = ['SE1', 'SE2']
NEW_MARKET_AREA = 'SE_NEW'

# TO COMBINE FILES
PATH_TO_CSV = "/Users/shwetat/Projects/Ocean_grid/Havnett_repo/csvs/"
FILE_EXTENSION = "csv"
COMBINE_FILE_NAME = "Data_Europe_GradualDevelopment_NNS0_vtest_agg.xlsx"
COLUMNS_TO_DROP = []
#PATH_TO_YAML = "Users/shwetat/Projects/Ocean_grid/Havnett_repo/Data_Processing_GENeSYS-MOD/Disaggregation/disaggregation_GENeSYS_MOD/config.yaml"

def read_yaml():
    with open("/Users/shwetat/Projects/Ocean_grid/Havnett_repo/Data_Processing_GENeSYS-MOD/Disaggregation/disaggregation_GENeSYS_MOD/config_combine.yaml", 'r') as config:
        return yaml.safe_load(config)



def run_aggregate():

    configs = read_yaml()

    DataRaw(filepath=FILENAME,
                  outputpath = PATH_TO_CSV,
                  new_market_area=NEW_MARKET_AREA,
                  old_market_area=OLD_MARKET_AREA,
                  config=configs)
  
def run_combine():    
    all_filenames = get_file_list(path_to_csvs=PATH_TO_CSV,
                                  file_extension=FILE_EXTENSION)
    combine_xlsx(path_to_csvs=PATH_TO_CSV,
                  all_filenames=all_filenames,
                  output_file=COMBINE_FILE_NAME)
    
if __name__ == "__main__":
    run_aggregate()
    run_combine()
    