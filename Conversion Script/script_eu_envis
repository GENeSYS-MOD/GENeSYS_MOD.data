# -*- coding: utf-8 -*- 
settings_file = 'Set_filter_file.xlsx' 
output_file_format = 'excel' 
output_format = 'long' 
processing_option = 'both' 
scenario_option = 'Europe_EnVis_NECPEssentials' 
debugging_output = False 
data_base_region = 'DE' 
from functions.function_import import master_function 
scenarios = ["Europe_EnVis_Green","Europe_EnVis_Trinity","Europe_EnVis_REPowerEU++","Europe_EnVis_NECPEssentials"] 
for s in scenarios: 
    print("Currently performing operation for scenario: ", s) 
    master_function(settings_file, output_file_format, output_format, processing_option, s, debugging_output, data_base_region) 
