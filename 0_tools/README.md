# Tools
Contains a selection of potentially useful code snippets that support but are not a critical part of the main workflow.

## ERA5 tools
###  Shapefile bounding box coordinates
Filename(s): ERA5_find_download_coordinates_from_shapefile.ipynb

The ERA5 download scripts and several others related to downloading and processing parameter fields need to know the spatial extent of the domain in regular lat/lon format. This script loads the user-provided shapefile as specified in the control file, determines the bounding box of the shapefile and rounds these coordinates slightly down (for minimum latitude and longitude) and up (for maximum latitude and longitude). This ensures that downloads and cutouts based on these coordinates are slightly larger than the modelling domain.

This procedure is not integrated in the main workflow scripts because it is not always necessary (if the user has another way to determine the bounding box) and potentially quite slow for larger domains. 


### ERA5 sanity check
Filename(s): ERA5_check_merged_forcing_values.ipynb, ERA5_check_merged_forcing_values.py

After merging ERA5 surface and pressure level data into a single file, performing some rudimentary checks on the data can give peace of mind about the download and merging procedures. This script iterates over each merged file and performs a few sanity checks. It generates a log file listing for each forcing variable how often its value equals NaN or is missing and how often values fall outside user-specified ranges. It equally checks that the time dimension has equidistant and consecutive values (in each individual file, this is not between different files).


## SUMMA tools

### Merge separate output files into a single file
Filename(s): SUMMA_concat_split_summa.py

SUMMA's split-domain runs (i.e. those with the `-g` argument) result in output files that only contain data for the given subset of GRUs. This script concatenates multiple split-domain output files into a single file. Usage: `python SUMMA_concat_split_summa.py [path/to/split/outputs/] [input_file_*_pattern.nc] [output_file.nc]`. 

### Merge separate domain-split output files into temporally-split files
Filename(s): tbd

SUMMA's split-domain runs (i.e. those with the `-g` argument) result in output files that only contain data for the given subset of GRUs, but for the full temporal domain for each GRU. mizuRoute can read inputs that are split across time (e.g. year1.nc, year2.nc, etc.) but requires that each file has data for all GRUs in the domain. This file converts SUMMA's some-grus-but-all-time.nc files into mizuRoute's required all-grus-but-some-time.nc files. Note that such conversion is mostly useful in cases of larger domains, where storing the full timeseries for all GRUs in one file is infeasible.



### Merge separate restart files into a single initial conditions file
Filename(s): SUMMA_merge_restarts_into_warmState.py

SUMMA's restart files are intended to be used as initial condition files to either pick up a run from a given point or as estimates of the initial states for a new run. Restart files generated from a run with a subset of GRUs (i.e. using the `-g` argument) will only contain information for the selected subset of GRUs. This file concatenates multiple split-domain restarts into a single file. 

**Note** that this function does not utilize the `control_active.txt` file and manual changes to the file will be needed. See the file itself for a description.


### Summarize SUMMA logs
Filename(s): SUMMA_summarize_logs.py

Log files are created for a run as usual when SUMMA is run with the option `-g startGRU numGRU`. If such a run is part of a parallel simulation where the modelling domain is divided into multiple chunks of GRUs, analyzing these individual log files for successes or graceful failures can be cumbersome. This script summarizes the log files by reading the final few lines in each log file and divides the full run into success/SUMMA error/early termination. It also reports the time needed for successful runs. The summary file is placed at the top of the log folder if no other name for the summary file is provided. Usage: `python SUMMA_summarize_logs.py [log_folder] [optional: name_of_summary_file.ext] [optional: extension of log files (default: .txt)]`. 

**Note** that this function assumes that the provided folder **only** contains SUMMA log files. Things may break if this is not the case. 