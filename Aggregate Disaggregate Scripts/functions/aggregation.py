import pandas as pd

def aggregate_data(df, method, index_count, regions_to_combine, new_region, output_csv="aggregated_data.csv"):
    """
    Aggregates data in a DataFrame based on the given regions and saves the result as a new CSV file.

    Parameters:
        df (pd.DataFrame): The input DataFrame.
        method (str): Aggregation method (e.g., 'sum', 'mean').
        index_count (int): The number of index levels to use for aggregation.
        regions_to_combine (list): List of region names to combine.
        new_region (str): Name for the new aggregated region.
        output_csv (str): Path to save the resulting CSV file.

    Returns:
        pd.DataFrame: The aggregated DataFrame.
    """
    if method not in ['sum', 'mean']:
        raise ValueError("Supported methods are 'sum' and 'mean'")

    df = df.reset_index()
    index_columns = df.columns[:index_count].tolist()
    df.set_index(index_columns, inplace=True)
    filtered_df = df[df.index.get_level_values('Region').isin(regions_to_combine)]

    aggregated_rows = []
    grouped_by = index_columns[1:]  
    print(grouped_by)
    
    for group in filtered_df.groupby(grouped_by):
        group_data = group[1]
        if method == 'sum':
            aggregated_row = group_data.sum(numeric_only=True)
        elif method == 'mean':
            aggregated_row = group_data.mean(numeric_only=True)
        elif method == 'copy':
            aggregated_row = group_data.copy()

        aggregated_row['Region'] = new_region
 
        if isinstance(group[0], tuple):
            for i, level_name in enumerate(grouped_by):
                aggregated_row[level_name] = group[0][i]
        else:
            aggregated_row[grouped_by[0]] = group[0]

        aggregated_rows.append(aggregated_row)

    aggregated_df = pd.DataFrame(aggregated_rows)

    result_df = df.copy() #[~df.index.get_level_values('Region').isin(regions_to_combine)]
    result_df = result_df.reset_index()
    result_df = pd.concat([result_df, aggregated_df], ignore_index=True)
   
    return result_df
    