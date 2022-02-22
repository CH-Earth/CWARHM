# mwah_wrapper.py

import sys
import os
import subprocess
import functools
import shutil

submodule_path_default = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "..",
    "..",
    "submodules",
    "summaWorkflow_public",
)


def set_default_path(submodule_path):
    if not submodule_path:
        submodule_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "..",
            "..",
            "submodules",
            "summaWorkflow_public",
        )
    return submodule_path


##WIP
def localworkingdir(func):
    """Decorator - Changes working dir to script_path and resets working dir afterwards"""

    @functools.wraps(func)
    def wrapper(script_path, *args, **kwargs):
        main_working_dir = os.getcwd()
        script_dir = os.path.dirname(script_path)
        os.chdir(script_dir)
        print("working dir of decorator " + script_dir)
        print(os.getcwd)
        try:
            return func(script_path, *args, **kwargs)
        finally:
            os.chdir(main_working_dir)


def exec_python_lwd(script_path, *args, **kwargs):
    """Executes python script with localized working directory.
    Changes working dir to folder of python script before executing.
    Then changes back to original working directory.

    Args:
        script_path (path string): Path to python script
    """
    main_working_dir = os.getcwd()
    script_dir = os.path.dirname(script_path)
    print("running wrapper for {}".format(script_path))
    os.chdir(script_dir)
    exec(open(script_path).read(), globals(), globals())
    os.chdir(main_working_dir)

#TODO write documentation
#TODO finish up subprocess call
def subprocess_lwd(script_path, *args, **kwargs):
    main_working_dir = os.getcwd()
    working_env = os.environ.copy()
    #print(working_env['PATH'])
    script_dir = os.path.dirname(script_path)
    print("running wrapper for {}".format(script_path))
    os.chdir(script_dir)
    subprocess.run(["sh",script_path])
    #subprocess.run(['conda info | grep -i "base environment"' , script_path],env=working_env,shell=True)
    #subprocess.run(["bash -c 'source ~/opt/anaconda3/bin/activate summa-env'" , 'echo yes',script_path],shell=True)
    #subprocess.Popen(script_path,env=working_env)
    #proc = subprocess.run(['conda activate summa-env','conda env list'],executable="/bin/bash",shell=False)
    #subprocess.run(". ~/opt/anaconda3/etc/profile.d/conda.sh && conda activate summa-env && {}".format(script_path),shell=True)
    #subprocess.run(". ~/opt/anaconda3/etc/profile.d/conda.sh && conda env list",shell=True)
    #print(proc)
    os.chdir(main_working_dir)

def run_jupyter_notebook(script_path, *args, **kwargs):
    main_working_dir = os.getcwd()
    script_dir = os.path.dirname(script_path)
    print("running wrapper for {}".format(script_path))
    os.chdir(script_dir)
    subprocess.run("jupyter nbconvert --to notebook --execute {}".format(script_path),shell=True)
    os.chdir(main_working_dir)

def change_control_file_in_submodule(submodule_path: str = None, control_file_name: str = None):
    """Copy control file in test folder to submodule folder and adjust
    'make_folder_structure' to reference this control file. Needs to be 
    run when starting a new run.
    """
    #test_file_dir = os.path.dirname(os.path.realpath(__file__))
    test_file_dir = '.'
    control_file_path = os.path.join(test_file_dir,control_file_name)
    make_folder_structure_path = os.path.join(test_file_dir,'make_folder_structure.py')
    print(os.getcwd())
    target_folder_txt = os.path.join(submodule_path,'0_control_files')
    target_folder_py= os.path.join(submodule_path,'1_folder_prep')
    shutil.copy(control_file_path,os.path.join(target_folder_txt,control_file_name))
    shutil.copy(control_file_path,os.path.join(target_folder_txt,'control_active.txt'))
    shutil.copy(make_folder_structure_path,os.path.join(target_folder_py,'make_folder_structure.py'))

#%% From here the wrapper functions start

