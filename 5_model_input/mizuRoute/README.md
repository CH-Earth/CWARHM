# mizuRoute settings
Creates all input files needed to run mizuRoute:
- `0_base_settings` includes the parameter file that does not require any geospatial information or user paths;
- `1a_copy_base_settings` includes a script to move the base settings from their folder here to the experiment's settings folder;
- `1b_network_topology_file` includes a script that creates a network toplogy file. This file contains geospatial information for each routing basin and stream segment;
- `1c_optional_remapping_file` includes a script that can be used to generate a file that tells mizuRoute how to remap SUMMA output (from SUMMA GRUs) to routing basins that have different spatial extents than the SUMMA GRUs. mizuRoute can do this remapping internally if required. This script can be skipped for model setups in which the SUMMA GRUs map 1:1 onto the mizuRoute Routing basins;
- `1d_control_file` includes a script that creates a `.control` file for this experiment. This file defines where mizuRoute can find its input data, which time period to do the routing for, where to save its simulations and several other settings.

The description of these files is purposely kept short, because this information is available in much greater detail in the mizuRoute docs: https://mizuroute.readthedocs.io/en/master/Intro.html

## Control file settings
This section lists all the settings in `control_active.txt` that the code in this folder uses.
- **settings_mizu_path**: location where the mizuRoute settings need to go
- **settings_mizu_topology, settings_mizu_remap, settings_mizu_control_file**: names of the mizuRoute configuration files
- **river_network_shp_path, river_network_shp_name**: location of the river network shapefile
- **river_network_shp_segid, river_network_shp_downsegid, river_network_shp_slope, river_network_shp_length**: names of the river network shapefile columns
- **river_basin_shp_path, river_basin_shp_name**: location of the routing basins shapefile
- **river_basin_shp_rm_hruid, river_basin_shp_area, river_basin_shp_hru_to_seg**: names of the routing basins shapefile columns
- **settings_mizu_make_outlet**: river reaches to be treated as network outlets
- **intersect_routing_path, intersect_routing_name**: location where the intersection between hydrologic model catchments and routing basins needs to go
- **settings_mizu_routing_var, settings_mizu_routing_units, settings_mizu_routing_dt, settings_mizu_output_vars, settings_mizu_output_freq, settings_mizu_within_basin, experiment_output_summa, experiment_output_mizuRoute, experiment_time_start, experiment_time_end**: routing settings 
