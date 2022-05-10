# Make the initial folder structure
Both notebook and Python script need to be modified to point to the right control file. When executed, both will copy this control file into `control_active.txt` and create the basic folder structure on the path specified in the control file. In particular, this creates folders for the catchment and river network shapefiles that are needed for subsequent steps. The user must manually copy the `.shp` files into these directories.

## Shapefile folder overview
### (SUMMA) Catchment
A shapefile outlining the catchment should be placed in this folder. The shapefile must:
- Have the geometry of the basin(s) and sub-basin(s);
- Have its Coordinate Reference System (CRS) set to regular lat/long (WGS84, EPSG:4326);
- Include a column with numeric Grouped Response Unit (GRU) identifiers;
- Include a column with unique numeric Hydrologic Response Unit (HRU) identifiers;
- Include a column with HRU area in [m^2];
- Include a column with HRU centroid (latitude);
- Include a column with HRU centroid (longitude).

Names of each column must be specified in the control file. Note that HRU IDs must be unique. GRU IDs need not be, because multiple HRUs can be defined within a single GRU. 


### (mizuRoute) River network
A shapefile outlining the river network (i.e. the stream segments) should be placed in this folder. The shapefile must:
- Have the geometry of the river network;
- Have its Coordinate Reference System (CRS) set to regular lat/long (WGS84, EPSG:4326);
- Include a column with unique numeric stream segment identifiers;
- Include a column with the segment IDs of the downstream segment each segment connects to. The network outlet must have a downstream ID too but this can be any value;
- Include a column with segment slope [-];
- Include a column with segment length [m].

In a basic model setup, it is assumed that the stream segments have a surrounding basin that maps 1:1 onto SUMMA's GRUs. If this is not the case and the drainage basins used for routing do not map directly onto the SUMMA GRUs, a river basins shapefile needs to be provided as well. See below.


### (mizuRoute) River basins
Including this file is **_optional_** and is only required in cases where the catchment delineation of SUMMA's GRUs is different from the basins that are delineated as part of the routing network. In such cases, a shapefile outlining the river routing basins (i.e. the drainage area of each stream catchment) should be placed in this folder. The shapefile must:
- Have the geometry of the river routing basins;
- Have its Coordinate Reference System (CRS) set to regular lat/long (WGS84, EPSG:4326);
- Include a column with unique numeric Hydrologic Response Unit (HRU) identifiers;
- Include a column with HRU area in [m^2];
- Include a column with the stream segment ID (as specified in the river network shapefile) that each routing HRU drains into.

Note that the HRUs mentioned here are distinctly different entities than the HRUs that are defined as part of the (SUMMA) catchment shapefile. If routing basins differ from the SUMMA GRUs, make sure to set the control file option `river_basin_needs_remap` to `yes`.


## Control file settings
This section lists all the settings in `control_active.txt` that the code in this folder uses.
- **root_path**: main path where data needs to go.
- **domain_name**: name of the modelling domain that will be used to create a dedicated domain_[domain_name] subfolder in root_path.
- **catchment_shp_path, river_network_shp_path, river_basin_shp_path**: paths where the domain shapefiles need to go. Default settings will automatically generate these folder in root_path/domain_[domain_name]/shapefiles 