### 1 folder prep
def create_folder_structure(submodule_path: str = None):
    """Executes the code from summaWorkflow_public step 1_folder_prep. Description from local python file:
    SUMMA workflow: make folder structure
    Makes the initial folder structure for a given control file. All other files in the workflow will look for the file `control_active.txt` during their execution. This script:

    1. Copies the specified control file into `control_active.txt`;
    2. Prepares a folder structure using the settings in `control_active.txt`.
    3. Creates a copy of itself to be stored in the new folder structure.

    The destination folders are referred to as "domain folders".

    :param submodule_path: path to the summaWorkflow_public repository. Defaults to "../submodules/summaWorkflow_public".
    :type submodule_path: str
    """
    if not submodule_path:
        submodule_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "..",
            "..",
            "submodules",
            "summaWorkflow_public",
        )

    python_file_to_run = os.path.join(
        submodule_path, "1_folder_prep", "make_folder_structure.py"
    )

    exec_python_lwd(python_file_to_run)


### 2 install
def clone_summa_repo(
    submodule_path: str = os.path.join(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "..",
            "..",
            "submodules",
            "summaWorkflow_public",
        )
    )
):

    """This code downloads the latest version of the code base. sh script.
    Settings are given in the control file of mwah.

    Relevant settings in `control_active.txt` that the code in this folder uses:
    - **github_summa, github_mizu**: GitHub URLs from which to clone SUMMA and mizuRoute.

    Args:
        submodule_path (str, optional): path to the summaWorkflow_public repository.
        Defaults to "../submodules/summaWorkflow_public".
    """
    script_path = os.path.join(submodule_path, "2_install", "1a_clone_summa.sh")
    subprocess_lwd(script_path)


def compile_summa(submodule_path: str):

    """[Description]]

    Args:
        submodule_path (str: path to the summaWorkflow_public repository.
    """
    script_path = os.path.join(submodule_path, "2_install", "1b_compile_summa.sh")
    subprocess_lwd(script_path)


def clone_mizuroute_repo(submodule_path: str):
    """[Description]]

    Args:
        submodule_path (str, optional): path to the summaWorkflow_public repository.
    """
    script_path = os.path.join(submodule_path, "2_install", "2a_clone_mizuroute.sh")
    subprocess_lwd(script_path)


def compile_mizuroute(submodule_path: str):
    """[Description]]

    Args:
        submodule_path (str, optional): path to the summaWorkflow_public repository.
    """
    script_path = os.path.join(submodule_path, "2_install", "2b_compile_mizuroute.sh")
    subprocess_lwd(script_path)


### 3a forcing
def download_ERA5_pressureLevel_annual(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "3a_forcing", "1a_download_forcing", "download_ERA5_pressureLevel_annual.ipynb"
    )
    run_jupyter_notebook(python_file_to_run)


def download_ERA5_surfaceLevel_annual(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "3a_forcing", "1a_download_forcing", "download_ERA5_surfaceLevel_annual.ipynb"
    )

    run_jupyter_notebook(python_file_to_run)


def run_download_ERA5_pressureLevel_paralell(submodule_path: str):

    """[Description]]

    Args:
        submodule_path (str: path to the summaWorkflow_public repository.
    """
    script_path = os.path.join(submodule_path, "3a_forcing", "1a_download_forcing", "run_download_ERA5_pressureLevel.sh")
    subprocess_lwd(script_path)


def run_download_ERA5_surfaceLevel_paralell(submodule_path: str):

    """[Description]]

    Args:
        submodule_path (str: path to the summaWorkflow_public repository.
    """
    script_path = os.path.join(submodule_path, "3a_forcing", "1a_download_forcing", "run_download_ERA5_surfaceLevel.sh")
    subprocess_lwd(script_path)


def download_ERA5_geopotential(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "3a_forcing", "1b_download_geopotential", "download_ERA5_geopotential.py"
    )

    exec_python_lwd(python_file_to_run)


