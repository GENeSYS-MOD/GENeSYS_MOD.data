# -*- coding: utf-8 -*- 
settings_file = 'Conversion Script/Set_filter_file_MiddleEarth.xlsx'
output_file_format = 'excel' 
output_format = 'long' 
processing_option = 'both' 
scenario_option = 'MiddleEarth'
debugging_output = False 
data_base_region = 'Gondor'  

from functions.function_import import master_function

master_function(settings_file,output_file_format, output_format, processing_option, scenario_option, debugging_output, data_base_region)
