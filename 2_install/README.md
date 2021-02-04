# SUMMA and mizuRoute install
Terminal commands only.

Requirements:
- linux environment
- fortran compiler (e.g. gcc)
- netcdf-fortran library
- openblas library
- (sundials library - now now, but later)

## Workflow steps
Fork the SUMMA and mizuRoute repositories to your own GitHub account. This currently cannot be done via terminal commands and must be manual. See: https://help.github.com/en/articles/fork-a-repo

SUMMA: https://github.com/ncar/summa

mizuRoute: https://github.com/ncar/mizuRoute

Next, use the provided scripts to clone both repositories to an install directory. GitHub links and install directories can be specified in the control file.  

Finally, compile the source code. This step depends on the user's configuration and cannot easily be standardized. Scripts that compile either executable on the University of Saskatachewan's HPC cluster "Copernicus" are included (1) to provide a traceable record of USask's SUMMA and mizuRoute setups, and (2) to provide an example of how compiling both executables can be done. 

## Assumptions not specified in `control_active.txt`
This code by default clones the `develop` branch of both repositories, to get the latest available fixes and updates before they are released on the respective `master` branches. 