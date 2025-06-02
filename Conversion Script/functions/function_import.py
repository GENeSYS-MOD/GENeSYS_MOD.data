# In your new module, e.g., functions_wrapper.py
from functions.input_error_check import validate_input
from functions.directories_definition import directories
from functions.read_settings_file import read_settings_file
from functions.read_parameters import read_regular_parameters
from functions.process_parameters import process_regular_parameters
from functions.output_parameters import output_regular_parameters
from functions.read_filter_timeseries import read_filter_timeseries
from functions.output_timeseries import output_timeseries
from functions.data_error_check import search_non_utf8_characters
import sys

def master_function(settings_file,output_file_format, output_format, processing_option, scenario_option, debugging_output, data_base_region):
    # Call directories function to get all necessary directory paths
    current_directory, excel_file_path, parameter_directory, sets_and_tags_directory, timeseries_directory, output_csv_directory, output_excel_directory, output_excel_file_path, output_excel_file_path_timeseries = directories(settings_file, scenario_option)

    # Validate user input
    validate_input(output_file_format, output_format, processing_option, settings_file, scenario_option)

    # check for utf-8-errors
    #search_non_utf8_characters()

    try:
        search_non_utf8_characters()  # Assuming this function checks for non-UTF-8 files
    except UnicodeDecodeError as e:
        print("Non UTF-8 characters found in file" + '{relative_path}')

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
            df_pivot, worksheet_name, data_overwritten = process_regular_parameters(path, unique_values_concatenated, output_format, scenario_option,debugging_output, data_base_region)
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

    print("\nEverything worked successfully. You are great! Smile :)")
    # Return any necessary data or confirmation
