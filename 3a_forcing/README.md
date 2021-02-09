# Forcing data: ERA5 

The ERA5 product is a reanalysis data set. See documentation (link below) for details about which observations are used and how they are combined in the reanalysis. ERA5's forcing variables (called parameters in the ERA5 documentation) can be either instantaneous or time-step averages (see the data documentation). They are provided at various heights: surface and single level for every of the 137 air layers that ERA5 uses. 

## Code setup
### Notebooks
Calls the control file to find download path, download period and spatial domain. Downloads data and makes log file.

### Python and shell scripts
Shell scripts call the control file to find download path, download period and spatial domain. They then call the relevant Python script with path, download year and spatial domain as input arguments. Python script downloads data. Shell script makes log files.


## Assumptions not specified in `control_active.txt`

- Downloads are of hourly data in monthly chunks. Requires changes to download scripts to adjust;
- Maximum number of parallel download jobs is set to 5. Requires minor changes to `run_download_[data]_annual.sh` to adjust.


## Forcing needed to run SUMMA

SUMMA needs the following forcing variables (https://summa.readthedocs.io/en/master/input_output/SUMMA_input/#meteorological-forcing-files):
- Precipitation rate [kg m-2 s-1]
- Downward shortwave radiation at the upper boundary [W m-2]
- Downward longwave radiation at the upper boundary [W m-2]
- Air pressure at the the measurement height [Pa]
- Air temperature at the measurement height [K]
- Wind speed at the measurement height [m s-1]
- Specific humidity at the measurement height [g g-1]

The upper boundary refers to the upper boundary of the SUMMA domain, so this would be at some height above the canopy or ground (in case there is no canopy). The measurement height is the height (above bare ground) where the meteorological variables are specified. This value is specified as `mHeight` in the local attributes file. SUMMA forcing time stamps are **period-ending** and the forcing information reflects **average conditions over the time interval** of length data_step preceding the time stamp.

ERA5 data preparation includes interactions between an atmospheric model and a land surface model. This model setup includes different layers and ERA5 data is available at 137 different pressure levels (i.e. some height above the surface), as well as at the surface. The lowest atmospheric level is L137, at geopotential and geometric altitude 10 m (https://www.ecmwf.int/en/forecasts/documentation-and-support/137-model-levels) and data here relies only on the atmospheric model. Any variables at a height lower than L137 (i.e. at the surface) are the result of interpolation between atmospheric model and land model. We want to use only the outcomes from the ECMWF atmospheric model, because in our setup SUMMA takes on the role of a land surface model. Therefore we obtain (1) air temperature, (2) wind speed and (3) specific humidity at the lowest pressure level (L137). (4) Precipitation, (5) downward shortwave radiation, (6) downward longwave radiation and (7) air pressure are unaffected by the land model coupling and can be downloaded at the surface level. This is beneficial because surface-level downloads are substantially faster than pressure-level downloads.


## ERA5 availability

Generally speaking, ERA5 data are available as hourly data for the period 1979 to current minus 5 days. This will be extended to cover the period 1950-1970. Spatial resolution of the data is a 31km grid over the Earth's surface. As mentioned, the workflow uses both surface-level and pressure-level data:

- ERA5 hourly data on single levels from 1970 to present (https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview)
- ERA5 hourly data on pressure levels from 1970 to present (https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-pressure-levels?tab=overview)

### Surface-level variables

We need the following ERA5 variables at the surface:
- Mean total precipitation rate [kg m-2 s-1]
- Mean surface downward short-wave radiation flux [W m-2]
- Mean surface downward long-wave radiation flux [W m-2]
- Surface pressure [Pa]

These variables can be downloaded straight through the CDS API (see template_ERA5_singleLevel.py; https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-pressure-levels?tab=form).


### Pressure-level variables

We need the following variables at the lowest pressure level (L137) of the atmospheric model to run SUMMA:
- Temperature [K]
- Wind speed
    - U-component and V-component of wind speed [m s-1]
    - These will be converted into a directionless wind speed vector 
- Specific humidity [kg kg-1]

This is not directly available through the CDS API and must come from MARS instead (see template_ERA5_pressureLevel.py; https://confluence.ecmwf.int/display/CKB/How+to+download+ERA5#).


## Downloading ERA5
Data is provided in the GRIB2 format by ECMWF. A subset of the data can be found on the Climate Data Store (https://cds.climate.copernicus.eu/#!/home), which is interpolated to a lat/lon grid and available in netcdf format.

Steps to downloading ERA5 through CDS can be found here: https://confluence.ecmwf.int/display/CKB/How+to+download+ERA5
1. Make a CDS account
2. Create a .cdsapi file in $HOME/
3. Install the cdsapi (pip install --user cdsapi)
4. Run a python script with the download request

See the two template_ERA5_[type].py files.


## Suggested citation
Copernicus Climate Change Service (C3S) (2017): ERA5: Fifth generation of ECMWF atmospheric reanalyses of the global climate . Copernicus Climate Change Service Climate Data Store (CDS), 2020-03-26. https://cds.climate.copernicus.eu/cdsapp#!/home


## Reference pages
- General description (last access 8-01-2020): https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5
- Difference with ERA_interim (last access 8-01-2020): https://confluence.ecmwf.int//pages/viewpage.action?pageId=74764925
- Product main page (last access 8-01-2020): http://climate.copernicus.eu/climate-reanalysis
- Documentation (last access 8-01-2020): https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation
- Download guide (last access 8-01-2020): https://confluence.ecmwf.int/display/CKB/How+to+download+ERA5




#### Single levels data lets us get the data at the surface
We also want the following for possible future analyses:
- Mean large-scale precipitation rate [kg m-2 s-1]
- Mean convective precipitation rate [kg m-2 s-1]
- Mean large-scale snowfall rate [kg m-2 s-1]
- Mean convective snowfall rate [kg m-2 s-1]




## Misc notes

### Discrepancies between SUMMA and ERA5
Overview of mismatch between what SUMMA needs, what ERA5 can give us and what Martyn says should work.

- Downward shortwave radiation at upper boundary. ERA5 gives values at the surface, but surface is not necesarrily the land surface. Could be the top of their vegetation or something else. MPC: we can use ERA5 as SUMMA input directly
- Downward longwave radiation at upper boundary. See shortwave radiation
- For temperature, wind speed and specific humidty, it's easiest/best to take all of these from the same, **lowest** pressure level in the data
- We might need to do some time step averaging in cases where we get instantaneous data (SUMMA requires averages)


### Wind speed scaling from 10m to 2m
First coverted to a single vector: w = sqrt(u^2 + v^2).
Then converted to 2m wind speed using a log profile (Allen et al, 1998):

u2 = u(z) * 4.87 / ln(67.8z - 5.42)

u2 = u10  * 4.87 / ln(67.8\*10 - 5.42) 


### Specific humidity calculation
Based on 2m dewpoint and surface pressure (Stull, 2012): 

e = 6.112 \* exp((17.67*2*T_dew) / (2\*T_dew + 243.5))

spechum = (0.622 * e)  / (pres - (0.378 * e))

### Abbas' notes on air pressure
Air pressure: Abbas recommends Eq. 2 in Dodson and Marks (1997; downloaded and in Mendeley) to get air pressure. 
Specific humidity: Abbas recommends the Dingman (2014) book for conversion between this and relative humidity; there also other equations for specific environments; see also Kunkel (1988; downloaded and in Mendeley)


### Abbas' code based on Dingman
#2.1b. compute es the saturated vapor pressure (e*) in [mb] after Dingman (2014) [Pa] Ta = Air temperature [C]

#there are two forms of the equation (here using the one for T >= 0)

es <- 611*exp((17.27*(Ta))/(Ta+237.3))  # after Dingman (2014) [Pa]

#for T < 0 use

es <- 611*exp((21.87*(Ta))/(Ta+265.5))  # after Dingman (2014) [Pa]

#2.2. compute ea the (actual vapor pressure), [Pa]; inputs es = e* [Pa], RH [Ratio]

ea <- es*RH/100

#2.3 compute qa the (specific humidity) (q) [kg kg-1]

qa <- 0.622*ea/ph # Dingman 2014 p.113 eq.(3.11)


### References
Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998). Crop evapotranspiration - Guidelines for computing crop water requirements - FAO Irrigation and drainage paper 56. Rome.

Stull, R. (2012). Practical Meteorology - An Algebra-based Survey of Atmospheric Science Titel Page. In Practical Meteorology - An Algebra-based Survey of Atmospheric Science. Retrieved from http://www.eos.ubc.ca/books/Practical_Meteorology/
