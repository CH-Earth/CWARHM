# Make the initial folder structure
Both notebook and Python script need to be modified to point to the right control file. When executed, both will copy this control file into `control_active.txt` and create the basic folder structure on the path specified in the control file. In particular, this creates folders for the catchment and river network shapefiles (`.shp`) that are needed for subsequent steps. The user must manually copy their shapefiles files into these directories.


## Control file settings
This section lists all the settings in `control_active.txt` that the code in this folder uses.
- **root_path**: main path where data needs to go.
- **domain_name**: name of the modelling domain that will be used to create a dedicated domain_[domain_name] subfolder in root_path.
- **catchment_shp_path, river_network_shp_path, river_basin_shp_path**: paths where the domain shapefiles need to go. Default settings will automatically generate these folder in root_path/domain_[domain_name]/shapefiles 