import os
import shutil
import sys

#%%
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from pathlib import Path
from cwarhm.wrappers import cwarhm_summa as fm
from cwarhm.model_specific_processing import mizuroute as mzr
from cwarhm.data_specific_processing import era5
from cwarhm.data_specific_processing import merit
import cwarhm.util.util as utl

os.chdir(os.path.dirname(os.path.realpath(__file__)))
cwarhm_summa_folder = os.path.abspath("../../dependencies/cwarhm-summa")

### SETTINGS
test_data_path = Path("/Users/localuser/Research/summaWorkflow_data/domain_BowAtBanff")
# set control file to use
control_options = utl.read_summa_workflow_control_file('control_Bow_at_Banff_test.txt')
# copy control file to cwarhm summa folder
fm.change_control_file_in_submodule(cwarhm_summa_folder, 'control_Bow_at_Banff_test.txt')
# set path where results go
results_folder_path = control_options['root_path'] + '/domain_' + control_options['domain_name']

reset_test = False
if reset_test:
    ## manage context of test: copy test data to required folder
    # remove results folder if exists
    if os.path.exists(results_folder_path):
        shutil.rmtree(results_folder_path)
    # create results folder
    # copy test_data to results folder as in mwah results and previous result share the same root folder (by default)

    shutil.copytree(test_data_path, results_folder_path)
    fm.create_folder_structure(cwarhm_summa_folder)

#%% start example
#%% download data (downloads not included in example) - data specific input layer - part 1
## data can be downloaded by the test_data_download.py script.


#%% process downloaded data - data specific input layer - part 2

### forcing ERA5 ###

era5.merge_era5_surface_and_pressure_level_downloads(control_options['forcing_raw_path'], control_options['forcing_merged_path'], control_options['forcing_raw_time'])
# fm.merge_forcing(cwarhm_summa_folder, control_options['forcing_raw_time']) # replaced by functions from era5

fm.create_ERA5_shapefile(cwarhm_summa_folder)

## merit hydro ##
fm.unpack_merit_hydro(cwarhm_summa_folder)
fm.create_merit_hydro_virtual_dataset(cwarhm_summa_folder)
fm.specify_merit_hydro_subdomain(cwarhm_summa_folder)
fm.convert_merit_hydro_vrt_to_tif(cwarhm_summa_folder)

## MODIS ##
fm.create_modis_virtual_dataset(cwarhm_summa_folder)
fm.reproject_modis_virtual_dataset(cwarhm_summa_folder)
fm.specify_modis_subdomain(cwarhm_summa_folder)
fm.create_multiband_modis_vrt(cwarhm_summa_folder)
fm.convert_modis_vrt_to_tif(cwarhm_summa_folder)
fm.find_mode_modis_landclass(cwarhm_summa_folder)

## SOILGRIDS ##
fm.extract_soilgrids_domain(cwarhm_summa_folder)

#%% model agnostic mapping layer
fm.sort_catchment_shape(cwarhm_summa_folder)

fm.find_HRU_elevation(cwarhm_summa_folder) 
fm.find_HRU_land_classes(cwarhm_summa_folder)
#%%
fm.find_HRU_soil_classes(cwarhm_summa_folder) 

#%%
fm.make_single_weighted_forcing_file(cwarhm_summa_folder)
fm.make_all_weighted_forcing_files(cwarhm_summa_folder)
fm.temperature_lapsing_and_datastep(cwarhm_summa_folder)

#%% Model specific processing layer
## Build repo clones and compile
fm.clone_summa_repo(cwarhm_summa_folder)
fm.clone_mizuroute_repo(cwarhm_summa_folder)

## Compiling needs adjustment for local OS
##fm.compile_summa(cwarhm_summa_folder)
##fm.compile_mizuroute(cwarhm_summa_folder)

## mizuRoute ##
fm.copy_mizuroute_base_settings(cwarhm_summa_folder)
mzr.generate_mizuroute_topology(control_options['river_network_shp_path'], control_options['river_basin_shp_path'],
    os.path.join(control_options['settings_mizu_path'],control_options['settings_mizu_topology']),
    control_options['settings_mizu_make_outlet'])
fm.create_mizuroute_network_topology_file(cwarhm_summa_folder)

fm.remap_summa_catchments_to_mizurouting(cwarhm_summa_folder)
fm.create_mizuroute_control_file(cwarhm_summa_folder)

#%%
## SUMMA ##
fm.copy_summa_base_settings(cwarhm_summa_folder)
fm.create_summa_file_manager(cwarhm_summa_folder)
fm.create_summa_forcing_file_list(cwarhm_summa_folder)
fm.create_summa_cold_state(cwarhm_summa_folder)
fm.create_summa_trial_parameters(cwarhm_summa_folder)
fm.initialize_summa_attributes_nc(cwarhm_summa_folder)
fm.insert_soilclass_from_hist_into_summa_attributes(cwarhm_summa_folder)
fm.insert_landclass_from_hist_into_summa_attributes(cwarhm_summa_folder)
fm.insert_elevation_from_hist_into_summa_attributes(cwarhm_summa_folder)

#%% run models
## Note that models need to be compiled

#fm.run_summa(cwarhm_summa_folder)
#fm.run_mizuroute(cwarhm_summa_folder)

#%% evaluate models
#fm.plot_mizuroute_and_summa_shapefiles(cwarhm_summa_folder)
#fm.plot_ERA5_download_coordinates_and_catchment_shapefile(cwarhm_summa_folder)
#fm.plot_geospatial_parameters_to_model_elements(cwarhm_summa_folder)
#fm.plot_SWE_and_streamflow_per_HRU(cwarhm_summa_folder)
#fm.plot_forcing_grid_vs_catchment_averaged(cwarhm_summa_folder)
## fm.plot_SWE_SM_ET_Q_per_GRU(cwarhm_summa_folder) not all data local!
## fm.plot_temperature_lapse_rates(cwarhm_summa_folder) not all data local!