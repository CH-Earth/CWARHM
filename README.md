# Community Workflows to Advance Reproducibility in Hydrologic Modeling (CWARHM)
This is the code repository that accompanies the paper _"Community Workflows to Advance Reproducibility in Hydrologic Modeling: Separating model-agnostic and model-specific configuration steps in applications of large-domain hydrologic models"_ (Knoben et al., 2022).

## Introduction
Despite the proliferation of computer-based research on hydrology and water resources, such research is typically poorly reproducible. Published studies have low reproducibility because of both incomplete availability of the digital artifacts of research and a lack of documentation on workflow processes. This leads to a lack of transparency and efficiency because existing code can neither be checked nor re-used. Given the high-level commonalities between existing process-based hydrological models in terms of their input data and required pre-processing steps, more open sharing of code can lead to large efficiency gains for the modeling community. 

Here we present a model configuration workflow that provides full reproducibility of the resulting model instantiation in a way that separates the model-agnostic preprocessing of specific datasets from the model-specific requirements that specific models impose on their input files. This workflow is applied to the Structure for Unifying Multiple Modeling Alternatives (SUMMA, Clark et al., 2015a,b) and mizuRoute (Mizukami et al., 2016), to create a model configuration that provides process-based hydrologic simulations and vector-based streamflow routing capabilities. The workflow uses open-source data with global coverage to determine model parameters and forcing, thus enabling transparent and efficient hydrologic science.

The code in this repository is the outcome of stepwise modification of an existing SUMMA instantiation developed by Andy Wood and colleagues at NCAR. This existing setup served as a testbed for consecutive changes to model input data, domain discretization and domain size, resulting in globally applicable model setup code that separates model-agnostic and model-specific configuration tasks.

All separate README files in this repository have been collated here: https://cwarhm.readthedocs.io/en/latest/.

## README structure
This readme covers the following:
1. **Repository and workflow scope**, covering (i) models, (ii) data sources, and (iii) limitations.
2. **Workflow requirements**, covering (i) the computational environment, (ii) the ESRI shapefile a user needs to provide as input, (iii) workflow control files, and (iv) disk space.
3. **Test cases**, covering (i) global, (ii) continental, and (iii) local test cases.
4. **Getting started**, covering (i) a typical workflow use description, (ii) a practical example using the local test case, and (iii) instructions for configuring the required computational environment.
5. Disclaimer, acknowledgements and references.


## Note on cyber security
Use of this workflow requires accounts with various data providers. Login details with these providers are stored as plain text in the user's home directory. It is therefore strongly recommended that you **choose unique, new passwords for these accounts**. Using the same passwords you use elsewhere poses a security risk.

----------
----------

## Scope
This repository and the manuscript it accompanies (Knoben et al., 2022) contain and describe a workflow used to configure a single set of hydrologic and routing models for multiple spatial domains. This is seen as the first step on a possible route to a community modeling culture. Later steps envision modification of this initial workflow to configure different experiments or models. This workflow is intentionally generalized and modular, so that such modifications of its code are possible. 

### Models
The workflow uses the Structure for Unifying Multiple Modeling Alternatives (SUMMA, Clark et al., 2015a,b) hydrologic model and mizuRoute (Mizukami et al., 2016) routing model. 

### Data coverage
The workflow uses the following data sources:
- ERA5 forcing data (Copernicus Climate Change Service, 2017), available globally from 1979 to current minus five days;
- SOILGRIDS-derived (Benham et al., 2009; Hengl et al., 2017; Knoben, 2021) maps of global soil classes;
- MODIS maps (Friedl et al., 2019) of global vegetation types;
- MERIT Hydro Hydrologically Adjusted Elevations (Yamazaki et al., 2019) as a DEM.

The workflow can thus generate model setups with global coverage and for the past half century.

### Limitations
Currently, the workflow scope deliberately excludes spatial discretization and parameter estimation. 

----------
----------

## Requirements
Four things are needed to execute the workflow code in this repository: the correct computational environment, an ESRI shapefile containing the modeling domain, a so-called _workflow control file_, and sufficient disk space. 

