def validate_input(output_file_format, output_format, processing_option):
    
    valid_file_formats = ['csv', 'excel']
    if output_file_format.lower() not in valid_file_formats:
        raise ValueError(f"Invalid output file format: '{output_file_format}'. Expected 'csv' or 'excel'.")
    
    valid_output_formats = ['long', 'wide']
    if output_format.lower() not in valid_output_formats:
        raise ValueError(f"Invalid output format: '{output_format}'. Expected 'wide' or 'long'.")
    
    valid_processing_options = ['both', 'parameters_only', 'timeseries_only']
    if processing_option.lower() not in valid_processing_options:
        raise ValueError(f"Invalid processing option: '{processing_option}'. Expected 'both', 'parameters_only', or 'timeseries_only'.")

    return True