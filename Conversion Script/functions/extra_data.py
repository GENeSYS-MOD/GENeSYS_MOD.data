# Residual capacity og tag_daily storage

import pandas as pd


"""from pathlib import Path

def get_all_regions():

    #sets_directory = Path(__file__).parent.parent / "Data" / "Parameters" / "00_Sets&Tags"
    parameters_directory = Path(__file__).parent.parent / "Data" / "Parameters"

    # Get all parameters files
    parameters_files = [folder / (folder.name + ".csv") for folder in parameters_directory.iterdir() if folder.is_dir() and folder.name[:len("Par_")] == "Par_"]

    all_regions = set()

    for parameters_file in parameters_files:

        parameter_data = pd.read_csv(parameters_file)

        if "Region" in parameter_data.columns:
            all_regions.update(parameter_data["Region"])

    return all_regions

all_regions = get_all_regions()

"""

def extra_residual_capacity(parameters_dict: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    tech = "HLR_Heatpump_Aerial"
    year = 2018
    value = 100

    regions = ["AT", "BE", "BG", "CH", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GR", 
            "HR", "HU", "IE", "IT", "LT", "LU", "LV", "NL", "NO", "NONEU_Balkan", 
            "PL", "PT", "RO", "SE", "SI", "SK", "TR", "UK"]
    
    for region in regions:
        new_data = pd.DataFrame({"Region": [region], "Technology": [tech], "Year": [year], "Value": [value]})
        parameters_dict["Par_ResidualCapacity"] = pd.concat([parameters_dict["Par_ResidualCapacity"], new_data], ignore_index=True)

    return parameters_dict
    
def add_daily_or_seasonal(parameters_dict: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    
    #storages = ["S_Battery_Li-Ion", "S_Battery_Redox", "S_Heat_HLR", "S_Heat_HLI"] # "S_Heat_HLB", "S_Heat_HLDH", 

    storages = {"S_Battery_Li-Ion": 1, "S_Battery_Redox": 1, "S_Heat_HLR": 1, "S_Heat_HLI": 1, "S_Heat_HLB": 0, "S_Heat_HLDH": 0}

    parameters_dict["Par_TagDailyOrSeasonalStorage"] = pd.DataFrame(columns=["Storage", "IsDaily"]) 

    for storage, value in storages.items():

        new_data = pd.DataFrame({"Storage": [storage], "IsDaily": [value]})
        parameters_dict["Par_TagDailyOrSeasonalStorage"] = pd.concat([parameters_dict["Par_TagDailyOrSeasonalStorage"], new_data], ignore_index=True)

    return parameters_dict

def regional_base_add_HLDH(parameters_dict: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    tech = "HLDH_Biomass_Boiler"
    year = 2018
    value = 0.01

    regions = ["AT", "BE", "BG", "CH", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GR", 
            "HR", "HU", "IE", "IT", "LT", "LU", "LV", "NL", "NO", "NONEU_Balkan", 
            "PL", "PT", "RO", "SE", "SI", "SK", "TR", "UK"]
    
    for region in regions:
        # Use columns Region,Technology,Fuel,Year,Value,,Unit,Source,Updated at,Updated by
        new_data = pd.DataFrame({"Region": [region], "Technology": [tech], "Fuel": ["Heat_Low_DistrictHeat"], "Year": [year], "Value": [value], "": [""], 
                                 "Unit": ["PJ"], "Source": [""], "Updated at": [""], "Updated by": [""]})
        
        parameters_dict["Par_RegionalBaseYearProduction"] = pd.concat([parameters_dict["Par_RegionalBaseYearProduction"], new_data], ignore_index=True)

    # Delete unnamed column
    for column in parameters_dict["Par_RegionalBaseYearProduction"].columns:
        if column.startswith("Unnamed"):
            # Change name to ""
            parameters_dict["Par_RegionalBaseYearProduction"].rename(columns={column: ""}, inplace=True)

    return parameters_dict