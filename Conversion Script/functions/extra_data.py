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
    techs = ["HLR_Heatpump_Aerial", "HLDH_Heatpump_Air"]
    year = 2018
    value = 100

    regions = ["AT", "BE", "BG", "CH", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GR", 
            "HR", "HU", "IE", "IT", "LT", "LU", "LV", "NL", "NO", "NONEU_Balkan", 
            "PL", "PT", "RO", "SE", "SI", "SK", "TR", "UK"]
    
    for tech in techs:
        for region in regions:
            new_data = pd.DataFrame({"Region": [region], "Technology": [tech], "Year": [year], "Value": [value]})
            parameters_dict["Par_ResidualCapacity"] = pd.concat([parameters_dict["Par_ResidualCapacity"], new_data], ignore_index=True)

    return parameters_dict
    
def add_daily_or_seasonal(parameters_dict: dict[str, pd.DataFrame], storages: dict[str, float]) -> dict[str, pd.DataFrame]:
    
    #storages = ["S_Battery_Li-Ion", "S_Battery_Redox", "S_Heat_HLR", "S_Heat_HLI"] # "S_Heat_HLB", "S_Heat_HLDH", 

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
        new_data = pd.DataFrame({"Region": [region], "Technology": [tech], "Fuel": ["Heat_District"], "Year": [year], "Value": [value], "": [""], 
                                 "Unit": ["PJ"], "Source": [""], "Updated at": [""], "Updated by": [""]})
        
        parameters_dict["Par_RegionalBaseYearProduction"] = pd.concat([parameters_dict["Par_RegionalBaseYearProduction"], new_data], ignore_index=True)

    # Delete unnamed column
    for column in parameters_dict["Par_RegionalBaseYearProduction"].columns:
        if column.startswith("Unnamed"):
            # Change name to ""
            parameters_dict["Par_RegionalBaseYearProduction"].rename(columns={column: ""}, inplace=True)

    return parameters_dict

def capital_cost_change(parameters_dict: dict[str, pd.DataFrame], capital_cost_percentages: dict[str, float]) -> dict[str, pd.DataFrame]:
    # Change capital cost of all technologies
    for tech, percentage in capital_cost_percentages.items():
        parameters_dict["Par_CapitalCost"].loc[parameters_dict["Par_CapitalCost"]["Technology"] == tech, "Value"] *= percentage

    return parameters_dict


def cool_low_building_no_2018(parameters_dict: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    
    # In SpecifiedAnnualDemand, set the value of cooling for fuel Cool_Low_Building to 0 for year 2018

    parameters_dict["Par_SpecifiedAnnualDemand"].loc[(parameters_dict["Par_SpecifiedAnnualDemand"]["Fuel"] == "Cool_Low_Building") & (parameters_dict["Par_SpecifiedAnnualDemand"]["Year"] == 2018), "Value"] = 0

    return parameters_dict

# Prevent specified annual_demand from being 0
def specified_annual_demand_not_zero(parameters_dict: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    
    parameters_dict["Par_SpecifiedAnnualDemand"].loc[parameters_dict["Par_SpecifiedAnnualDemand"]["Value"] == 0, "Value"] = 0.000001

    return parameters_dict

# Add a new technology to the Par_CapitalCost table
def add_technology_capital_cost(parameters_dict: dict[str, pd.DataFrame], tech: str, value: float) -> dict[str, pd.DataFrame]:
    
    # Columns: Region,Technology,Year,Value,,Unit,Source,Updated at,Updated by
    for year in [2018, 2020, 2025, 2030, 2035, 2040, 2045, 2050]:
        new_data = pd.DataFrame({"Region": ["World"], "Technology": [tech], "Year": [year], "Value": [value], "": [""], 
                                "Unit": ["EUR/kW"], "Source": [""], "Updated at": [""], "Updated by": [""]})
        
        parameters_dict["Par_CapitalCost"] = pd.concat([parameters_dict["Par_CapitalCost"], new_data], ignore_index=True)

    return parameters_dict