def merge_forcing(submodule_path: str = submodule_path_default):
    """3a_forcing, 2_merge_forcing
    Combine separate surface and pressure level downloads
    Creates a single monthly `.nc` file with SUMMA-ready variables for further processing.
    Combines ERA5's `u` and `v` wind components into a single directionless wind vector.

    This script goes through the following steps:
    1. Convert longitude coordinates in pressureLevel file to range [-180,180]
    2. Checks
    - are lat/lon the same for both data sets?
    - are times the same for both datasets?
    3. Aggregate data into a single file 'ERA5_NA_[yyyymm].nc', keeping the relevant metadata in place

        Args:
            submodule_path (str, optional): path to the summaWorkflow_public repository. Defaults to submodule_path.
    """
    python_file_to_run = os.path.join(
        submodule_path,
        "3a_forcing",
        "2_merge_forcing",
        "ERA5_surface_and_pressure_level_combiner.py",
    )

    exec_python_lwd(python_file_to_run)


def create_ERA5_shapefile(submodule_path: str = submodule_path_default):
    """mwah workflow 3a_forcing, 3_create_shapefile
        The shapefile for the forcing data needs to represent the regular latitude/longitude grid of the ERA5 data. We need this for later intersection with the catchment shape(s) so we can create appropriately weighted forcing for each model element.

    Notebook/script reads location of merged forcing data and the spatial extent of the data from the control file.

    ## Assumptions not included in `control_active.txt`
    - Code assumes that the merged forcing contains dimension variables with the names "latitude" and "longitude". This is the case for ERA5.

        Args:
            submodule_path (str, optional): [description]. Defaults to submodule_path.
    """
    python_file_to_run = os.path.join(
        submodule_path, "3a_forcing", "3_create_shapefile", "create_ERA5_shapefile.py"
    )

    exec_python_lwd(python_file_to_run)


### 3b parameters
## Merit Hydro


def download_merit_hydro_adjusted_elevation(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "3b_parameters", "MERIT_Hydro_DEM", "1_download", "download_merit_hydro_adjusted_elevation.py"
    )

    exec_python_lwd(python_file_to_run)


def unpack_merit_hydro(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "3b_parameters", "MERIT_Hydro_DEM", "2_unpack", "unpack_merit_hydro_dem.sh"
    )

    subprocess_lwd(python_file_to_run)


