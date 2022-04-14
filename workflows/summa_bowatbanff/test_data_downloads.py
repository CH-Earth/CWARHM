import os
from pathlib import Path
import shutil
import sys

#%%
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from cwarhm.wrappers import cwarhm_summa as fm
from cwarhm.model_specific_processing import mizuroute as mzr
from cwarhm.data_specific_processing import era5
from cwarhm.data_specific_processing import merit
import cwarhm.util.util as utl

os.chdir(os.path.dirname(os.path.realpath(__file__)))

#%% start example
# read control file to use with functions
control_options = utl.read_summa_workflow_control_file('control_Bow_at_Banff_test.txt')
utl.build_folder_structure(control_options)

#%% download data (downloads not included in example) - data specific input layer - part 1
## the lines below are included if the test data is not available locally

## ERA5
# TODO: fix parallelization issue, runs whole script in paralell
bbox = [float(i) for i in control_options['forcing_raw_space'].split('/')]
#years = utl.unpack_year_range(control_options['forcing_raw_time'])
#era_5_raw_data_path = control_options['forcing_raw_path']
#era5.run_era5_download_in_parallel(years,bbox,era_5_raw_data_path,'surface_level')
#era5.run_era5_download_in_parallel(years,bbox,era_5_raw_data_path,'pressure_level')

## MERIT DEM
# TODO: check bbox... hopefully the same as for ERA5...
merit_raw_folder = control_options['parameter_dem_raw_path']
credentials = utl.read_merit_credentials_file()
merit.download_merit(merit_raw_folder, credentials, ['elv'], bbox=bbox)

## fm.download_modis_mcd12q1_v6(cwarhm_summa_folder)
## fm.download_soilgrids_soilclass_global(cwarhm_summa_folder)