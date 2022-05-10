# Forcing data download
Downloads ERA5 forcing data (surface and pressure level variables) for the domain specified in the control file. Note that downloads of surface level and pressure level data are retrieved from two different types of data storage on the ECMWF side. Different restrictions may apply to both storage types at any given time and downloads of surface and pressure level data are typically not equally fast. 


## Notebooks vs Python and shell scripts
Notebooks are set up for serial downloads, Python and shell scripts together run downloads in parallel. Notebooks read the control file to find download path, download period and spatial domain. Downloads data and makes log file. Shell scripts read the control file to find download path, download period and spatial domain. They then call the relevant Python script with path, download year and spatial domain as input arguments using the `parallel` command line utility. The code in the python scripts downloads the data, after which the shell scripts write simple log files. Note that ECMWF sometimes restricts data access to the ERA5 data (e.g. only 1 connection per user may be allowed). In such cases parallelization on the user's side will not speed up the downloads.


## Download setup instructions
Downloading ERA5 data requires:
- Registration: https://cds.climate.copernicus.eu/user/register?destination=%2F%23!%2Fhome
- Setup of the `cdsapi`: https://cds.climate.copernicus.eu/api-how-to


## Download run instructions
Execute the download script and keep the terminal or notebook open until the downloads fully complete. No manual interaction with the https://cds.climate.copernicus.eu/ website is required.


## Download workflow
Data is provided in the GRIB2 format by ECMWF. A subset of the data can be found on the Climate Data Store (https://cds.climate.copernicus.eu/#!/home), which is interpolated to a lat/lon grid and available in netcdf format.

Steps to downloading ERA5 through CDS can be found here: https://confluence.ecmwf.int/display/CKB/How+to+download+ERA5
1. Make a CDS account
2. Create a .cdsapi file in $HOME/
3. Install the cdsapi (pip install --user cdsapi)
4. Run the scripts/notebooks to download data


## Assumptions not specified in `control_active.txt`
- Downloads are of hourly data in monthly chunks. Requires changes to download scripts to adjust;
- Maximum number of parallel download jobs is set to 5. Requires minor changes to `run_download_[data]_annual.sh` to adjust.


## Suggested data citation
Copernicus Climate Change Service (C3S) (2017): ERA5: Fifth generation of ECMWF atmospheric reanalyses of the global climate. Copernicus Climate Change Service Climate Data Store (CDS), 2020-03-26. https://cds.climate.copernicus.eu/cdsapp#!/home