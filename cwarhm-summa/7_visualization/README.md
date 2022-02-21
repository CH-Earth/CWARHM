# Visualization scripts
--- Work in progress ---

Will contain scripts used to produce paper plots. Will also contain general examples of useful plots.

## 1_mizuRoute_and_summa_shapefiles
Overview figure of mizuRoute routing basins and river network on one side, and SUMMA GRUs and HRUs on the other.

## 2_ERA5_download_coordinates_and_catchment_shapefile
Figure used to check if conversion of bounding box found in `control_active.txt` to ERA5 download coordinates works as it should.

## HRU_mean_streamflow
Mean annual routed streamflow per stream segment, with elevation of each SUMMA HRU as background. Uses water years.

## HRU_mean_SWE
Mean HRU elevation and mean maximum annual SWE per HRU. Uses water years. Also contains some testing code to check temporal evoluation of SWE and temperature, to confirm that applied lapse rates make sense.

## SWE_and_streamflow_per_HRU
Mean annual routed streamflow per stream segment, with mean annual maximum SWE of each SUMMA HRU as background. Uses water years.