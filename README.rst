CWARHM
=======

**CWARHM** is a Python library to organize workflows to build hydrological models.
The Package branch is to develop the original SUMMA-CWARHM (currently on main, in this branch moved under dependencies/summa-cwarhm) into a python package where the code exectuting workflow steps are callable functions, and the actual workflows (here a workflow are all the steps involved in setting up an hydrological model) are scripts calling the available functions in a certain order.

Installation
--------------
The dependencies of the CWARHM package (or CWARHM-Assembler - CWARHMA) can be installed using conda:

  ``cd /path/to/summaWorkflow_public``
  
  ``conda env create -f environment.yml``
  
  ``conda activate cwarhm-env``


Additionally the package can be installed in the environment in developer mode (not needed for the test):

  ``cd /path/to/summaWorkflow_public``
  
  ``conda activate cwarhm-env``
  
  ``pip install -e .``

Test Bow at Banff SUMMA
----------
As test case workflows/summa_bowatbanff/ is available. Before running the test script test_bow_at_banff.py, some path modifications have to be made:

  1.) In workflows/summa_bowatbanff/control_Bow_at_Banff_test.txt, change the **root_path** modeling domain setting to a local folder where the test results should be saved.
  
  2.) In workflows/summa_bowatbanff/test_bow_at_banff.py, change the paths: 
    - cwarhm_summa_folder; to point to the `./summaWorkflow_public/dependencies/cwarhm-summa` folder
    - results_folder_path , to match the root_path in the control file
    - test_data_path , path to the test data, if you want to skip the data download workflow steps (by default)
    - reset_test to True (default), this is a flag that starts a new run (and deletes all data from any results folder), and restarts by copying the test data to the results folder or False: continue with existing data in the results folder.
    
  3.) The test data is not part of this repo due to its size (30+GB). For those in the comphyd group it can be found here:

**copernicus** /project/gwf/gwf_cmt/cwarhm_test_data
**GRAHAM** /project/6008034/CompHydCore/cwarhm_test_data

If this is not accessible, you can download the data with the CWARHM functions (wrapped from the original CWARHM). You can also use a results directory from an earlier test run.

Test Bow at Banff MESH
---------
The Bow at Banff MESH test, performs a part of a complete workflow (with data specific parts and most of the model agnostic parts processed by the above workflow). to have a look at the relevant functions have a look at tests/test_mesh_bowatbanff.py
Note that for it to run some input data is needed that is now included in the test folder and will be extracted automatically (21MB).
Only one path has to adjusted, but in two(!) places (see test/test_mesh_bowatbanff.py).
