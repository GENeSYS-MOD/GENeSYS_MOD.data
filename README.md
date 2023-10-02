# GENeSYS_MOD.data
The Global Energy System Model (GENeSYS-MOD) - Data repository

## General Information
Complete fundamental data repository for GENeSYS-MOD. All input parameters are presented with source tags, including general input (*Par_*) and time series input (*TS_*). A complete overview of all input parameters, including description and unit, is presented in *Overview_GENeSYS-MOD.csv*. Sources for all data is included within each input parameter folder, along with general assumptions (see *Assumptions.txt*) on how the data is created when relevant. 

## Guidelines for data modification
- It is **forbidden** to modify data without adding a source tag.
- A source tag can be based on several assumptions. These assumptions can be elaborated upon in *Assumptions.txt*.
- The fundamental data should have a source tag. If it doesn't, it needs to be updated.
- All data sheets, reports, or data files that are used as sources should be uploaded to the data repository within *00_Sources*. Further, add source name, file name, and which input parameters it is used for in *00_Overview_Sources.csv*.  
- If the data modification is linked to a specific project/scenario, the fundamental data should not be modified. Rather, create a new folder with the project/scenario name within the input parameter folder. Within the new folder, a .csv-file should be created with input parameter name containing the data that should be overwritten when running GENeSYS-MOD for that project/scenario. Note that the format of the new .csv-file must match the format of the fundamental .csv-file for each respective input parameter. 

## Example source tags
| Source | Updated at (dd.mm.yyyy) | Updated by |
| ----------- | ----------- | ---------------- |
| Geothermal Power; Table 1.7; High cost of slow energy transitions for emerging countries: On the case of Egypt's pathway options; Appendix A Supplementary data | 06.09.2023 | Firstname Lastname <email adress> |
| Wind-offshore - shallow waters; distant from shore; high resource area; Power&Heat; EU Reference Scenario 2020 | 06.09.2023 | Firstname Lastname <email adress> |
| Assumption that makes the constraint not effective | 05.09.2023 | Firstname Lastname <email adress> |
| Own calulation of distance - see txt.file for more Info | 05.09.2023 | Firstname Lastname <email adress> |