### Computational enviroment
The model configuration code is written in a combination of Bash and Python and requires various libraries and Python packages. Here we specify exact versions of each, as they were used to run the three modeling test cases presented in Knoben et al. (2022).

Libraries needed for required Python packages:
```
proj             7.0.1   https://proj.org/
geos             3.8.1   https://libgeos.org/
gdal             3.0.4   https://gdal.org/             Note: also used as a command line utility by certain scripts
libspatialindex  1.8.5   https://libspatialindex.org/
qgis             3.18.1  https://www.qgis.org/         Note: see Getting Started section for installation details
```
Python packages are listed in the `environment.yml` and `requirements.txt` files that can be found in the root folder of this repository. See the `Getting started` section for instructions on how to use these with conda and pip, respectively.

Fortran libraries, needed to compile SUMMA and mizuRoute:
```
gcc             7.3.0  https://gcc.gnu.org/
openblas        0.3.4  https://www.openblas.net/
netcdf-fortran  4.4.4  https://www.unidata.ucar.edu/software/netcdf/fortran/docs/
```
Optional utilities:
```
GNU Parallel                  20180122  https://www.gnu.org/software/parallel/
netCDF Operators              4.9.5     http://nco.sourceforge.net/
Climate Data Operators (cdo)  1.9.8     https://code.mpimet.mpg.de/projects/cdo
```


### ESRI shapefile
The scope of our workflow implementation assumes that the user has access to a basin discretization stored as an ESRI shapefile that defines the area of interest as discrete modeling elements (e.g., grid cells, sub-basins). Specifically, the workflow expects:

- A shapefile that discretizes the modelling domain into Grouped Responses Units (GRUs) and Hydrological Response Units (HRUs) for use by SUMMA;
- A shapefile that discretizes the river network that connects the GRUs and, optionally, a shapefile that discretizes the routing basins if these are not the same as the SUMMA GRUs for use by mizuRoute;

These shapefiles should include certain mandatory elements. The folder `0_example` contains a detailed description of shapefile requirements. It also contains example shapefiles that can be used to create a model setup for the Bow River at Banff, Canada. See the `Test cases` section for instructions on how to replicate the Bow at Banff model configuration.


### Workflow control file
Users interact with the workflow through so-called _control files_ that contain certain high-level decisions about the model configuration the workflow will generate. The repository contains examples of these in the folder `0_control_files`. Instructions can be found in the `Getting started` section.


### Disk space
Disk space requirements are largely dependent on the size of the modeling domain (in time and space) and the number of output variables saved by SUMMA. Minimum requirements for the Bow at Banff example are as follows:

- Workflow repository code: < 250 MB
- SUMMA source code: < 50 MB
- mizuRoute source code: < 50 MB
- Initial forcing data download: < 20 MB (5 years at hourly resolution, 20 ERA5 grid cells)
- Initial soil map download: < 500 MB (downloads a global map that is later subset to the region of interest)
- Initial DEM data download: ~3.5 GB (downloads a 30x30 degree region that is later subset to the region of interest)
- Initial MODIS data download: ~22 GB (downloads global data that is later subset to the region of interest)
- SUMMA simulation: < 150 MB (18 model variables simulated with hourly timesteps but saved as daily values)
- mizuRoute simulation: < 100 MB (both routing schemes)

Note that data generated in intermediate steps in the workflow is saved in corresponding directories. Users may wish to manually delete these intermediate results if disk space is an issue. 

----------
----------

## Test cases 
This section provides brief details about the model configuration test cases shown in Knoben et al. (2022).
All control files can be found in the folder `0_control_files`.

### Global model configuration
This first test case simulates hydrologic processes across planet Earth to illustrate
the large-domain applicability of our approach. The global domain (excluding Greenland 
and Antarctica) is divided into 2,939,385 sub-basins or Grouped Response Units
(GRUs; median GRU size is 36 km2; mean size is 45 km2) derived from the global MERIT
basins data set (Lin et al., 2019). Simulations are run for a single month (1979-01-01 to
1979-01-31) at a 15-minute temporal resolution.

