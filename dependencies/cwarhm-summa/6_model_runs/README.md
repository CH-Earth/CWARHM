# Model runs
Contains scripts needed to run SUMMA and mizuRoute for a given experiment, using the experiment settings as defined in the control file. Script `1_run_summa_as_array.sh` can be used to run SUMMA with the `-g` argument, which can be used to parallelize runs. Run `summa.exe` without any input arguments to get a brief overview of the `-g` and other possible runtime arguments.

## Control file settings
This section lists all the settings in `control_active.txt` that the code in this folder uses.
- **install_path_summa, install_path_mizuroute**: install directories of both models
- **exe_name_summa, exe_name_mizuroute**: names of compiled executables
- **settings_summa_path, settings_mizu_path: main setting paths
- **settings_summa_filemanager, settings_mizu_control_file**: location of filemanager and mizuRoute.control files, which need to be specified as arguments for the executables
- **experiment_log_summa, experiment_log_mizuroute**: location where log files need to be saved
- **experiment_id**: name of the experiment
- **experiment_backup_settings**: flag to disable the backup of model input files 

