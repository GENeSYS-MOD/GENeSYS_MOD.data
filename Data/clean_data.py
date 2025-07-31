import os
import pandas as pd

# Define paths
data_folder_path = './Parameters/'
reference_excel_path = '../Conversion Script/Set_filter_file.xlsx'
technology_sheet_name = 'Technology_selection'

# Read the reference technology list from the Excel file and strip whitespace
reference_df = pd.read_excel(reference_excel_path, sheet_name=technology_sheet_name)
reference_df['Technology'] = reference_df['Technology'].str.strip()
valid_technologies = set(reference_df['Technology'].dropna().unique())

# Create a set for case-insensitive comparison and a mapping dictionary for original forms
valid_technologies_set = set(tech.lower() for tech in valid_technologies)
original_technology_map = {tech.lower(): tech for tech in valid_technologies}

# Initialize a set to collect removed technology names
removed_technologies = set()

# Function to clean CSV files in the data folder
def clean_csv_files(data_folder_path, valid_technologies_set, original_technology_map):
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

                # Identify 'Unnamed' columns and rename them to empty string
                df.columns = [col if not col.startswith('Unnamed') else '' for col in df.columns]

                # Check if the 'Technology' column exists
                if 'Technology' in df.columns:

                    # Convert the 'Technology' column to lowercase for comparison
                    df['Technology_lower'] = df['Technology'].str.lower()

                    # Find the technologies to be removed
                    to_remove = df[~df['Technology_lower'].isin(valid_technologies_set)]['Technology']
                    removed_technologies.update(to_remove)

                    # Save the removed technologies to a file
                    with open('removed_technologies.txt', 'w') as f:
                        for tech in map(str, removed_technologies):
                            f.write(f"{tech}\n")

                    # Filter rows with valid technologies and map back to original form
                    cleaned_df = df[df['Technology_lower'].isin(valid_technologies_set)].copy()
                    cleaned_df['Technology'] = cleaned_df['Technology_lower'].map(original_technology_map)
                    cleaned_df = cleaned_df.drop(columns=['Technology_lower'])

                    # Save the cleaned CSV file with a '_clean' suffix
                    clean_csv_path = os.path.join(item_path, csv_file)
                    cleaned_df.to_csv(clean_csv_path, index=False)
                    print(f"Cleaned and saved: {clean_csv_path}")



# Call the function to clean the CSV files in the data folder
clean_csv_files(data_folder_path, valid_technologies_set, original_technology_map)

print("CSV file cleaning complete.")