- Control files: `control_Africa.txt`, `control_Europe.txt`, `control_NorthAmerica.txt`, `control_NorthAsia.txt`, `control_Oceania.txt`, `control_SouthAmerica.txt`, `control_SouthAsia.txt`
- Shapefiles: provided through Hydroshare (Knoben et al., 2022a)
- Notes: for processing convenience, the global domain is divided into several sub-domains.

### Continental model configuration
This second test case uses 40 years of hourly forcing data to simulate hydrologic
 processes over the North American continent and illustrates the combined large-domain
 and multi-decadal applicability of our approach. The continental domain is divided into
 517,315 sub-basins (median GRU size is 33 km2; mean size is 40 km2) derived from the
 global MERIT basins data set (Lin et al., 2019). Simulations are run from 1979-01-01
 to 2019-12-31 at a 15-minute temporal resolution.

- Control file: `control_NorthAmerica`
- Shapefiles: provided through Hydroshare (Knoben et al., 2022a)

### Local model configuration
This third test case uses 5 years of hourly forcing data to simulate hydrologic
436 processes over the Bow at Banff catchment located in Alberta, Canada and illustrates
the ability of our workflow to deal with complex spatial discretization shapefiles. The 
local domain is divided into 51 sub-basins (median GRU size is 32 km2; mean size is 43
km2) derived from the global MERIT basins data set (Lin et al., 2019). These sub-basins 
are further discretized into Hydrological Response Units (HRUs), based on 500 meter elevation 
increments, resulting in 118 HRUs (median HRU size is 11 km2; mean size is 19 km2). 
Simulations are run from 2008-01-01 to 2013-12-31 at a 15-minute temporal resolution.

- Control file: `control_Bow_at_Banff.txt`
- Shapefiles: provided in folder `0_example/shapefiles`

----------
----------

## Getting started

### Typical workflow

The workflow is organized around the idea that the code that generates data (i.e. the scripts that form this repo) is kept in a separate directory from the data that is downloaded and created. The connection between repository scripts and data directory is given in the `control_file` as control setting `root_path`. We strongly recommend to **_not_** put the data directory specified in `root_path` inside any of the repository folders, but to use a dedicated and separate location for the data instead. Note that the size requirement of the data directory depends on the size of the domain and the length and number of simulations.

A typical application would look as follows:

1. Fork this repository to your own GitHub account and clone your fork into an arbitrary folder on your operating platform (e.g. local machine with Linux capabilities, a high performance cluster).
2. Create the right computational environment.
2. Navigate to `summaWorkflow_public/0_control_files`. Copy and rename `control_BowAtBanff.txt` to something more descriptive of your modeling domain.
3. Update all relevant settings in your newly made control file. Initially, this is mainly:
	- The path to your own data directory, sepcified by setting `root_path`;
	- The names of your shapefiles and the names of the columns in your shapefiles;
	- The spatial extent of your modelling domain;
	- The temporal extent of your period of interest. 
4. Navigate to `summaWorkflow_public/1_folderPrep` and run the notebook or Python code there to create the basic layout of your data directory.
5. Copy your catchment, river network and routing basin shapefiles (`.shp`) into the newly created `your/data/path/domain_[yourDomain]/shapefiles` folder, placing the shapefiles in the `catchment` and `river_network` folders respectively.
6. Run through the various scripts in order.

Doing so will generate a basic SUMMA and mizuRoute setup that contains the following:

- Compiled executables for SUMMA and mizuRoute;
- Model-agnostic pre-processed forcing and geospatial parameter data;
- Remapped forcing data (as timeseries) and geospatial data (as representative values) for each model element (HRUs) defined in the user's shapefile;
- Model-specific settings files for SUMMA and mizuRoute that provide parameter values, initial conditions and runtime settings;
- Model simulations from SUMMA and mizuRoute.

