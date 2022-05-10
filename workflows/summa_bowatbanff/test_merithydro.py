import os

from pathlib import Path
import shutil
import sys

#%%
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import cwarhm.util.util as utl
from cwarhm.wrappers import cwarhm_summa as fm
import cwarhm.data_specific_processing.merit as merit

os.chdir(os.path.dirname(os.path.realpath(__file__)))
cwarhm_summa_folder = "/Users/ayx374/Documents/GitHub/forks/summaWorkflow_public/dependencies/cwarhm-summa"
#cwarhm_summa_folder = "./dependencies/cwarhm-summa"
results_folder_path = Path("/Users/ayx374/Documents/project/chwarm_test_results/domain_BowAtBanff")
test_data_path = Path("/Users/ayx374/Documents/project/chwarm_test_data/domain_BowAtBanff")

# set control file to use with wrappers
fm.change_control_file_in_submodule(cwarhm_summa_folder, 'control_Bow_at_Banff_test.txt')
# read control file to use with functions
control_options = utl.read_summa_workflow_control_file('/Users/ayx374/Documents/GitHub/forks/summaWorkflow_public/dependencies/cwarhm-summa/0_control_files/control_Bow_at_Banff_test.txt')

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
## the lines below are included if the test data is not available locally

## fm.run_download_ERA5_pressureLevel_paralell(cwarhm_summa_folder)
## fm.run_download_ERA5_surfaceLevel_paralell(cwarhm_summa_folder)
## fm.download_merit_hydro_adjusted_elevation(cwarhm_summa_folder)
## fm.download_modis_mcd12q1_v6(cwarhm_summa_folder)
## fm.download_soilgrids_soilclass_global(cwarhm_summa_folder)

#%% process downloaded data - data specific input layer - part 2

### forcing ERA5 ###
#fm.merge_forcing(cwarhm_summa_folder)
#fm.create_ERA5_shapefile(cwarhm_summa_folder)

## merit hydro ##
merit.extract_merit_tars(control_options)
fm.unpack_merit_hydro(cwarhm_summa_folder)
fm.create_merit_hydro_virtual_dataset(cwarhm_summa_folder)
fm.specify_merit_hydro_subdomain(cwarhm_summa_folder)
fm.convert_merit_hydro_vrt_to_tif(cwarhm_summa_folder)