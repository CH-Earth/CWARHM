# ERA5 data merger
Creates a single monthly `.nc` file with SUMMA-ready variables for further processing. Combines ERA5's `u` and `v` wind components into a single directionless wind vector. 

## Description
We downloaded separate ERA5 data at pressure level 137 and the surface. We want all the forcing aggregated into a single file and to be in the right units for SUMMA (ERA5 units are already OK for use in SUMMA):
- Precipitation as 'pptrate' in [kg m\*\*-2 s**-1]
- Air pressure at measurement height (assumed to be equivalent to air pressure at the surface) as 'airpres' in [Pa]
- Downward shortwave radiation as 'SWRadAtm' in [W m**-2]
- Downward longwave radiation as 'LWRadAtm' in [W m**-2]
- Temperature at measurement height as '' in [K]
- Specific humidity at measurement height as 'spechum' in [g g**-1]
- Wind speed at measurement height as '' in [m s**-1]
 
The ERA5 data are split out over two files, that each contain hourly data for a given combination of year and month. Files named 'ERA5_surface\_[yyyymm].nc' contain variables at the surface:
- precipitation ('mtpr'), 
- surface pressure ('sp'), 
- mean surface downward shortwave radiation ('msdwswrf')
- mean surface downward longwave radiation('msdwlwrf') 
 
Files named 'ERA5_pressureLevel137\_[yyymm].nc' contain variables at at the lowest pressure level of the atmospheric model (10m):
- temperature ('t'),
- specific humidity ('q')
- u-component of wind speed ('u')
- v-component of wind speed ('v')
 
This script goes through the following steps:
1. Convert longitude coordinates in pressureLevel file to range [-180,180]
2. Checks
- are lat/lon the same for both data sets?
- are times the same for both datasets?
3. Aggregate data into a single file 'ERA5_NA_[yyyymm].nc', keeping the relevant metadata in place

## Assumptions not included in `control_active.txt`
Code assumes it operates on the same years that were downloaded, contained in field `forcing_raw_time` in the control file. To merge only a subset of these files, change the specification of the `years` variable.