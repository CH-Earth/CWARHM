# Tools
Contains a selection of potentially useful code snippets that support but are not a critical part of the main workflow.

## 1. Shapefile bounding box coordinates
The ERA5 download scripts and several others related to downloading and processing parameter fields need to know the spatial extent of the domain in regular lat/lon format. This script loads the user-provided shapefile as specified in the control file, determines the bounding box of the shapefile and rounds these coordinates slightly down (for minimum latitude and longitude) and up (for maximum latitude and longitude). This ensures that downloads and cutouts based on these coordinates are slightly larger than the modelling domain.

This procedure is not integrated in the main workflow scripts because it is not always necessary (if the user has another way to determine the bounding box) and potentially quite slow for larger domains. 


## 2. ERA5 sanity check
After merging ERA5 surface and pressure level data into a single file, performing some rudimentary checks on the data can give peace of mind about the download and merging procedures. This script iterates over each merged file and performs a few sanity checks. It generates a log file listing for each forcing variable how often its value equals NaN or is missing and how often values fall outside user-specified ranges. It equally checks that the time dimension has equidistant and consecutive values (in each individual file, this is not between different files).


## X. Summarize SUMMA logs
Log files are created for this run as usual when SUMMA is run with the option `-g startGRU numGRU`. If such a run is part of a parallel simulation where the modelling domain is divided into multiple chunks of GRUs, analyzing these individual log files for successes or graceful failures can be cumbersome. This script summarizes the log files by reading the final few lines in each log file and divides the full run into success/SUMMA error/early termination. It also reports the time needed for successful runs. The summary file is placed at the top of the log folder if no other name for the summary file is provided. Usage: `python summarize_logs.py [log_folder] [optional: name_of_summary_file.txt]`. **Note** that this function assumes that the provided folder **only** contains SUMMA log files. Things may break if this is not the case. 