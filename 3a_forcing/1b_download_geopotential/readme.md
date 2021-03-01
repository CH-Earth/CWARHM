# ERA5 invariants
Downloads various auxiliary data, such as land mask and geopotential for ERA5 data. We currently only use geopotential (parameter download ID 129).

Source: https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation#ERA5:datadocumentation-Parameterlistings

## Levels
These variables are available to surface and pressure levels. We need them to set up SUMMA so we'll use the surface level variables, because those correspond to ground surface.

## Time
These parameters are invariant in time, so we can select any time we need for them (see section "Parameter listings", Table 1 on: https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation).

## Geopotential to elevation
Divide by gravitational acceleration: https://apps.ecmwf.int/codes/grib/param-db?id=129
`g = 9.80665 m s-2'

"At the surface of the Earth, this parameter shows the variations in geopotential (height) of the surface, and is often referred to as the orography."

