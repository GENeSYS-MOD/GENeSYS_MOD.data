import pandas as pd
from datetime import datetime
import os

def update_or_append_csv(existing_csv_path, new_data):
    try:
        existing_data = pd.read_csv(existing_csv_path)
        
        # Drop unnamed columns from existing data
        existing_data = existing_data.loc[:, ~existing_data.columns.str.contains('^Unnamed')]
        
        # Ensure new_data has the same columns as existing_data
        new_data = new_data.reindex(columns=existing_data.columns[:len(new_data.columns)], fill_value='')

        updated_data = existing_data.copy()

        for _, new_row in new_data.iterrows():
            match_columns = [col for col in existing_data.columns if col not in ['Value', 'Unit', 'Source', 'Updated at', 'Updated by']]
            match = (existing_data[match_columns] == new_row[match_columns]).all(axis=1)

            if match.any():
                idx = match.idxmax()
                if existing_data.loc[idx, 'Value'] != new_row['Value']:
                    updated_data.loc[idx, 'Value'] = new_row['Value']
                    updated_data.loc[idx, 'Updated at'] = datetime.now().strftime('%d.%m.%Y')
                    updated_data.loc[idx, 'Source'] = "Automated entry, please add source"
                    updated_data.loc[idx, 'Updated by'] = ""
            else:
                new_row_extended = pd.concat([new_row, pd.Series({
                    'Unit': existing_data['Unit'].iloc[0] if 'Unit' in existing_data.columns else '',
                    'Updated at': datetime.now().strftime('%d.%m.%Y'),
                    'Source': "Automated entry, please add source",
                    'Updated by': ''
                })])

                # Remove duplicate columns before reindexing
                new_row_extended = new_row_extended.loc[~new_row_extended.index.duplicated(keep='first')]

                # Reindex new_row_extended to match the columns of updated_data
                new_row_extended = new_row_extended.reindex(updated_data.columns, fill_value='')

                updated_data = pd.concat([updated_data, new_row_extended.to_frame().T], ignore_index=True)

        # Remove rows with empty critical columns before saving
        critical_columns = ['Emission', 'Year', 'Value']
        updated_data = updated_data.dropna(subset=critical_columns)

        updated_data.to_csv(existing_csv_path, index=False)
    except FileNotFoundError:
        new_data['Unit'] = ''
        new_data['Updated at'] = datetime.now().strftime('%d.%m.%Y')
        new_data['Source'] = "Automated entry, please add source"
        new_data['Updated by'] = ''
        new_data.to_csv(existing_csv_path, index=False)
