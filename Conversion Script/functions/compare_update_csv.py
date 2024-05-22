import pandas as pd
import os
from datetime import datetime

def update_or_append_csv(existing_csv_path, new_data):
    # Convert new_data columns to uppercase
    new_data.columns = [col.capitalize() for col in new_data.columns]

    if os.path.exists(existing_csv_path):
        existing_data = pd.read_csv(existing_csv_path)
        updated_data = existing_data.copy()

        # Debugging step: Print existing and new data columns
        print(f"Existing data columns: {existing_data.columns}")
        print(f"New data columns: {new_data.columns}")

        # Ensure required columns are present in existing_data
        for col in ['Value', 'Unit', 'Source', 'Updated at', 'Updated by']:
            if col not in existing_data.columns:
                existing_data[col] = ''
                updated_data[col] = ''

        # Align columns for proper comparison
        existing_data, new_data = existing_data.align(new_data, join='outer', axis=1, fill_value='')

        # Ensure no duplicate columns
        existing_data = existing_data.loc[:, ~existing_data.columns.duplicated()]
        new_data = new_data.loc[:, ~new_data.columns.duplicated()]

        for _, new_row in new_data.iterrows():
            # Create a mask for matching rows (excluding 'Value' and extra columns)
            match_columns = [col for col in existing_data.columns if col not in ['Value', 'Unit', 'Source', 'Updated at', 'Updated by']]
            match = (existing_data[match_columns] == new_row[match_columns]).all(axis=1)
            
            if match.any():
                # Update the 'Value' and extra columns
                idx = match.idxmax()
                updated_data.loc[idx, 'Value'] = new_row['Value']
                updated_data.loc[idx, 'Updated at'] = datetime.now().strftime('%Y-%m-%d')
                updated_data.loc[idx, 'Source'] = "Automated entry, please add source"
                updated_data.loc[idx, 'Updated by'] = ""
            else:
                # Append the new row and fill extra columns
                new_row_extended = new_row.to_dict()
                new_row_extended.update({
                    'Unit': existing_data['Unit'].iloc[0] if 'Unit' in existing_data.columns else '',
                    'Updated at': datetime.now().strftime('%Y-%m-%d'),
                    'Source': "Automated entry, please add source",
                    'Updated by': ''
                })
                new_row_df = pd.DataFrame(new_row_extended, index=[0])
                new_row_df = new_row_df.reindex(columns=updated_data.columns, fill_value='')  # Ensure alignment with updated_data
                updated_data = pd.concat([updated_data, new_row_df], ignore_index=True)

        updated_data.to_csv(existing_csv_path, index=False)
    else:
        new_data['Updated at'] = datetime.now().strftime('%Y-%m-%d')
        new_data['Source'] = "Automated entry, please add source"
        new_data['Updated by'] = ""
        new_data.to_csv(existing_csv_path, index=False)
