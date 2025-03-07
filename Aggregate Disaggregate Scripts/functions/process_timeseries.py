import os
import pandas as pd 
from read_csv_from_directory import process_files

def timeseries_files(config, main_folder, output_path):
    ts_files = config['parameters']['time_series_files'] 
    for df, file_path in process_files(main_folder):
        df.columns = df.iloc[0]
        df = df[1:]
        param_name = os.path.splitext(os.path.basename(file_path))[0]
        file_path = os.path.join(output_path, f'{param_name}.csv')
        for file in ts_files:
            if param_name == file['file_name']: 
                regions_to_split = file['regions_to_split']
                new_regions = file['new_regions']
                split_ratio = file['split_ratio']
                print(param_name, regions_to_split, new_regions, split_ratio)
                
                for region in new_regions:
                    df[region] = df[regions_to_split].sum(axis=1) * split_ratio[region]
            df.to_csv(file_path)