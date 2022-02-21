# Parameters
SUMMA requires certain inputs that need to be derived from geospatial data fields. Here we obtain and pre-process:
- Merit-Hydro digital elevation model (DEM) data;
- SOILGRIDS soil properties data;
- MODIS vegetation properties data.

## Elevation
Elevation data are needed to compare the elevation of each model element to that elevation of the forcing grid that we use as model input. The difference between both is used to apply lapse rates to air temperature data, to approximate temperature gradients based on altitude.

## Soil properties
SUMMA uses a lookup table approach to find values for certain soil parameters. Soils are divided into different categories. A representative soil category per model elements is derived from SOILGRIDS maps that show sand, silt and clay percentages.

## Vegetation properties
SUMMA uses a lookup table approach to find values for certain vegetation parameters. Vegetation cover is divided into different categories. MODIS data provides vegetation classes as per the IGBP classification, which lets us find a representative vegetation type per model element.