# SUMMA workflow
This repository contains scripts to install, set up and run the Structure for Unifying Multiple Modeling Alternatives (SUMMA, Clark et al., 2015a,b) and mizuRoute (Mizukami et al., 2016) to generate hydrologic simulations for a given domain. The workflow uses open-source data with global coverage to determine model parameters and forcing, thus enabling transparent and efficient hydrologic science.


## Scope

A basic SUMMA+mizuRoute setup requires:
- Compiled executables for SUMMA and mizuRoute;
- A shapefile that discretizes the modelling domain into Grouped Responses Units (GRUs) and Hydrological Response Units (HRUs) for use by SUMMA;
- A shapefile that discretizes the river network that connects the GRUs and, optionally, a shapefile that discretizes the routing basins if these are not the same as the SUMMA GRUs for use by mizuRoute;
- Time series of forcing data for each HRU
- Various settings files for SUMMA and mizuRoute that provide parameter values, initial conditions and runtime settings.

This workflow requires the user to provide the catchment and river network shapefiles with certain required contents (see the relevant readme's for details). The scripts in the repository provide all the necessary code to download and pre-process forcing and parameter data, create SUMMA's and mizuRoute's required input files, and run hydrologic and routing simulations. This generates a basic SUMMA + mizuRoute setup, upon which the user can improve by, for example, swapping global datasets for higher quality local ones or connecting the model setup to a calibration algorithm. 


## Data coverage

The workflow uses the following data sources:
- ERA5 forcing data (Copernicus Climate Change Service, 2017), available globally from 1970 to current minus five days;
- SOILGRIDS-derived (Benham et al., 2009; Hengl et al., 2017; Knoben, 2021) maps of global soil classes;
- MODIS maps (Friedl et al., 2019) of global vegetation types.

The workflow can thus generate model setups with global coverage and for the past half century.


## Shapefile requirements

The workflow assumes the user can provide shapefiles that delineate the (sub-)catchments used by SUMMA and the river network used by mizuRoute. These shapefiles should include certain additional info. The folder `0_example` contains example shapefiles that can be used to create a model setup for the Bow at Banff, Canada. This folder also contains a detailed description of shapefile requirements.


## Getting started

Example shapefiles and a control file for the Bow river at Banff, AB, Canada, are provided as part of this repository. Shapefiles can be found in the folder `0_example`. The control file can be found in `0_control_files`. We strongly recommend to first use the provided shapefiles and control file to create your own setup for the Bow river at Banff. This domain is relatively small and the control file only specifies 1 year of data, which limits the download requirements. Instructions:
1. Obtain a copy of the repository code;
2. Ensure your computational environment has the correct packages and modules installed (see below);
3. Modify the setting `root_path` in the file `control_BowAtBanff.txt` to point to your desired data directory location;
4. Run the scripts in order, starting with the one in folder `./1_folder_prep`. This creates a basic folder structure in your specified data directory.
5. Copy the Bow at Banff shapefiles from the `./0_examples/shapefiles` folder in this repo into the newly generated basic folder structure in your data directory. The remaining scripts in the workflow will look for the shapefiles there.
6. Run the remaining scripts in the workflow in order and try to trace which information each script needs and how it obtains this from the control file. Understanding how the workflow operates will make it much easier to create your own control file.


## Typical workflow

The workflow is organized around the idea that the code that generates data (i.e. the scripts that form this repo) is kept in a separate directory from the data that is downloaded and created. The connection between repository scripts and data directory is given in the `control_file` as control setting `root_path`. We strongly recommend to **_not_** put the data directory specified in `root_path` inside any of the repository folders, but to use a dedicated and separate location for the data instead. Note that the size requirement of the data directory depends on the size of the domain and the length and number of simulations.

A typical application would look as follows:

1. Fork this repository to your own GitHub account and clone your fork into an arbitrary folder on your operating platform (e.g. local machine with Linux capabilities, a high performance cluster). 
2. Navigate to `summaWorkflow_public/0_control_files`. Copy and rename `control_BowAtBanff.txt` to something more descriptive of your modeling domain.
3. Update all relevant settings in your newly made control file. Initially, this is mainly:
	- The path to your own data directory, sepcified by setting `root_path`;
	- The names of your shapefiles and the names of the columns in your shapefiles;
	- The spatial extent of your modelling domain;
	- The temporal extent of your period of interest. 
4. Navigate to `summaWorkflow_public/1_folderPrep` and run the notebook or Python code there to create the basic layout of your data directory.
5. Copy your catchment, river network and routing basin shapefiles (`.shp`) into the newly created `your/data/path/domain_[yourDomain]/shapefiles` folder, placing the shapefiles in the `catchment` and `river_network` folders respectively.
6. Run through the various scripts in order.


## Software requirements

The workflow uses a combination of Python and Bash. This section lists how to setup your system to use this workflow. We recommend you contact your system administrator if none of this makes sense. **Note** that this section is a work in progress. 

### Python

The Python code requires various packages, which may be installed through either `pip` or `conda`. It is typically good practice to create a clean (virtual) environment and install the required packages through a package manager. The workflow was developed on Python 3.7.7. and successfully tested on Python 3.8.8. 

Pip:
Package requirements specified in `requirements.txt`. Assumes a local install of the `GDAL` library is available. Scripts for topographic analysis are set up to interact with a stand-alone install of QGIS (see below). Basic instructions to create a new virtual environment:

```
cd /path/to/summaWorkflow_public
virtualenv summa-env
source summa-env/bin/activate
pip install -r requirements.txt
```

Conda:
Package requirements specified in `environment.yml`. Installs `GDAL` as a Conda package. Scripts for topographic analysis are set up to use the Conda `QGIS` package (see below). Basic instructions to create a new virtual environment:

```
cd /path/to/summaWorkflow_public
conda env create -f environment.yml
conda activate summa-env
```

If `summa-env` is not automatically added as a kernel, close the notebook, run the following from a conda terminal and restart the notebook:
```
python -m ipykernel install --name summa-env
```

#### Interaction with QGIS
The scripts used for geospatial analysis use several functions from QGIS. Depending on your system, you may be able to get `QGIS` as a Conda package (https://anaconda.org/conda-forge/qgis) or require a stand-alone install of QGIS (https://qgis.org/en/site/). The provided notebooks in folder `/summaWorkflow_public/5_model_input/SUMMA/1_topo/` are designed to use `QGIS` as a Conda package; the Python scripts in this folder show how to use a standalone install.


### Bash

The Bash code requires various libraries and command line utilities. These are (tested versions in brackets):

- Libraries
	- `GCC (7.3.0)`  compiler: https://gcc.gnu.org/
	- `openblas (0.3.4)` library: https://www.openblas.net/
	- `netcdf-fortran (4.4.4)` library: https://www.unidata.ucar.edu/software/netcdf/fortran/docs/
	- `gdal (2.1.3)`: https://gdal.org/
- CMD utilities
	- [optional] `GNU Parallel (20180122)`: https://www.gnu.org/software/parallel/
	- [optional] `netCDF Operators (4.9.5)`: http://nco.sourceforge.net/
	

## Note on deprecation warnings in Python packages

At the time of writing (12-04-2021) `numpy` issues warnings about a deprecated feature. `netCDF4` uses this feature and as a result any script that uses `netCDF4` currently floods the screen with warnings. These are safe to ignore. See:
- https://github.com/numpy/numpy/issues/18281
- https://github.com/Unidata/netcdf4-python/commit/d50b949ea3982a6281c6bce25d335736ad067b64


## Disclaimer

This workflow (“the program”) is licensed under the GNU GPL v3.0 license. You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/. Please take note of the following:
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
In practical terms, this means that:
1. The developers do not and cannot warrant that the program meets your requirements or that the program is error free or bug free, nor that these errors or bugs can be corrected;
2. You install and use the program at your own risk;
3. The developers do not accept responsibility for the accuracy of the results obtained from using the program. In using the program, you are expected to make the final evaluation of any results in the context of your own problem.


## Acknowledgements

Our thanks to those who have contributed to improving this repository (in order of first reports):

- Dave Casson
- Hongli Liu
- Guoqiang Tang


## References

Benham, E., Ahrens, R. J., & Nettleton, W. D. (2009). Clarification of Soil Texture Class Boundaries. United States Department of Agriculture. https://www.nrcs.usda.gov/wps/portal/nrcs/detail/ks/soils/?cid=nrcs142p2_033171

Clark, M. P., B. Nijssen, J. D. Lundquist, D. Kavetski, D. E. Rupp, R. A. Woods, J. E. Freer, E. D. Gutmann, A. W. Wood, L. D. Brekke, J. R. Arnold, D. J. Gochis, R. M. Rasmussen, 2015a: A unified approach for process-based hydrologic modeling: Part 1. Modeling concept. Water Resources Research, doi:10.1002/2015WR017198

Clark, M. P., B. Nijssen, J. D. Lundquist, D. Kavetski, D. E. Rupp, R. A. Woods, J. E. Freer, E. D. Gutmann, A. W. Wood, D. J. Gochis, R. M. Rasmussen, D. G. Tarboton, V. Mahat, G. N. Flerchinger, D. G. Marks, 2015b: A unified approach for process-based hydrologic modeling: Part 2. Model implementation and case studies. Water Resources Research, doi:10.1002/2015WR017200

Clark, M. P., B. Nijssen, J. D. Lundquist, D. Kavetski, D. E. Rupp, R. A. Woods, J. E. Freer, E. D. Gutmann, A. W. Wood, L. D. Brekke, J. R. Arnold, D. J. Gochis, R. M. Rasmussen, D. G. Tarboton, V. Mahat, G. N. Flerchinger, D. G. Marks, 2015c: The structure for unifying multiple modeling alternatives (SUMMA), Version 1.0: Technical Description. NCAR Technical Note NCAR/TN-514+STR, 50 pp., doi:10.5065/D6WQ01TD

Copernicus Climate Change Service (C3S) (2017): ERA5: Fifth generation of ECMWF atmospheric reanalyses of the global climate. Copernicus Climate Change Service Climate Data Store (CDS), 2020-03-26. https://cds.climate.copernicus.eu/cdsapp#!/home

Friedl, M., Sulla-Menashe, D. (2019). MCD12Q1 MODIS/Terra+Aqua Land Cover Type Yearly L3 Global 500m SIN Grid V006 [Data set]. NASA EOSDIS Land Processes DAAC. Accessed 2020-05-20 from https://doi.org/10.5067/MODIS/MCD12Q1.006

Hengl T, Mendes de Jesus J, Heuvelink GBM, Ruiperez Gonzalez M, Kilibarda M, Blagotić A, et al. (2017) SoilGrids250m: Global gridded soil information based on machine learning. PLoS ONE 12(2): e0169748. https://doi.org/10.1371/journal.pone.0169748

Knoben, W. J. M. (2021). Global USDA-NRCS soil texture class map, HydroShare, https://doi.org/10.4211/hs.1361509511e44adfba814f6950c6e742 	

Mizukami, N., Clark, M. P., Sampson, K., Nijssen, B., Mao, Y., McMillan, H., Viger, R. J., Markstrom, S. L., Hay, L. E., Woods, R., Arnold, J. R., and Brekke, L. D., 2016: mizuRoute version 1: a river network routing tool for a continental domain water resources applications, Geosci. Model Dev., 9, 2223–2238, https://doi.org/10.5194/gmd-9-2223-2016
