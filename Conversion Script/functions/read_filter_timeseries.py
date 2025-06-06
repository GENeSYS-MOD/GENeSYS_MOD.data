import os
import pandas as pd

def read_filter_timeseries(timeseries_dir, unique_values_concatenated, scenario_option, debugging_output):
    filtered_data = {}
    overwritten_data_info = []

    unique_regions = unique_values_concatenated['Region'].unique()

    for subdir in os.listdir(timeseries_dir):
        
        subdir_path = os.path.join(timeseries_dir, subdir)
        if os.path.isdir(subdir_path):
            csv_file = next((f for f in os.listdir(subdir_path) if f.endswith('.csv')), None)
            if csv_file:
                csv_path = os.path.join(subdir_path, csv_file)

                if debugging_output == True:
                    print("File being processed:" + csv_path)

                # Assuming the headers are in the second row (index 1)
                df = pd.read_csv(csv_path, header=1)

                scenario_subdir_path = os.path.join(subdir_path, scenario_option)
                if os.path.exists(scenario_subdir_path) and os.path.isdir(scenario_subdir_path):
                    scenario_csv_file = next((f for f in os.listdir(scenario_subdir_path) if f.endswith('.csv')), None)
                    if scenario_csv_file:
                        scenario_csv_path = os.path.join(scenario_subdir_path, scenario_csv_file)
                        df_scenario = pd.read_csv(scenario_csv_path, header=1)

                        # Identify common columns excluding 'Value'
                        common_cols = [col for col in df.columns if col in df_scenario.columns and col != 'Value']

                        # Merge on column 'HOUR'
                        df = df.merge(df_scenario, on='HOUR', how='left', suffixes=('', '_updated'))
                        for col in common_cols:
                            if col != 'HOUR':
                                col_updated = col+'_updated'
                                df[col] = df[col_updated].combine_first(df[col])
                                df.drop(col_updated, axis=1, inplace=True)
                        overwritten_data_info.append(subdir)

                        data_overwritten = True
                        
                # List of columns to include
                columns_to_include = ['HOUR'] + [region for region in unique_regions if region in df.columns]
                
                # Create the filtered DataFrame
                df_filtered = df[columns_to_include].copy()
                    
                filtered_data[subdir] = df_filtered

    return filtered_data, "\n".join(overwritten_data_info)
