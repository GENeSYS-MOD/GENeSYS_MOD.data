import os
import pandas as pd 
from read_csv_from_directory import process_files

# This function is to process trade files
def trade_changed_files(config, main_folder, output_path):
    trade_changed_files = config['parameters']['trade_files'] 
    
    # Load each CSV file from the main folder
    for df, file_path in process_files(main_folder):
        param_name = os.path.splitext(os.path.basename(file_path))[0]
        file_path = os.path.join(output_path, f'{param_name}.csv') 
        
        for file in trade_changed_files:
            if param_name == file['file_name']:
                method = file['method']
                index_count = file['index_count']
                regions_to_split = file['regions_to_split']
                new_regions = file['new_regions']
                split_ratio = file['split_ratio']
                new_connections = file.get('new_connections', {})  # Extract new connections
                
                print(param_name, method, index_count, regions_to_split, new_regions, split_ratio, new_connections)
                
                df.set_index(df.columns[:index_count].tolist(), inplace=True)

                # Process regions to split
                for region in regions_to_split:
                    if region in df.index.get_level_values('Region'):
                        print(f"Processing region: {region}")
                        ref_row = df.loc[region].iloc[0].to_dict()  # Get only one reference row as dictionary
                        
                        # Filter rows where Region == 'NO'
                        region_data = df.loc[region].copy() #added later
                        index_cols = df.index.names #added later
                        new_region_dfs = []
                        
                        # Standard region split
                        for new_region, ratio in split_ratio.items():
                            new_data = region_data.to_frame().T if isinstance(region_data, pd.Series) else region_data.copy()
                            new_data['Value'] *= ratio
                            
                            # Modify 'Region' in place without adding a new column
                            new_data.loc[:, "Region"] = new_region
                            
                            print(f"new data:", new_data.tail())
                                                        
                            new_data.reset_index(inplace=True)
                            
                            new_region_dfs.append(new_data)
                        
                        # Add new connections dynamically
                        for key, details in new_connections.items():
                            if "-" in key:
                                reg1, reg2 = key.split("-")

                                # Manually create a new row for this connection
                                conn_row = ref_row.copy()

                                conn_row[index_cols[0]] = reg1  # Update first index column (e.g., 'Region')
                                if len(index_cols) > 1:
                                    conn_row[index_cols[1]] = reg2  # Update second index column (e.g., 'Region2')

                                conn_row["Value"] = details["value"]  # Assign new connection value

                                # Convert to DataFrame and add to list
                                new_region_dfs.append(pd.DataFrame([conn_row]))
                                print(f"Added connection: {reg1} -> {reg2} with Value: {details['value']}")


                        combined_new_regions = pd.concat(new_region_dfs, ignore_index=True)
                        
                        # Add the new regions back to the original DataFrame
                        df.reset_index(inplace=True)
                        df = pd.concat([df, combined_new_regions], ignore_index=True)

                        # Reapply multi-index
                        df.set_index(df.columns[:index_count].tolist(), inplace=True)

                        # Save the modified DataFrame
                        df.to_csv(file_path)

                    else:
                        print(f"Region {region} not found in dataset")
                        df.to_csv(file_path)

    print("Processing completed.")