import os
import pandas as pd

def read_filter_timeseries(timeseries_dir, unique_values_concatenated, scenario_option):
    filtered_data = {}
    overwritten_data_info = []

    unique_regions = unique_values_concatenated['Region'].unique()

    for subdir in os.listdir(timeseries_dir):
        subdir_path = os.path.join(timeseries_dir, subdir)
        if os.path.isdir(subdir_path):
            csv_file = next((f for f in os.listdir(subdir_path) if f.endswith('.csv')), None)
            if csv_file:
                csv_path = os.path.join(subdir_path, csv_file)
                # Assuming the headers are in the second row (index 1)
                df = pd.read_csv(csv_path, header=1)

                scenario_subdir_path = os.path.join(subdir_path, scenario_option)
                if os.path.exists(scenario_subdir_path) and os.path.isdir(scenario_subdir_path):
                    scenario_csv_file = next((f for f in os.listdir(scenario_subdir_path) if f.endswith('.csv')), None)
                    if scenario_csv_file:
                        scenario_csv_path = os.path.join(scenario_subdir_path, scenario_csv_file)
                        df_scenario = pd.read_csv(scenario_csv_path, header=1)

                        for region in unique_regions:
                            if region in df.columns and region in df_scenario.columns:
                                df[region] = df_scenario[region]
                                if subdir not in overwritten_data_info:
                                    overwritten_data_info.append(subdir)

                filtered_data[subdir] = df

    return filtered_data, "\n".join(overwritten_data_info)
