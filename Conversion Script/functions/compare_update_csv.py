import pandas as pd
import os
from datetime import datetime

def update_or_append_csv(existing_csv_path, new_data):
    # Convert new_data columns to uppercase
    new_data.columns = [col.capitalize() for col in new_data.columns]

    if os.path.exists(existing_csv_path):
        existing_data = pd.read_csv(existing_csv_path)
        updated_data = existing_data.copy()

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

        # Replace NaN with empty string for comparison
        existing_data = existing_data.fillna('')
        new_data = new_data.fillna('')

        # Ensure data types match
        for col in existing_data.columns:
            if col in new_data.columns and existing_data[col].dtype != new_data[col].dtype:
                if existing_data[col].dtype == 'object':
                    new_data[col] = new_data[col].astype(str)
                elif existing_data[col].dtype == 'float64':
                    new_data[col] = pd.to_numeric(new_data[col], errors='coerce').fillna(0).astype(float)
                elif existing_data[col].dtype == 'int64':
                    new_data[col] = pd.to_numeric(new_data[col], errors='coerce').fillna(0).astype(int)

        for _, new_row in new_data.iterrows():
            # Create a mask for matching rows (excluding 'Value' and extra columns)
            match_columns = [col for col in existing_data.columns if col not in ['Value', 'Unit', 'Source', 'Updated at', 'Updated by']]
            match = (existing_data[match_columns].astype(str) == new_row[match_columns].astype(str)).all(axis=1)

            if match.any():
                # Get the index of the matched row
                idx = match.idxmax()
                # Check if the value is different
                if updated_data.loc[idx, 'Value'] != new_row['Value']:
                    # Update the 'Value' and extra columns
                    updated_data.loc[idx, 'Value'] = new_row['Value']
                    updated_data.loc[idx, 'Updated at'] = datetime.now().strftime('%d.%m.%Y')
                    updated_data.loc[idx, 'Source'] = "Automated entry, please add source"
                    updated_data.loc[idx, 'Updated by'] = ""
            else:
                # Append the new row and fill extra columns
                new_row_extended = new_row.to_dict()
                new_row_extended.update({
                    'Unit': existing_data['Unit'].iloc[0] if 'Unit' in existing_data.columns else '',
                    'Unnamed: 3': '',  # Insert empty value instead of 0.0
                    'Updated at': datetime.now().strftime('%d.%m.%Y'),
                    'Source': "Automated entry, please add source",
                    'Updated by': ''
                })
                new_row_df = pd.DataFrame(new_row_extended, index=[0])
                new_row_df = new_row_df.reindex(columns=updated_data.columns, fill_value='')  # Ensure alignment with updated_data
                updated_data = pd.concat([updated_data, new_row_df], ignore_index=True)

        updated_data.to_csv(existing_csv_path, index=False)
    else:
        new_data['Updated at'] = datetime.now().strftime('%d.%m.%Y')
        new_data['Source'] = "Automated entry, please add source"
        new_data['Updated by'] = ""
        new_data.to_csv(existing_csv_path, index=False)
