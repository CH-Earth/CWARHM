# SUMMA settings
Creates all input files needed to run SUMMA:
- `0_base_settings` includes those files that initially do not require any geospatial information or user paths;
- `1_topo` includes scripts to map the prepared geospatial data (DEM, soil classes, vegetation types) to Hydrologic Response Units (HRUs);
- `2_forcing` includes scripts to map ERA5 gridded forcing to HRUs, apply temperature lapse rates and finalize the forcing `.nc` files for use by SUMMA;
- `3a_copy_base_settings` includes a script to move the base settings from their folder here to the experiment's settings folder;
- `3b_file_manager` includes a script that creates a `fileManager.txt` file for this experiment. This file defines where SUMMA can find its input data, which time period to simulate and where to save its simulations;
- `3c_forcing_file_list` includes a script that specifies the names of the `.nc` files that contain forcing data;
- `3d_initial_conditions` includes a script to create a basic initial conditions file;
- `3e_trial_parameters` includes a script that generates an empty trial parameters file. In a typical setup, this file can be used to overwrite the default values of any parameter. For this initial setup, no parameters will be overwritten;
- `3f_attributes` includes a script that creates an HRU attributes file. This file contains a variety of HRU-level information, such as the HRUs' latitude and longitude, elevation and geospatial characteristics.

The description of these files is purposely kept short, because this information is available in much greater detail in the SUMMA docs: https://summa.readthedocs.io/en/latest/input_output/SUMMA_input/

## Control file settings
This section lists all the settings in `control_active.txt` that the code in this folder uses.
- **settings_summa_path**: location where the SUMMA settings need to go
- **settings_summa_filemanager, settings_summa_coldstate, settings_summa_attributes, settings_summa_trialParams, settings_summa_forcing_list**: names of SUMMA configuration files
- **experiment_id, experiment_time_start, experiment_time_end**: name and simulation period of the experiment
- **forcing_summa_path**: path were the SUMMA-ready forcing data can be found
- **experiment_output_summa**: output path for the SUMMA simulations
- **forcing_time_step_size**: size of the forcing time step
- **forcing_measurement_height**: height above surface were forcing data is estimated/measured
- **catchment_shp_path, catchment_shp_name, catchment_shp_hruid, catchment_shp_gruid, catchment_shp_area, catchment_shp_lat, catchment_shp_lon**: location of catchment shapefile and the names of its columns
- **intersect_soil_path, intersect_soil_name, intersect_land_path, intersect_land_name, intersect_dem_path, intersect_dem_name**: location of the intersections between catchment shapefile and preprocessed geospatial parameter fields 
