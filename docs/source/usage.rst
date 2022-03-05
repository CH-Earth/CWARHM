Usage
=====

.. _installation:

Installation
------------

To use cwarhm, certain dependencies need to be installed. To install using conda:

On the command line or Anaconda prompt go to the cwarhm directory. Then:

.. code-block:: console

    $ conda env create -f environment.yml
    $ conda activate cwarhm-env

Last, the package cwarhm itself can be added to the environment:

.. code-block:: console

    $ pip install -e .

First test
----------
As test case workflows/summa_bowatbanff/ is available. Before running the test script test_bow_at_banff.py, some path modifications have to be made:

1. In control_Bow_at_Banff_test.txt, change the **root_path** modeling domain setting to a local folder where the test results should be saved
2. In test_bow_at_banff.py, change the paths:

  #. cwarhm_summa_folder
  #. results_folder_path , to match the root_path in the control file
  #. test_data_path , path to the test data, if you want to skip the data download workflow steps (by default)
  #. reset_test to True (default), this is a flag that starts a new run (and deletes all data from any results folder), and restarts by copying the test data to the results folder or False: continue with existing data in the results folder.

3. The test data is not part of this repo due to its size (30+GB). For those in the comphyd group it can be found here:

**copernicus** /project/gwf/gwf_cmt/cwarhm_test_data
**GRAHAM** /project/6008034/CompHydCore/cwarhm_test_data

If this is not accessible, you can download the data with the CWARHM functions (wrapped from the original CWARHM). You can also use a results directory from an earlier test run.
