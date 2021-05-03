# ERA5 invariant data
Downloads various auxiliary data, such as land mask and geopotential for ERA5 data. We currently only use geopotential (parameter download ID 129) to estimate ERA5 elevation and use this to define temperature lapse rates.

Source: https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation#ERA5:datadocumentation-Parameterlistings


## Download setup instructions
Downloading ERA5 data requires:
- Registration: https://cds.climate.copernicus.eu/user/register?destination=%2F%23!%2Fhome
- Setup of the `cdsapi`: https://cds.climate.copernicus.eu/api-how-to

## Download run instructions
Execute the download script and keep the terminal or notebook open until the downloads fully complete. No manual interaction with the https://cds.climate.copernicus.eu/ website is required.

## Levels
These variables are available to surface and pressure levels. We need them to set up SUMMA so we'll use the surface level variables, because those correspond to ground surface.

## Time
These parameters are invariant in time, so we can select any time we need for them (see section "Parameter listings", Table 1 on: https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation).

## Geopotential to elevation
We use the geopotential given for each ERA5 data point to estimate the elevation at this data point: "at the surface of the Earth, this parameter shows the variations in geopotential (height) of the surface, and is often referred to as the orography." To do so, we need to divide geopotential by gravitational acceleration (https://apps.ecmwf.int/codes/grib/param-db?id=129): `g = 9.80665 m s-2'. This step is performed during the preparation of SUMMA inputs.

## Assumptions not specified in `control_active.txt`
- Name of the download file hard-coded as `ERA5_geopotential.nc`.