def create_merit_hydro_virtual_dataset(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    file_to_run = os.path.join(
        submodule_path, "3b_parameters", "MERIT_Hydro_DEM", "3_create_vrt", "make_merit_dem_vrt.sh"
    )

    subprocess_lwd(file_to_run)


def specify_merit_hydro_subdomain(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    file_to_run = os.path.join(
        submodule_path, "3b_parameters", "MERIT_Hydro_DEM", "4_specify_subdomain", "specify_subdomain.sh"
    )

    subprocess_lwd(file_to_run)


def convert_merit_hydro_vrt_to_tif(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    file_to_run = os.path.join(
        submodule_path, "3b_parameters", "MERIT_Hydro_DEM", "5_convert_to_tif", "convert_vrt_to_tif.sh"
    )

    subprocess_lwd(file_to_run)


## MODIS


def download_modis_mcd12q1_v6(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "3b_parameters", "MODIS_MCD12Q1_V6", "1_download", "download_modis_mcd12q1_v6.py"
    )

    exec_python_lwd(python_file_to_run)


def create_modis_virtual_dataset(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    file_to_run = os.path.join(
        submodule_path, "3b_parameters", "MODIS_MCD12Q1_V6", "2_create_vrt", "make_vrt_per_year.sh"
    )

    subprocess_lwd(file_to_run)


def reproject_modis_virtual_dataset(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    file_to_run = os.path.join(
        submodule_path, "3b_parameters", "MODIS_MCD12Q1_V6", "3_reproject_vrt", "reproject_vrt.sh"
    )

    subprocess_lwd(file_to_run)


def specify_modis_subdomain(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    file_to_run = os.path.join(
        submodule_path, "3b_parameters", "MODIS_MCD12Q1_V6", "4_specify_subdomain", "specify_subdomain.sh"
    )

    subprocess_lwd(file_to_run)


def create_multiband_modis_vrt(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    file_to_run = os.path.join(
        submodule_path, "3b_parameters", "MODIS_MCD12Q1_V6", "5_multiband_vrt", "create_multiband_vrt.sh"
    )

    subprocess_lwd(file_to_run)


def convert_modis_vrt_to_tif(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    file_to_run = os.path.join(
        submodule_path, "3b_parameters", "MODIS_MCD12Q1_V6", "6_convert_to_tif", "convert_vrt_to_tif.sh"
    )

    subprocess_lwd(file_to_run)


def find_mode_modis_landclass(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "3b_parameters", "MODIS_MCD12Q1_V6", "7_find_mode_land_class", "find_mode_landclass.py"
    )

    exec_python_lwd(python_file_to_run)


### Soilgrids


def download_soilgrids_soilclass_global(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "3b_parameters", "SOILGRIDS", "1_download", "download_soilclass_global_map.py"
    )

    exec_python_lwd(python_file_to_run)


def extract_soilgrids_domain(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "3b_parameters", "SOILGRIDS", "2_extract_domain", "extract_domain.py"
    )

    exec_python_lwd(python_file_to_run)


### 4a sort shape
def sort_catchment_shape(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "4a_sort_shape", "1_sort_catchment_shape.py"
    )

    exec_python_lwd(python_file_to_run)


### 4b remapping
## 1 topo
def find_HRU_elevation(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "4b_remapping", "1_topo", "1_find_HRU_elevation.py"
    )

    exec_python_lwd(python_file_to_run)


def find_HRU_soil_classes(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "4b_remapping", "1_topo", "2_find_HRU_soil_classes.py"
    )

    exec_python_lwd(python_file_to_run)


def find_HRU_land_classes(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "4b_remapping", "1_topo", "3_find_HRU_land_classes.py"
    )

    exec_python_lwd(python_file_to_run)


## 2 forcing
def make_single_weighted_forcing_file(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "4b_remapping", "2_forcing", "1_make_one_weighted_forcing_file.py"
    )

    exec_python_lwd(python_file_to_run)


def make_all_weighted_forcing_files(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "4b_remapping", "2_forcing", "2_make_all_weighted_forcing_files.py"
    )

    exec_python_lwd(python_file_to_run)


def temperature_lapsing_and_datastep(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "4b_remapping", "2_forcing", "3_temperature_lapsing_and_datastep.py"
    )

    exec_python_lwd(python_file_to_run)


### 5 model input
## mizuRoute
def read_mizuroute_base_settings():
    pass


def copy_mizuroute_base_settings(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "5_model_input", "mizuRoute","1a_copy_base_settings", "1_copy_base_settings.py"
    )

    exec_python_lwd(python_file_to_run)


def create_mizuroute_network_topology_file(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "5_model_input", "mizuRoute","1b_network_topology_file", "1_create_network_topology_file.py"
    )

    exec_python_lwd(python_file_to_run)


def remap_summa_catchments_to_mizurouting(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "5_model_input", "mizuRoute","1c_optional_remapping_file", "1_remap_summa_catchments_to_routing.py"
    )

    exec_python_lwd(python_file_to_run)


def create_mizuroute_control_file(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "5_model_input", "mizuRoute","1d_control_file", "1_create_control_file.py"
    )

    exec_python_lwd(python_file_to_run)


## SUMMA
def read_summa_base_settings():
    pass


def copy_summa_base_settings(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "5_model_input", "SUMMA","1a_copy_base_settings", "1_copy_base_settings.py"
    )
    
    exec_python_lwd(python_file_to_run)


def create_summa_file_manager(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "5_model_input", "SUMMA","1b_file_manager", "1_create_file_manager.py"
    )

    exec_python_lwd(python_file_to_run)


def create_summa_forcing_file_list(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "5_model_input", "SUMMA","1c_forcing_file_list", "1_create_forcing_file_list.py"
    )

    exec_python_lwd(python_file_to_run)


def create_summa_cold_state(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "5_model_input", "SUMMA","1d_initial_conditions", "1_create_coldState.py"
    )

    exec_python_lwd(python_file_to_run)


def create_summa_trial_parameters(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "5_model_input", "SUMMA","1e_trial_parameters", "1_create_trialParams.py"
    )

    exec_python_lwd(python_file_to_run)


# attributes


def initialize_summa_attributes_nc(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "5_model_input", "SUMMA","1f_attributes", "1_initialize_attributes_nc.py"
    )

    exec_python_lwd(python_file_to_run)


def insert_soilclass_from_hist_into_summa_attributes(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "5_model_input", "SUMMA","1f_attributes", "2a_insert_soilclass_from_hist_into_attributes.py"
    )

    exec_python_lwd(python_file_to_run)


def insert_landclass_from_hist_into_summa_attributes(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "5_model_input", "SUMMA","1f_attributes", "2b_insert_landclass_from_hist_into_attributes.py"
    )

    exec_python_lwd(python_file_to_run)


def insert_elevation_from_hist_into_summa_attributes(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    python_file_to_run = os.path.join(
        submodule_path, "5_model_input", "SUMMA","1f_attributes", "2c_insert_elevation_into_attributes.py"
    )

    exec_python_lwd(python_file_to_run)


### 6 Model runs
def run_summa(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    file_to_run = os.path.join(
        submodule_path, "6_model_runs", "1_run_summa.sh"
    )

    subprocess_lwd(file_to_run)


def run_summa_as_array(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    file_to_run = os.path.join(
        submodule_path, "6_model_runs", "1_run_summa_as_array.sh"
    )

    subprocess_lwd(file_to_run)


def run_mizuroute(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    file_to_run = os.path.join(
        submodule_path, "6_model_runs", "2_run_mizuRoute.sh"
    )

    subprocess_lwd(file_to_run)


### 7 Visualization


def plot_mizuroute_and_summa_shapefiles(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    file_to_run = os.path.join(
        submodule_path, "7_visualization", "1_mizuRoute_and_summa_shapefiles.ipynb"
    )

    run_jupyter_notebook(file_to_run)


def plot_ERA5_download_coordinates_and_catchment_shapefile(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    file_to_run = os.path.join(
        submodule_path, "7_visualization", "2_ERA5_download_coordinates_and_catchment_shapefile.ipynb"
    )

    run_jupyter_notebook(file_to_run)


def plot_forcing_grid_vs_catchment_averaged(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    file_to_run = os.path.join(
        submodule_path, "7_visualization", "3_forcing_grid_vs_catchment_averaged.ipynb"
    )

    run_jupyter_notebook(file_to_run)


def plot_temperature_lapse_rates(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    file_to_run = os.path.join(
        submodule_path, "7_visualization", "4_temperature_lapse_rates.ipynb"
    )

    run_jupyter_notebook(file_to_run)


def plot_geospatial_parameters_to_model_elements(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    file_to_run = os.path.join(
        submodule_path, "7_visualization", "5_geospatial_parameters_to_model_elements.ipynb"
    )

    run_jupyter_notebook(file_to_run)


def plot_SWE_SM_ET_Q_per_GRU(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    file_to_run = os.path.join(
        submodule_path, "7_visualization", "6_SWE_SM_ET_Q_per_GRU.ipynb"
    )

    run_jupyter_notebook(file_to_run)

def plot_SWE_and_streamflow_per_HRU(submodule_path: str):
    """[description]

    :param submodule_path: path to the summaWorkflow_public repository.
    :type submodule_path: str
    """


    file_to_run = os.path.join(
        submodule_path, "7_visualization", "7_SWE_and_streamflow_per_HRU.ipynb"
    )

    run_jupyter_notebook(file_to_run)


#%% test area
mwah_sbmodule_folder = "/Users/ayx374/Documents/GitHub/forks/comphydShared_summa/submodules/summaWorkflow_public"

# create_folder_structure(mwah_sbmodule_folder)
# clone_summa_repo(mwah_sbmodule_folder)
# clone_mizuroute_repo(mwah_sbmodule_folder)
# merge_forcing(mwah_sbmodule_folder)
# create_ERA5_shapefile(mwah_sbmodule_folder)
#create_modis_virtual_dataset(mwah_sbmodule_folder)
