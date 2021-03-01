# Download ERA5

## Code setup
### Notebooks
Reads the control file to find download path, download period and spatial domain. Downloads data and makes log file.

### Python and shell scripts
Shell scripts read the control file to find download path, download period and spatial domain. They then call the relevant Python script with path, download year and spatial domain as input arguments. Python script downloads data. Shell script makes log files.


## Assumptions not specified in `control_active.txt`

- Downloads are of hourly data in monthly chunks. Requires changes to download scripts to adjust;
- Maximum number of parallel download jobs is set to 5. Requires minor changes to `run_download_[data]_annual.sh` to adjust.

## Download workflow
Data is provided in the GRIB2 format by ECMWF. A subset of the data can be found on the Climate Data Store (https://cds.climate.copernicus.eu/#!/home), which is interpolated to a lat/lon grid and available in netcdf format.

Steps to downloading ERA5 through CDS can be found here: https://confluence.ecmwf.int/display/CKB/How+to+download+ERA5
1. Make a CDS account
2. Create a .cdsapi file in $HOME/
3. Install the cdsapi (pip install --user cdsapi)
4. Run a python script with the download request

## Suggested citation
Copernicus Climate Change Service (C3S) (2017): ERA5: Fifth generation of ECMWF atmospheric reanalyses of the global climate . Copernicus Climate Change Service Climate Data Store (CDS), 2020-03-26. https://cds.climate.copernicus.eu/cdsapp#!/home