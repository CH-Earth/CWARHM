# SUMMA workflow
This repository contains scripts to install, set up and run the Structure for Unifying Multiple Modeling Alternatives (SUMMA, Clark et al., 2015a,b) and mizuRoute (Mizukami et al., 2016) to generate hydrologic simulations for a given domain. The workflow uses open-source data with global coverage to determine model parameters and forcing, thus enabling transparent and efficient hydrologic science.

A basic SUMMA+mizuRoute setup requires:
- Compiled executables for SUMMA and mizuRoute;
- A shapefile that discretizes the modelling domain into Grouped Responses Units (GRUs) and Hydrological Response Units (HRUs)
- A shapefile that discretizes the river network connecting the GRUs
- Time series of forcing data for each HRU
- A `.nc` file with parameter values for each HRU; the `attributes.nc` file;
- A `.nc` file with initial conditions for each HRU; the `coldState.nc` file;
- A `.nc` file that can be used to trial new parameter values without changing `attributes.nc` or any of the other parameter `.txt` files; the `trialParams.nc` file;

This workflow requires the user to provide the catchment and river network shapefiles with certain required contents (see the relevant readme's for details). The scripts in the repository provide all the necessary code to download and pre-process forcing and parameter data, create SUMMA's and mizuRoute's required input files, and run hydrologic and routing simulations. 


## Repository structure
This section gives a brief description of the contents and purpose of each folder.

### 0_controlFiles
Contains control files in which the user can specify folder locations for data downloads, model setting files and model simulations. Scripts in the `summaWorkflow_public` repository will look for the file 'control_active.txt' by default.

### 1_folderPrep
Contains code to set up the basic folder structure in the data directory specified in the control file. In particular, this generates the folders where shapefiles of the catchment(s) and river network need to go.

### 2_install
Contains scripts that create local clones of the SUMMA and mizuRoute GitHub repositories. Also contains scripts that show how both were compiled on the Unviersity of Saskatchewan's HPC cluster "Copernicus".





## Typical workflow
A typical application would look as follows:

1. Fork this repository to your own GitHub account and clone your fork into an arbitrary folder on your operating platform (e.g. local machine with Linux capabilities, a high performance cluster). 
2. Navigate to `summaWorkflow_public/0_controlFiles`. Copy and rename `control_template` to something more descriptive of your modeling domain.
3. Specify the folder where your data downloads etc need to go in your newly made control file.
4. Navigate to `summaWorkflow_public/1_folderPrep` and run the notebook or Python code there to create the basic layout of your data directory.
5. Copy your catchment and river network shapefiles (`.shp`) into the newly created `your/data/path/domain_[yourDomain]/shapefiles' folder, placing the shapefiles in the `catchment` and `river_network` folders respectively.




- Define the domain
	- Generate an HRU mask for the domain and assign HRU IDs
		- Specify lat/lon as part of the mask
		- Specify area as part of the mask
- Forcing
	- Download forcing data for the requested time period and spatial extent
	- Intersect forcing grid with HRU mask and create SUMMA-ready forcing files 
- Parameter data
	- Download and pre-process SOILGRIDS data
	- Download and pre-process MODIS XXX data
	- Download and pre-process MERIT Hydro DEM
- Create attributes.nc
	- Intersect elevation data with HRU mask
	- Intersect soilgrids data with HRU mask
	- Intersect modis veg data with HRU mask
	- Insert lat/long data from HRU mask
	- Insert hru_area from HRU mask
	- Set mHeight depending on the data (10m)
	- (Assuming HRU == GRU), set downHRUidx (0), hru2grudid (hru_id), hru_id (from HRU mask), gru_id (hru_id) 
	- (Assuming relevant parametrizations are not used) set slopeTypeId (1), contourLength (30m), tan_slope (0.1)
- Create coldstate.nc
- Create trialParams.nc


## Requirements
< Copy this from the paper >


## References
Clark, M. P., B. Nijssen, J. D. Lundquist, D. Kavetski, D. E. Rupp, R. A. Woods, J. E. Freer, E. D. Gutmann, A. W. Wood, L. D. Brekke, J. R. Arnold, D. J. Gochis, R. M. Rasmussen, 2015a: A unified approach for process-based hydrologic modeling: Part 1. Modeling concept. Water Resources Research, doi:10.1002/2015WR017198

Clark, M. P., B. Nijssen, J. D. Lundquist, D. Kavetski, D. E. Rupp, R. A. Woods, J. E. Freer, E. D. Gutmann, A. W. Wood, D. J. Gochis, R. M. Rasmussen, D. G. Tarboton, V. Mahat, G. N. Flerchinger, D. G. Marks, 2015b: A unified approach for process-based hydrologic modeling: Part 2. Model implementation and case studies. Water Resources Research, doi:10.1002/2015WR017200

Clark, M. P., B. Nijssen, J. D. Lundquist, D. Kavetski, D. E. Rupp, R. A. Woods, J. E. Freer, E. D. Gutmann, A. W. Wood, L. D. Brekke, J. R. Arnold, D. J. Gochis, R. M. Rasmussen, D. G. Tarboton, V. Mahat, G. N. Flerchinger, D. G. Marks, 2015c: The structure for unifying multiple modeling alternatives (SUMMA), Version 1.0: Technical Description. NCAR Technical Note NCAR/TN-514+STR, 50 pp., doi:10.5065/D6WQ01TD

Mizukami, N., Clark, M. P., Sampson, K., Nijssen, B., Mao, Y., McMillan, H., Viger, R. J., Markstrom, S. L., Hay, L. E., Woods, R., Arnold, J. R., and Brekke, L. D., 2016: mizuRoute version 1: a river network routing tool for a continental domain water resources applications, Geosci. Model Dev., 9, 2223–2238, https://doi.org/10.5194/gmd-9-2223-2016

## --- ##

## Repository structure
The repo is split between Model Agnostic (MA) steps and Model Specific (MS) steps. MA steps are general pre- and postprocessing steps that are independent of the model choice and thus can easily be integrated into the workflow of other models. Examples are download and quality control of input data.

MS steps are specific towards using SUMMA and are thus less generally applicable. Examples are downloading SUMMA source code and converting general forcing files into the specific configuration required by SUMMA.

The repository has the following folders:
- 0_MA_domain_specification: shapefiles for various domains or the code to generate them
- 0_MA_forcing: code to obtain and pre-process forcing data
- 0_MA_parameters: code to obtain and pre-process parameter data (soils, topography, land use)
- 0_MA_tools: generally useful code snippets
- 1_MS_summa_setup: code to download and compile SUMMA source code
- 2_MS_experiment_setup: code to prepare the necessary files for experiments with SUMMA
- 3_MS_model_runs: code to run the experiments
- 4_MA_output_evaluation: code to model outputs



# Temp stuff
## Temporary note on possible process-based evaluation structure
- Level 0 (sanity checks/laugh tests): do fluxes and states behave in a way that could feasibly be realistic?
  - Method: diagnostic plots
- Level 1 (model realism): does the model show behaviour that hydrologic theory tells us should be there?
  - Method: literature on snow/SWE; definition of theory-based metrics; calculation of said metrics for SNOTEL sites
- Level 2a (model performance comparison - lower benchmark): now we have realism-metrics, to what extent does our model outperform existing modelling efforts and/or simpler models?
  - Method: collect earlier modeling efforts; define baseline models (e.g. inter-annual monthly SWE mean); compare SUMMA simulations against both
- Level 2b (model performance comparison - upper benchmark): now we have realism-metrics, to what extent can our model still be improved in terms of input/output information content?
  - Method: use some form of ML approach to wrangle as much info as we can from the data; compare SUMMA to this




