# mizuRoute settings
Creates all input files needed to run mizuRoute:
- `0_base_settings` includes the parameter file that does not require any geospatial information or user paths;
- `1a_copy_base_settings` includes a script to move the base settings from their folder here to the experiment's settings folder;
- `1b_network_topology_file` includes a script that creates a network toplogy file. This file contains geospatial information for each routing basin and stream segment;
- `1c_optional_remapping_file` includes a script that can be used to generate a file that tells mizuRoute how to remap SUMMA output (from SUMMA GRUs) to routing basins that have different spatial extents than the SUMMA GRUs. mizuRoute can do this remapping internally if required. This script can be skipped for model setups in which the SUMMA GRUs map 1:1 onto the mizuRoute Routing basins;
- `1d_control_file` includes a script that creates a `.control` file for this experiment. This file defines where mizuRoute can find its input data, which time period to do the routing for, where to save its simulations and several other settings.

The description of these files is purposely kept short, because this information is available in much greater detail in the mizuRoute docs: https://mizuroute.readthedocs.io/en/master/Intro.html