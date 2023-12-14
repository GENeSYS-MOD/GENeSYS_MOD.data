import os
import pandas as pd

def read_filter_timeseries(timeseries_dir, unique_values_concatenated):
    filtered_data = {}

    # Get the list of unique regions from unique_values_concatenated
    unique_regions = unique_values_concatenated['Region'].unique()

    # Iterate through each subdirectory in '00_Timeseries'
    for subdir in os.listdir(timeseries_dir):
        subdir_path = os.path.join(timeseries_dir, subdir)
        if os.path.isdir(subdir_path):
            # Assuming there is only one CSV file per subdirectory
            csv_file = next((f for f in os.listdir(subdir_path) if f.endswith('.csv')), None)
            if csv_file:
                csv_path = os.path.join(subdir_path, csv_file)

                # Read only the first row (excluding the first row of the file) to get the headers (regions)
                headers = pd.read_csv(csv_path, skiprows=1, nrows=0)

                # Include the first column (whatever it is) and filter the rest based on unique_regions
                columns_to_keep = [headers.columns[0]] + [col for col in headers.columns[1:] if col in unique_regions]

                # Now read the entire CSV with filtered columns, skipping the first row
                df = pd.read_csv(csv_path, skiprows=1, usecols=columns_to_keep)

                filtered_data[subdir] = df

    return filtered_data