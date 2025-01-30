import pandas as pd
import os
from read_csv_from_directory import process_files

# This function is to process files that require changes (disaggregate existing region) but not trade files
def process_changed_files(config, main_folder, output_path):
    changed_files = config['parameters']['changed_files'] # list of file with parameters
    
    #Load each CSV file from the main folder
    for df, file_path in process_files(main_folder):
        #combined_new_regions = pd.DataFrame()
        param_name = os.path.splitext(os.path.basename(file_path))[0]
        # Construct the full file path
        file_path = os.path.join(output_path, f'{param_name}.csv')
        for file in changed_files:
            if param_name == file['file_name']:
                method = file['method']
                index_count = file['index_count']
                regions_to_split = file['regions_to_split']
                new_regions = file['new_regions']
                split_ratio = file['split_ratio']
                print(param_name, method, index_count, regions_to_split, new_regions, split_ratio)
                
                df.set_index(df.columns[:index_count].tolist(), inplace=True)
                
                # Process regions to split
                for region in regions_to_split:
                    if region in df.index.get_level_values('Region'):
                        print("True")
                        # Filter rows for the region to split
                        region_data = df.loc[region]
                        # Create new DataFrame for the split regions
                        new_region_dfs = []
                        for new_region, ratio in split_ratio.items():
                            if index_count == 1:
                                new_data = region_data.to_frame().T if isinstance(region_data, pd.Series) else region_data.copy()
                                new_data['Value'] *= ratio
                                new_data['Region'] = new_region
                                new_data.reset_index(inplace=True, drop=True)
                                new_region_dfs.append(new_data)
                            else:
                                new_data = region_data.copy()
                                new_data['Value'] *= ratio
                                new_data['Region'] = new_region
                                new_data.reset_index(inplace=True) 
                                new_region_dfs.append(new_data) 
                        combined_new_regions = pd.concat(new_region_dfs, ignore_index=True)
                        # Add the new regions back to the original DataFrame
                        df.reset_index(inplace=True)  # Temporarily reset the index
                        df = pd.concat([df, combined_new_regions], ignore_index=True)

                        # Reapply multi-index  
                        df.set_index(df.columns[:index_count].tolist(), inplace=True)

                        # Save the DataFrame to the constructed path
                        df.to_csv(file_path)   

                    else:
                        print("do not have region in dataset")
                        df.to_csv(file_path)    

                        combined_new_regions = pd.concat(new_region_dfs, ignore_index=True)  
                        df.to_csv(file_path) 