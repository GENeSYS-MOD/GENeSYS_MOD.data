# GENeSYS_MOD.data
The Global Energy System Model (GENeSYS-MOD) - Data repository

## General Information
Complete fundamental data repository for GENeSYS-MOD. All input parameters are presented with source tags, including general input (*Par_*) and time series input (*TS_*). A complete overview of all input parameters, including description and unit, is presented in *Overview_GENeSYS-MOD.csv*. Sources for all data is included within each input parameter folder, along with general assumptions (see *Assumptions.txt*) on how the data is created when relevant. 

## Guidelines for data modification
- It is **forbidden** to modify or add data without adding a source tag.
- All input parameters are given in .csv-files with comma (,) as the delimiter.
- A source tag **must not** include semicolon (;) or quotation marks (").
- A source tag can be based on several assumptions. These assumptions can be elaborated upon in *Assumptions.txt*.
- A source tag includes a datestamp for when it was updated. *Format: dd.mm.yyyy*
- A source tag includes a contact person with e-mail adress. *Format: Firstname Lastname \<email adress>*
- The fundamental data should have a source tag. If it doesn't, it needs to be updated.
- All data sheets, reports, or data files that are used as sources should be uploaded to the data repository within *00_Sources*. Further, add source name, file name, and which input parameters it is used for in *00_Overview_Sources.csv*.  

## Adding data that are specific to a project/scenario
If the data modification is linked to a specific project/scenario, the fundamental data shall not be modified. Rather, create a new project/scenario folder within each of the input parameters that have different data from the fundamental data in that project/scenario. Within the new project/scenario folder, a .csv-file should be created with the input parameter name, and it shall contain the data to be overwritten when running GENeSYS-MOD for that project/scenario. Note that the format of the new .csv-file must match the format of the fundamental .csv-file for each respective input parameter, but the new .csv-file does not need to contain all the rows of the fundamental .csv-file. 

## General format of rows with source tags
|Index|(...)|Index|Value|\<empty column>|Unit| Source | Updated at (dd.mm.yyyy) | Updated by (Firstname Lastname \<email adress>)|
| ------| ----- | ------| ------- | --- |--|-----|-------------|---------------| 

## Examples of data rows with source tags
### Example 1
|Region|Technology|Year|Value||Unit| Source | Updated at | Updated by |
| ------| ----- | ------| ------- | --- |--|-----|-------------|---------------| 
|World|RES_Geothermal|2018|4970| |MEUR/GW|Geothermal Power- Table 1.7- High cost of slow energy transitions for emerging countries: On the case of Egypt's pathway options- Appendix A Supplementary data | 06.09.2023 | John Johnson \<name@domain.com> |

### Example 2

|Emission|Year|Value||Unit| Source | Updated at | Updated by |
| ------| ------| ------- | --- |--|-----|-------------|---------------| 
|CO2|2018|99999| |Mton|Assumption that makes the constraint not effective | 06.09.2023 | John Johnson \<name@domain.com>  |

### Example 3
|Region|Region|Fuel|Value ||Unit| Source | Updated at | Updated by |
| ------| ------| ------- | --- |--|--|---|-------------|---------------|
|AT|CH|Biofuel|439| |km|Own calulation of distance - see txt.file for more Info | 06.09.2023 | John Johnson \<name@domain.com>  |