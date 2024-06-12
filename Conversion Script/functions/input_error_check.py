import os

def validate_input(output_file_format, output_format, processing_option, settings_file, scenario_option):
    
    valid_file_formats = ['csv', 'excel']
    if output_file_format.lower() not in valid_file_formats:
        raise ValueError(f"Invalid output file format: '{output_file_format}'. Expected 'csv' or 'excel'.")
    
    valid_output_formats = ['long', 'wide']
    if output_format.lower() not in valid_output_formats:
        raise ValueError(f"Invalid output format: '{output_format}'. Expected 'wide' or 'long'.")
    
    valid_processing_options = ['both', 'parameters_only', 'timeseries_only']
    if processing_option.lower() not in valid_processing_options:
        raise ValueError(f"Invalid processing option: '{processing_option}'. Expected 'both', 'parameters_only', or 'timeseries_only'.")
    
    file_path = os.path.join(os.getcwd(), settings_file)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The specified filter file '{settings_file}' does not exist in the directory.")

    # Prüfung der Szenario-Option
    data_folder = os.path.join(os.getcwd(), '..', 'Data', 'Parameters')
    scenario_file_paths = []
    existing_scenarios = []
    if scenario_option.lower() != "none":
        for root, dirs, files in os.walk(data_folder):
            for file in files:
                if file.lower().startswith(scenario_option.lower()) and file.lower().endswith('.xlsx'):
                    scenario_file_paths.append(file)
                elif file.lower().endswith('.xlsx'):
                    existing_scenarios.append(f"'{os.path.splitext(file)[0]}'")
                    

        if not scenario_file_paths:
            existing_scenarios.sort()
            expected_files = ', '.join(existing_scenarios)
            raise FileNotFoundError(f"No Excel file found for scenario option: '{scenario_option}'. Expected: {expected_files}, or 'None'.")

    return True