# In your new module, e.g., functions_wrapper.py
from functions.input_error_check import validate_input
from functions.directories_definition import directories
from functions.read_settings_file import read_settings_file
from functions.read_parameters import read_regular_parameters
from functions.process_parameters import process_regular_parameters
from functions.output_parameters import output_regular_parameters
from functions.read_filter_timeseries import read_filter_timeseries
from functions.output_timeseries import output_timeseries

def master_function(output_file_format, output_format, processing_option):
    # Call directories function to get all necessary directory paths
    current_directory, excel_file_path, parameter_directory, sets_and_tags_directory, timeseries_directory, output_csv_directory, output_excel_directory, output_excel_file_path, output_excel_file_path_timeseries = directories()

    # Validate user input
    validate_input(output_file_format, output_format, processing_option)

    # Ensure unique_values_concatenated is defined
    unique_values_concatenated = read_settings_file(excel_file_path, output_csv_directory)

    # Check if processing_option is not 'timeseries_only'
    if processing_option != 'timeseries_only':
        # Process each regular parameter file
        regular_parameter_paths = read_regular_parameters(current_directory, parameter_directory, sets_and_tags_directory)

        # Store the worksheet names and corresponding dataframes
        worksheets_data = {'Sets': unique_values_concatenated}  # Including 'Sets' sheet

        # Process files and store dataframes with their names
        for path in regular_parameter_paths:
            df_pivot, worksheet_name = process_regular_parameters(path, unique_values_concatenated, output_format)
            worksheets_data[worksheet_name] = df_pivot  # or df_original based on your requirement

        # Call the function to output data
        output_regular_parameters(worksheets_data, output_excel_directory, output_excel_file_path, output_csv_directory, output_file_format)

    # Process timeseries if processing_option is not 'parameters_only'
    if processing_option != 'parameters_only':
        # Read and filter time series data
        filtered_timeseries_data = read_filter_timeseries(timeseries_directory, unique_values_concatenated)

        # Output the processed data
        output_timeseries(filtered_timeseries_data, output_excel_directory, output_excel_file_path_timeseries, output_csv_directory, output_file_format)


    # Return any necessary data or confirmation
