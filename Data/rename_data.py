import os
import pandas as pd

# Define paths using the parent directory
data_folder_path = './Parameters/'
rename_mapping_path = './mapping_names.csv'

# Define the mapping of old technology names to new technology names from csv file
rename_mapping = pd.read_csv(rename_mapping_path, index_col=0, header=0).squeeze("columns").to_dict()

# Function to rename technologies in CSV files in the data folder
def rename_technologies(data_folder_path, rename_mapping):
    # List all items in the data folder
    items = os.listdir(data_folder_path)

    for item in items:
        item_path = os.path.join(data_folder_path, item)

        # Skip the 'Sets' folder
        if item == 'Sets':
            continue

        # Check if the item is a directory (parameter folder)
        if os.path.isdir(item_path):
            # List all CSV files in the parameter folder
            csv_files = [f for f in os.listdir(item_path) if f.endswith('.csv')]

            for csv_file in csv_files:
                csv_path = os.path.join(item_path, csv_file)

                # Read the CSV file
                df = pd.read_csv(csv_path)

                # Strip whitespace from column names
                df.columns = df.columns.str.strip()


                # Replace old technology names with new ones using the mapping in all columns
                for col in df.columns:
                    if df[col].dtype == 'object':  # Only apply to string columns
                        df[col] = df[col].str.strip().replace(rename_mapping)

                # Identify 'Unnamed' columns and rename them to empty string
                df.columns = [col if not col.startswith('Unnamed') else '' for col in df.columns]

                # Save the renamed CSV file with a '_renamed' suffix
                csv_path = os.path.join(item_path, csv_file)
                df.to_csv(csv_path, index=False)
                print(f"Renamed and saved: {csv_path}")



# Call the function to rename technologies in the CSV files in the data folder
rename_technologies(data_folder_path, rename_mapping)

print("CSV file renaming complete.")
