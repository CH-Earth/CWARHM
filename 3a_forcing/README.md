# Forcing data: ERA5 
The ERA5 product is a reanalysis data set. See documentation (link below) for details about which observations are used and how they are combined in the reanalysis. ERA5's forcing variables (called parameters in the ERA5 documentation) can be either instantaneous or time-step averages (see the data documentation). They are provided at various heights: surface and single level for every of the 137 air layers that ERA5 uses. 

## Forcing needed to run SUMMA
SUMMA needs the following forcing variables (https://summa.readthedocs.io/en/master/input_output/SUMMA_input/#meteorological-forcing-files):
- Precipitation rate [kg m-2 s-1]
- Downward shortwave radiation at the upper boundary [W m-2]
- Downward longwave radiation at the upper boundary [W m-2]
- Air pressure at the the measurement height [Pa]
- Air temperature at the measurement height [K]
- Wind speed at the measurement height [m s-1]
- Specific humidity at the measurement height [g g-1]

The upper boundary refers to the upper boundary of the SUMMA domain, so this would be at some height above the canopy or ground (in case there is no canopy). The measurement height is the height (above bare ground) where the meteorological variables are specified. This value is specified as `mHeight` in the local attributes file. SUMMA forcing time stamps are **period-ending** and the forcing information should reflect the **average conditions over the time interval** of length `data_step` preceding the time stamp.


## SUMMA needs vs ERA5 availability
Generally speaking, ERA5 data are available as hourly data for the period 1979 to current minus 5 days. This will be extended to cover the period 1950-1970. Spatial resolution of the data is a 31km grid over the Earth's surface.

ERA5 data preparation includes interactions between an atmospheric model and a land surface model. This model setup includes different layers and ERA5 data is available at 137 different pressure levels (i.e. some height above the surface), as well as at the surface. The lowest atmospheric level is L137, at geopotential and geometric altitude 10 m (https://www.ecmwf.int/en/forecasts/documentation-and-support/137-model-levels) and data here relies only on the atmospheric model. Any variables at a height lower than L137 (i.e. at the surface) are the result of interpolation between atmospheric model and land model. We want to use only the outcomes from the ECMWF atmospheric model, because in our setup SUMMA takes on the role of a land surface model. Therefore we obtain (1) air temperature, (2) wind speed and (3) specific humidity at the lowest pressure level (L137). (4) Precipitation, (5) downward shortwave radiation, (6) downward longwave radiation and (7) air pressure are unaffected by the land model coupling and can be downloaded at the surface level. This is beneficial because surface-level downloads are substantially faster than pressure-level downloads. For more information see:

- ERA5 hourly data on single levels from 1970 to present (https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview)
- ERA5 hourly data on pressure levels from 1970 to present (https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-pressure-levels?tab=overview)


## Download requirements
Downloading ERA5 data requires:
- Registration: https://cds.climate.copernicus.eu/user/register?destination=%2F%23!%2Fhome
- Setup of the `cdsapi`: https://cds.climate.copernicus.eu/api-how-to


## Workflow description
- 1_download: contains notebooks/scripts to download the necessary variables from ERA5's surface level and pressure level data sets;
- 2_merge: contains notebooks/scripts to merge the pressure and surface level data into a single file, and convert `u` and `v` wind components into a single vector;
- 3_create_shapefile: contains notebooks/scripts to make a shapefile for ERA5 data for later use.


### Surface-level variable downloads
We need the following ERA5 variables at the surface:
- Mean total precipitation rate [kg m-2 s-1]
- Mean surface downward short-wave radiation flux [W m-2]
- Mean surface downward long-wave radiation flux [W m-2]
- Surface pressure [Pa]

These variables can be downloaded straight through the CDS API (see template_ERA5_singleLevel.py; https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-pressure-levels?tab=form).


### Pressure-level variable downloads
We need the following variables at the lowest pressure level (L137) of the atmospheric model to run SUMMA:
- Temperature [K]
- Wind speed
    - U-component and V-component of wind speed [m s-1]
    - These will be converted into a directionless wind speed vector 
- Specific humidity [kg kg-1]

This is not directly available through the CDS API and must come from MARS instead (see template_ERA5_pressureLevel.py; https://confluence.ecmwf.int/display/CKB/How+to+download+ERA5#).

## Suggested citation
Copernicus Climate Change Service (C3S) (2017): ERA5: Fifth generation of ECMWF atmospheric reanalyses of the global climate. Copernicus Climate Change Service Climate Data Store (CDS), 2020-03-26. https://cds.climate.copernicus.eu/cdsapp#!/home

## Reference pages
- General description (last access 8-01-2020): https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5
- Difference with ERA_interim (last access 8-01-2020): https://confluence.ecmwf.int//pages/viewpage.action?pageId=74764925
- Product main page (last access 8-01-2020): http://climate.copernicus.eu/climate-reanalysis
- Documentation (last access 8-01-2020): https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation
- Download guide (last access 8-01-2020): https://confluence.ecmwf.int/display/CKB/How+to+download+ERA5