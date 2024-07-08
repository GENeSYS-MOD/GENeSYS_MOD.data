# In your new module, e.g., functions_wrapper.py
from functions.input_error_check import validate_input
from functions.directories_definition import directories
from functions.read_settings_file import read_settings_file
from functions.read_parameters import read_regular_parameters
from functions.process_parameters import process_regular_parameters
from functions.output_parameters import output_regular_parameters
from functions.read_filter_timeseries import read_filter_timeseries
from functions.output_timeseries import output_timeseries
import sys
import pandas as pd
from pathlib import Path

def process_parameters(settings_file, output_format, scenario_option) -> dict[str, pd.DataFrame]:

    current_directory = Path(__file__).parent.parent
    #print("current_directory: ", current_directory)
    root_directory = current_directory.parent

    #unique_values_concatenated = read_settings_file( 
    unique_values_concatenated = read_settings_file(file_path=current_directory / settings_file,
                                                    output_csv_directory=root_directory / "Output" / "output_csv",
                                                    scenario_option=scenario_option,
                                                    output_format=output_format)
    
    #print("unique_values_concatenated: ", unique_values_concatenated)
    
    regular_parameter_paths = read_regular_parameters(current_directory, root_directory / "Data" / "Parameters")
    #print("regular_parameter_paths: ", regular_parameter_paths)

    worksheets_data = {'Sets': unique_values_concatenated}  # Including 'Sets' sheet
     
    worksheets_with_overwritten_data = []

    # Process files and store dataframes with their names
    for path in regular_parameter_paths:
        df_pivot, worksheet_name, data_overwritten = process_regular_parameters(path, unique_values_concatenated, output_format, scenario_option)
        worksheets_data[worksheet_name] = df_pivot  # or df_original based on your requirement

        # Check if data was overwritten and add to the list
        if data_overwritten:
            worksheets_with_overwritten_data.append(worksheet_name)
    
    # Print each worksheet name on a separate line with "Par_" removed
    print("Worksheets with specified scenario data:")
    for worksheet in worksheets_with_overwritten_data:
        readable_name = worksheet.replace("Par_", "")
        print(readable_name)
    print("\n")  # Prints a blank line 

    return worksheets_data

def process_timeseries(settings_file, output_format, scenario_option) -> dict[str, pd.DataFrame]:

    current_directory = Path(__file__).parent.parent
    #print("current_directory: ", current_directory)
    root_directory = current_directory.parent

    unique_values_concatenated = read_settings_file(file_path=current_directory / settings_file,
                                                    output_csv_directory=root_directory / "Output" / "output_csv",
                                                    scenario_option=scenario_option,
                                                    output_format=output_format)

    filtered_timeseries_data, timeseries_output_string = read_filter_timeseries(root_directory / "Data" / "Timeseries", unique_values_concatenated, scenario_option)

    return filtered_timeseries_data



def master_function(settings_file,output_file_format, output_format, processing_option, scenario_option):
    # Call directories function to get all necessary directory paths
    current_directory, excel_file_path, parameter_directory, sets_and_tags_directory, timeseries_directory, output_csv_directory, output_excel_directory, output_excel_file_path, output_excel_file_path_timeseries = directories(settings_file, scenario_option)

    # Validate user input
    validate_input(output_file_format, output_format, processing_option, settings_file)

    # Ensure unique_values_concatenated is defined
    unique_values_concatenated = read_settings_file(excel_file_path, output_csv_directory, scenario_option, output_format)


    # Check if processing_option is not 'timeseries_only'
    if processing_option != 'timeseries_only':
        # Process each regular parameter file
        regular_parameter_paths = read_regular_parameters(current_directory, parameter_directory, sets_and_tags_directory)
        

        # Store the worksheet names and corresponding dataframes
        worksheets_data = {'Sets': unique_values_concatenated}  # Including 'Sets' sheet
     
        worksheets_with_overwritten_data = []

        # Process files and store dataframes with their names
        for path in regular_parameter_paths:
            df_pivot, worksheet_name, data_overwritten = process_regular_parameters(path, unique_values_concatenated, output_format, scenario_option)
            worksheets_data[worksheet_name] = df_pivot  # or df_original based on your requirement

            # Check if data was overwritten and add to the list
            if data_overwritten:
                worksheets_with_overwritten_data.append(worksheet_name)
        
        # Print each worksheet name on a separate line with "Par_" removed
        print("Worksheets with specified scenario data:")
        for worksheet in worksheets_with_overwritten_data:
            readable_name = worksheet.replace("Par_", "")
            print(readable_name)
        print("\n")  # Prints a blank line    
        

        # Call the function to output data
        output_regular_parameters(worksheets_data, output_excel_directory, output_excel_file_path, output_csv_directory, output_file_format, scenario_option)
        

    # Process timeseries if processing_option is not 'parameters_only'
    if processing_option != 'parameters_only':
        # Read and filter time series data
        filtered_timeseries_data, timeseries_output_string = read_filter_timeseries(timeseries_directory, unique_values_concatenated, scenario_option)

        # Print the output string
        print("Timeseries data overwritten by scenario data:")
        print(timeseries_output_string)

        # Output the processed data
        output_timeseries(filtered_timeseries_data, output_excel_directory, output_excel_file_path_timeseries, output_csv_directory, output_file_format, scenario_option)

    print("\nProcessing finished. Smile and hope that you added your data correctly :)")
    # Return any necessary data or confirmation
