import os

def directories(settings_file, scenario_option):
    # Get the current working directory (where the script is located)
    current_directory = os.getcwd()

    # Assuming the script is in 'Conversion Script', and you need to go one level up to access 'Data' and 'Output'
    parent_directory = os.path.dirname(current_directory)

    # Directories inside the 'Data' folder
    data_directory = os.path.join(parent_directory, 'Data')
    sets_and_tags_directory = os.path.join(data_directory, 'Sets&Tags')
    parameter_directory = os.path.join(data_directory, 'Parameters')
    timeseries_directory = os.path.join(data_directory, 'Timeseries')

    # Directories for output
    output_directory = os.path.join(parent_directory, 'Output')
    output_csv_directory = os.path.join(output_directory, 'output_csv')
    output_excel_directory = os.path.join(output_directory, 'output_excel')
    output_excel_file_path = os.path.join(output_excel_directory, f"RegularParameters_{scenario_option}.xlsx")
    output_excel_file_path_timeseries = os.path.join(output_excel_directory, f"Timeseries_{scenario_option}.xlsx")

    # Path to the Excel settings file
    excel_file_path = os.path.join(current_directory, settings_file)

    return current_directory, excel_file_path, parameter_directory, sets_and_tags_directory, timeseries_directory, output_csv_directory, output_excel_directory, output_excel_file_path, output_excel_file_path_timeseries  
