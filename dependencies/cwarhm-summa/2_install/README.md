# SUMMA and mizuRoute install
SUMMA and mizuRoute are both under active development. This code downloads the latest version of the code base and gives examples of how to compile the Fortran source code of both programs.

Running SUMMA and mizuRoute requires a linux-based environment, because both programs use the `netcdf-fortran` library for which no Windows alternative currently exists.

Requirements:
- linux environment
- fortran compiler (e.g. gcc)
- `netcdf-fortran` library
- `openblas` library 


## Workflow steps
Fork the SUMMA and mizuRoute repositories to your own GitHub account. This currently cannot be done via terminal commands and must be done manually. Note that forking the code to your own account is considered best practice but not strictly necessary. See: https://help.github.com/en/articles/fork-a-repo

SUMMA: https://github.com/ncar/summa

mizuRoute: https://github.com/ncar/mizuRoute

Specify the URL of both repositories/forks and the desired install location in the control file and use the provided scripts to clone the latest version of both models to your local machine. The provided download scripts will work whether you forked the repositories or not. 

Next, compile the source code. This step depends on the user's configuration and cannot easily be standardized. Scripts that compile either executable on the University of Saskatachewan's HPC clusters "Plato" and "Copernicus", and Compute Canada's cluster "Graham", are included to (1) provide a traceable record of USask's SUMMA and mizuRoute setups, and (2) provide an example of how compiling both executables can be done. This example is unlikely to work as is on different computing environments: changes to which modules are loaded and the way in which this is done, and possibly the contents of the makefiles may be necessary. When in doubt, contact your system administrator. The repositories of both models (links given above) provide more details on how they should be compiled. 

## Assumptions not specified in `control_active.txt`
This code by default clones the `develop` branch of both repositories, which contains the latest available fixes and updates before they are included in new releases on the respective `master` branches. 


## Control file settings
This section lists all the settings in `control_active.txt` that the code in this folder uses.
- **github_summa, github_mizu**: GitHub URLs from which to clone SUMMA and mizuRoute.
- **install_path_summa, install_path_mizu**: install locations for both models.
- **exe_name_summa, exe_name_mizu**: names for compiled executables of both models
