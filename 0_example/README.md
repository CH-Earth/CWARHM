# Example data
This folder contains example shapefiles that can be used to reproduce the Bow at Banff case presented in the paper that describes this workflow. Shapefiles are derived from the MERIT Hydro basins (Lin et al., 2019). The Bow at Banff example case is a SUMMA setup that has 51 Grouped Response Units (GRUs) that are subdivided into 118 Hyrdrologic Response Units (HRUs) total.

## Shapefiles used for Bow at Banff
The following shapefiles are the basis of the Bow at Banff setup:
1. For SUMMA: a shapefile outlining the subcatchments (GRUs) of the Bow River up to Banff, and how these GRUs are subdivided into Hydrologic Response Units (HRUs) by elevation bands;
2. For mizuRoute: a shapefile that shows the routing basins. In this case these are identical to the SUMMA GRUs. This means that no routing remapping file is needed (see mizuRoute setup code for details about the remapping file). This also means that the IDs of the routing basins **_must be identical_** to the IDs assigned to the SUMMA GRUs. If these are not identical, mizuRoute will not be able to find the data for each routing basin in the SUMMA output files.
3. For mizuRoute: a shapefile that shows the river network that connects the routing basins. 


## Shapefile requirements
Each shapefile needs to contain certain bits of information in addition to the shape geometry. These are described below. Column names for variables are arbitrary and must be specified in the workflow control file. All shapefiles are expected to be in regular lat/lon format, also known as `EPSG:4326` and `WGS84`.


### Catchment shapefile
A shapefile that shows which basins will be SUMMA's Grouped Response Units (GRUs) and optionally how the GRUs are divided into Hydrologic Response Units (HRUs). Also needs centroid latitude and longitude and HRU area:

| Name in example file | Variable              | Units  | Control file variable | 
|----------------------|-----------------------|--------|-----------------------|
| GRU_ID               | GRU identifier        | -      | catchment_shp_gruid   |
| HRU_ID               | Unique HRU identifier | -      | catchment_shp_hruid   |
| center_lat           | Centroid latitude     | degree | catchment_shp_lat     |
| center_lon           | Centroid longitude    | degree | catchment_shp_lon     |
| HRU_area             | Area of each HRU      | m^2    | catchment_shp_area    |

Note: centroid location and area should be calculated in an equal-area projection such as `EPSG:6933` for accuracy. Centroid points then need to be converted to lat/lon.


### River network shapefile
A shapefile that shows the river network that connects the routing basins. Also needs river segment slope and length:

| Name in example file | Variable                  | Units  | Control file variable       | 
|----------------------|---------------------------|--------|-----------------------------|
| COMID                | Stream segment identifier | -      | river_network_shp_segid     |
| NextDownID           | ID of downstream segment  | -      | river_network_shp_downsegid |
| slope                | Stream segment mean slope | -      | river_network_shp_slope     |
| length               | Stream segment length     | m      | river_network_shp_length    |


### Routing basin shapefile
A shapefile that shows the routing basins. Routing basins in the Bow at Banff case are identical to SUMMA GRUs. Also needs routing basin area and the ID of the stream segment the basin connects to:

| Name in example file | Variable                              | Units  | Control file variable       | 
|----------------------|---------------------------------------|--------|-----------------------------|
| COMID                | Routing basin identifier              | -      | river_basin_shp_rm_hruid    |
| area                 | Area of each routing basin            | m^2    | river_basin_shp_area        |
| hru_to_seg           | Stream segment each basin connects to | -      | river_basin_shp_hru_to_seg  |


Note 1: technically, in this case it would be possible to merge the SUMMA-catchment shapefile with the mizuRoute-basin shapefile, effectively adding the column `hru_to_seg` to the SUMMA shape. The workflow example uses separate files for clarity.

Note 2: mizuRoute only uses the concept of HRUs in constrast to SUMMA's use of both GRUs and HRUs. In most setups, it makes sense to define SUMMA's GRUs as equal to mizuRoute HRUs, and let SUMMA worry about the routing inside each of the SUMMA-GRUs. The workflow setup code makes this assumption and **_cannot_** be used to create a mizuRoute setup that runs routing between SUMMA's HRUs (e.g. in the Bow at Banff case this would refer to routing between the different elevation bands) - SUMMA should and does handle this.


## References
Lin, P., M. Pan, H. E., Beck, Y. Yang, D. Yamazaki, R. Frasson, C. H. David, M. Durand, T. M. Pavelsky, G. H. Allen, C. J. Gleason, and E. F. Wood, 2019: Global reconstruction of naturalized river flows at 2.94 million reaches. Water Resources Research, doi:10.1029/2019WR025287.
