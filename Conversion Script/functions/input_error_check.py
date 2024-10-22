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

    # Scenario check
    data_folder = os.path.join(os.getcwd(), '..', 'Data', 'Parameters')
    scenario_folder_paths = []
    existing_scenarios = set()

    if scenario_option.lower() != "none":
        # folders inside data_folder (inside 'Parameters')
        for folder_name in os.listdir(data_folder):
            folder_path = os.path.join(data_folder, folder_name)
            if os.path.isdir(folder_path):
                # check for scenario folder inside these folders
                for subfolder in os.listdir(folder_path):
                    subfolder_path = os.path.join(folder_path, subfolder)
                    if os.path.isdir(subfolder_path):
                        if subfolder.lower() == scenario_option.lower():
                            scenario_folder_paths.append(subfolder_path)
                        existing_scenarios.add(subfolder)

        if not scenario_folder_paths:
            existing_scenarios_list = sorted(list(existing_scenarios), key=lambda s: s.lower())
            expected_folders = ', '.join(f"'{d}'" for d in existing_scenarios_list)
            raise FileNotFoundError(f"No scenario folder found for option: '{scenario_option}'. Expected: {expected_folders}, or 'None'.")

    return True