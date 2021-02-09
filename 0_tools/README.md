# Tools
Contains a selection of potentially useful code snippets that support but are not a critical part of the main workflow.

## ERA5 download coordinates
The ERA5 download scripts require specification on the coordinates to be downloaded in regular lat/lon format. This script loads the user-provided shapefile as specified in the control file, determines the bounding box of the shapefile and rounds these coordinates down (for minimum latitude and longitude) and up (for maximum latitude and longitude) to ERA5's 0.25 degree resolution. 

This procedure is not integrated in the main workflow scripts because it is not alwyas necessary (if the user has another way to determine the bounding box) and potentially quite slow for larger domains. 