This workflow requires the user to provide the catchment and river network shapefiles with certain required contents (see the relevant readme's for details). The scripts in the repository provide all the necessary code to download and pre-process forcing and parameter data, create SUMMA's and mizuRoute's required input files, and run hydrologic and routing simulations. This generates a basic SUMMA + mizuRoute setup upon which the user can improve by, for example, swapping global datasets for higher quality local ones or connecting the model setup to a calibration algorithm. 

### A concrete example

To assist in understanding the process described above, example shapefiles and a control file for the Bow river at Banff, AB, Canada, are provided as part of this repository. Shapefiles can be found in the folder `0_example`. The control file can be found in `0_control_files`. We strongly recommend to first use the provided shapefiles and control file to create your own setup for the Bow river at Banff. This domain is relatively small and the control file only specifies 1 year of data, which limits the download requirements. Instructions:

1. Obtain a copy of the repository code;
2. Ensure your computational environment has the correct packages and modules installed (see below);
3. Modify the setting `root_path` in the file `control_BowAtBanff.txt` to point to your desired data directory location;
4. Run the scripts in order, starting with the one in folder `./1_folder_prep`. This creates a basic folder structure in your specified data directory.
5. Copy the Bow at Banff shapefiles from the `./0_examples/shapefiles` folder in this repo into the newly generated basic folder structure in your data directory. The remaining scripts in the workflow will look for the shapefiles there.
6. Run the remaining scripts in the workflow in order and try to trace which information each script needs and how it obtains this from the control file. Understanding how the workflow operates will make it much easier to create your own control file.


### Setting up the computational environment
The workflow uses a combination of Python and Bash. This section lists how to setup your system to use this workflow. We recommend you contact your system administrator if none of this makes sense. **Note** that this section is a work in progress. 

#### Bash
The Bash code requires various libraries and command line utilities. See the `Requirements` section above.

#### Python

The Python code requires various packages, which may be installed through either `pip` or `conda`. Please note that while conda automatically installs the necessary underlying libraries for a given package, pip does not. The user must take care to have local installs of the required libraries if using pip. See the `Requirements` section above. It is typically good practice to create a clean (virtual) environment and install the required packages through a package manager. The workflow was developed on Python 3.7.7. and successfully tested on Python 3.8.8. 

Pip:
Package requirements specified in `requirements.txt`. Assumes a local install various libraries is available. Basic instructions to create a new virtual environment:

```
cd /path/to/CWARHM
virtualenv cwarhm-env
source cwarhm-env/bin/activate
pip install -r requirements.txt
```

Conda:
Package requirements specified in `environment.yml`.  Basic instructions to create a new virtual environment:

```
cd /path/to/CWARHM
conda env create -f environment.yml
conda activate cwarhm-env
```

If `cwarhm-env` is not automatically added as a Jupyter notebook kernel, close the notebook, run the following from a terminal and restart the notebook:
```
python -m ipykernel install --name cwarhm-env
```

#### Notes on topographic analysis (remapping) with QGIS
The code used for geospatial data remapping use several functions from QGIS. This code can be found in folder `/CWARHM/4b_remapping/1_topo/`. Depending on your system, you may be able to get `QGIS` as a Conda package (https://anaconda.org/conda-forge/qgis) or require a stand-alone install of QGIS (https://qgis.org/en/site/). The provided notebooks (`.ipynb`) are designed to use `QGIS` as a Conda package; the Python scripts (`.py`) in that folder show how to use a standalone install. The folder also contains a more detailed description of QGIS setup.

-------------
-------------

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
- Hannah Burdett
- Hongli Liu
- Guoqiang Tang
- Jim Freer


## References

Benham, E., Ahrens, R. J., & Nettleton, W. D. (2009). Clarification of Soil Texture Class Boundaries. United States Department of Agriculture. https://www.nrcs.usda.gov/wps/portal/nrcs/detail/ks/soils/?cid=nrcs142p2_033171

Clark, M. P., B. Nijssen, J. D. Lundquist, D. Kavetski, D. E. Rupp, R. A. Woods, J. E. Freer, E. D. Gutmann, A. W. Wood, L. D. Brekke, J. R. Arnold, D. J. Gochis, R. M. Rasmussen, 2015a: A unified approach for process-based hydrologic modeling: Part 1. Modeling concept. Water Resources Research, doi:10.1002/2015WR017198

Clark, M. P., B. Nijssen, J. D. Lundquist, D. Kavetski, D. E. Rupp, R. A. Woods, J. E. Freer, E. D. Gutmann, A. W. Wood, D. J. Gochis, R. M. Rasmussen, D. G. Tarboton, V. Mahat, G. N. Flerchinger, D. G. Marks, 2015b: A unified approach for process-based hydrologic modeling: Part 2. Model implementation and case studies. Water Resources Research, doi:10.1002/2015WR017200

Clark, M. P., B. Nijssen, J. D. Lundquist, D. Kavetski, D. E. Rupp, R. A. Woods, J. E. Freer, E. D. Gutmann, A. W. Wood, L. D. Brekke, J. R. Arnold, D. J. Gochis, R. M. Rasmussen, D. G. Tarboton, V. Mahat, G. N. Flerchinger, D. G. Marks, 2015c: The structure for unifying multiple modeling alternatives (SUMMA), Version 1.0: Technical Description. NCAR Technical Note NCAR/TN-514+STR, 50 pp., doi:10.5065/D6WQ01TD

Copernicus Climate Change Service (C3S) (2017): ERA5: Fifth generation of ECMWF atmospheric reanalyses of the global climate. Copernicus Climate Change Service Climate Data Store (CDS), 2020-03-26. https://cds.climate.copernicus.eu/cdsapp#!/home

Friedl, M., Sulla-Menashe, D. (2019). MCD12Q1 MODIS/Terra+Aqua Land Cover Type Yearly L3 Global 500m SIN Grid V006 [Data set]. NASA EOSDIS Land Processes DAAC. Accessed 2020-05-20 from https://doi.org/10.5067/MODIS/MCD12Q1.006

Hengl T, Mendes de Jesus J, Heuvelink GBM, Ruiperez Gonzalez M, Kilibarda M, Blagotić A, et al. (2017) SoilGrids250m: Global gridded soil information based on machine learning. PLoS ONE 12(2): e0169748. https://doi.org/10.1371/journal.pone.0169748

Knoben, W. J. M. (2021). Global USDA-NRCS soil texture class map, HydroShare, https://doi.org/10.4211/hs.1361509511e44adfba814f6950c6e742 	

Knoben, W. J. M., Clark, M. P., Bales, J., Bennett, A., Gharari, S., Marsh, C. B., Nijssen, B., Pietroniro, A., Spiteri, R. J., Tang, G., Tarboton, D. G., & Wood, A. W. (2022). Community Workflows to Advance Reproducibility in Hydrologic Modeling: Separating model-agnostic and model-specific configuration steps in applications of large-domain hydrologic models [Preprint]. Hydrology. https://doi.org/10.1002/essoar.10509195.2

Knoben, W. J. M., M. P. Clark, S. Gharari, G. Tang (2022a). Community Workflows to Advance Reproducibility in Hydrologic Modeling: Separating model-agnostic and model-specific configuration steps in applications of large-domain hydrologic models - Continental basin discretizations and river networks, HydroShare, https://doi.org/10.4211/hs.46d980a71d2c4365aa290dc1bfdac823

Lin, P., M. Pan, H. E., Beck, Y. Yang, D. Yamazaki, R. Frasson, C. H. David, M. Durand, T. M. Pavelsky, G. H. Allen, C. J. Gleason, and E. F. Wood, 2019: Global reconstruction of naturalized river flows at 2.94 million reaches. Water Resources Research, doi:10.1029/2019WR025287.

Mizukami, N., Clark, M. P., Sampson, K., Nijssen, B., Mao, Y., McMillan, H., Viger, R. J., Markstrom, S. L., Hay, L. E., Woods, R., Arnold, J. R., and Brekke, L. D., 2016: mizuRoute version 1: a river network routing tool for a continental domain water resources applications, Geosci. Model Dev., 9, 2223–2238, https://doi.org/10.5194/gmd-9-2223-2016

Yamazaki, D., Ikeshima, D., Sosa, J., Bates, P.D., Allen, G.H., Pavelsky, T.M., 2019. MERIT Hydro: A High‐Resolution Global Hydrography Map Based on Latest Topography Dataset. Water Resour. Res. 55, 5053–5073. https://doi.org/10.1029/2019WR024873
