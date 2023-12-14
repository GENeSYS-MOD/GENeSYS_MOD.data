import os

def read_regular_parameters(main_directory, parameter_directory, sets_and_tags_directory, file_pattern='Par_'):
    filepaths = []

    # Updated path for the sets_and_tags_directory within the 00_Parameters directory
    sets_and_tags_directory_f = os.path.join(main_directory, parameter_directory, sets_and_tags_directory)
    
    # Check if the sets_and_tags_directory exists, then add files
    if os.path.exists(sets_and_tags_directory_f):
        for f in os.listdir(sets_and_tags_directory_f):
            if f.startswith(file_pattern) and f.endswith('.csv'):
                filepaths.append(os.path.join(sets_and_tags_directory_f, f))

    # Continue to add files from subdirectories of 00_Parameters
    parameters_directory_f = os.path.join(main_directory, parameter_directory)
    for root, dirs, files in os.walk(parameters_directory_f):
        for file in files:
            if file.startswith(file_pattern) and file.endswith('.csv'):
                filepaths.append(os.path.join(root, file))

    return filepaths
