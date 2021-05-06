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

Next, compile the source code. This step depends on the user's configuration and cannot easily be standardized. Scripts that compile either executable on the University of Saskatachewan's HPC cluster "Copernicus" are included to (1) provide a traceable record of USask's SUMMA and mizuRoute setups, and (2) provide an example of how compiling both executables can be done. This example is unlikely to work as is on different computing environments and changes to the way and which modules are loaded and possibly the contents of the makefiles may be necessary. When in doubt, contact your system administrator. The repositories of both models (links given above) provide more details on how they should be compiled. 

## Assumptions not specified in `control_active.txt`
This code by default clones the `develop` branch of both repositories, which contains the latest available fixes and updates before they are included in new releases on the respective `master` branches. 

## Note on Makefile versions
Note that both programs are under active development and thus that substantial changes to the code base can happen. This may result in changes to the respective Makefiles too, meaning that it cannot be guaranteed that older Makefiles will still work after an update. Therefore the Makefiles that are part of this repository are provided as a *record* of our setup on 2021-02-05 and may not necessarily work with newer versions of SUMMA and mizuRoute. Up-to-date Makefiles are included as part of the source code of both programs and can be found in `[program]/build`. 

## Note on mizuRoute compiling
At the time of writing (mizuRoute commit `137820620f624f84f8cdb1d4e9884b8222a3f3df`) the compiler issues six warnings: one about an unused function, two about possible conversion errors, two about unused variables and one about unused dummy argument. These can safely be ignored.