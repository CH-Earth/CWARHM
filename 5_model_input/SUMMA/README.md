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