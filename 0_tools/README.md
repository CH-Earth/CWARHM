# Tools
Contains a selection of potentially useful code snippets that support but are not a critical part of the main workflow.

## 1. ERA5 download coordinates
The ERA5 download scripts require specification on the coordinates to be downloaded in regular lat/lon format. This script loads the user-provided shapefile as specified in the control file, determines the bounding box of the shapefile and rounds these coordinates down (for minimum latitude and longitude) and up (for maximum latitude and longitude) to ERA5's 0.25 degree resolution. 

This procedure is not integrated in the main workflow scripts because it is not alwyas necessary (if the user has another way to determine the bounding box) and potentially quite slow for larger domains. 


## 2. ERA5 sanity check
After merging ERA5 surface and pressure level data into a single file, performing some rudimentary checks on the data can give peace of mind about the download and merging procedures. This script iterates over each merged file and performs a few sanity checks. It generates a log file listing for each forcing variable how often its value equals NaN or is missing and how often values fall outside user-specified ranges. It equally checks that the time dimension has equidistant and consecutive values (in each individual file, this is not between different files).

