import os
import pandas as pd
import datetime

def output_regular_parameters(dataframes_dict, output_directory, output_excel_file_path, output_csv_directory, output_file_format, scenario_option):
    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    if output_file_format == 'excel':
        
        # Sort worksheet names alphabetically, but keep 'Sets' at the beginning
        sorted_worksheet_names = ['Sets'] + sorted([name for name in dataframes_dict if name != 'Sets'])

        # Write to Excel file
        start = datetime.datetime.now()
        with pd.ExcelWriter(output_excel_file_path, engine='xlsxwriter', mode='w') as excel_writer:
            for worksheet_name in sorted_worksheet_names:
                df_to_output = dataframes_dict[worksheet_name]
                df_to_output.to_excel(excel_writer, sheet_name=worksheet_name, index=False)
        end = datetime.datetime.now()
        difference = end-start
        print("Writing of the parameter data took: ",difference.total_seconds()," seconds")
        print("")
        print("")
    else:
        # Handle CSV output if required (same as before)
        for worksheet_name, df in dataframes_dict.items():
            output_file_path = os.path.join(output_csv_directory, f"{worksheet_name}_{scenario_option}.csv")
            df.to_csv(output_file_path, index=False)
