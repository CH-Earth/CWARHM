# SUMMA soil parameters
## Noah-MP in SUMMA
SUMMA's approach to soil parameters is based on that of the Noah-MP land model and relies on look-up tables. Briefly, the user defines for each model element a representative soil class as a numerical value (e.g. "sand" might be encoded as "1", "silty clay" as "11", etc). SUMMA then navigates the look-up table to extract typical values of hydraulic properties for the specified soil class and uses these values for further computations. 

SUMMA currently has several different look-up tables available in the file `TBL_SOILPARM.TBL` (found in the folder `5_model_input/SUMMA/0_base_settings`). This workflow assumes that the ROSETTA table is used to define soil class index values (specified below). Soil classes are stored as SUMMA parameters in a variable called "soilTypeIndex", kept in "attributes.nc" (https://summa.readthedocs.io/en/latest/input_output/SUMMA_input/#attribute-and-parameter-files). 

Further details can be found in the Noah-MP documentation, see e.g.: https://ral.ucar.edu/solutions/products/noah-multiparameterization-land-surface-model-noah-mp-lsm


## Download registration
Hydroshare downloads require registration through the Hydroshare website. See: https://www.hydroshare.org/sign-up/?next=

Hydroshare downloads use the Python package `hs_restclient`. Downloads require authentication through the client. Store  user details (username and password) in a new file `$HOME/.hydroshare` (Unix/Linux) or `C:\Users\[user]\.hydroshare` (Windows) as follows (replace `[name]` and `[pass]` with your own credentials):

```
name: [name]
pass: [pass]
```

**_Note: given that these passwords are stored as plain text, it is strongly recommended to use a unique password that is different from any other passwords you currently have in use._**


## SOILGRIDS data
The SOILGRIDS 250m data set (Hengl et al, 2017) provides values for various soil properties on a global scale. The data set uses machine learning and various local soil products to provide these soil property estimates. The SOILGRIDS native resolution is 250m x 250m, and soil properties are provided at 7 different depths for any given grid cell. 


## SOILGRIDS to SUMMA
SOILGRIDS does not provide soil classes directly. Instead we rely on the SOILGRIDS data fields that specify each location's sand, silt and clay percentage in the soil. We relate these percentages to soil classes through the USDA soil classification triangle (Benham et al, 2009). Then we define the most commonly occurring soil class for the 7 depth and choose that class as representative of the soil column at a given pixel. These preprocessing steps have already been completed and stored as a global map of soil classes on the Hydroshare repository (Knoben, 2021). The workflow code downloads this map and finds a representative soil class for each model element. The soil class for each model element is saved in "attributes.nc", which is part of the SUMMA input files.


## ROSETTA soil parameter table
This section records the ROSETTA soil parameter table that was used to define soil classes. Note that soil class numbering is arbitrary and the assigned soil classes thus only make sense in the context of how the classes were defined initially. In other words, this workflow assumes soil classes follow the numbering as given in this table. Other tables of soil properties might call "sand" class 12 instead of 1, and thus switching between soil tables needs to be done with care. This table is part of the parameter file `TBL_VEGPARM.TBL`.

| index | 'theta_res | theta_sat | vGn_alpha | vGn_n | k_soil   | BB   | DRYSMC | HC   | MAXSMC | REFSMC | SATPSI | SATDK    | SATDW    | WLTSMC | QTZ  | class           |
|-------|------------|-----------|-----------|-------|----------|------|--------|------|--------|--------|--------|----------|----------|--------|------|-----------------|
| 1     | 0.098      | 0.459     | -1.496    | 1.253 | 1.71E-06 | 1.4  | 0.068  | 1.09 | 0.482  | 0.412  | 0.405  | 1.28E-06 | 1.12E-05 | 0.286  | 0.25 | CLAY            |
| 2     | 0.079      | 0.442     | -1.581    | 1.416 | 9.47E-07 | 8.52 | 0.095  | 1.23 | 0.476  | 0.382  | 0.63   | 2.45E-06 | 1.13E-05 | 0.25   | 0.35 | CLAY LOAM       |
| 3     | 0.061      | 0.399     | -1.112    | 1.472 | 1.39E-06 | 5.39 | 0.078  | 1.21 | 0.451  | 0.329  | 0.478  | 6.95E-06 | 1.43E-05 | 0.155  | 0.4  | LOAM            |
| 4     | 0.049      | 0.39      | -3.475    | 1.746 | 1.22E-05 | 4.38 | 0.057  | 1.41 | 0.41   | 0.383  | 0.09   | 1.56E-04 | 5.14E-06 | 0.075  | 0.82 | LOAMY SAND      |
| 5     | 0.053      | 0.375     | -3.524    | 3.177 | 7.44E-05 | 4.05 | 0.045  | 1.47 | 0.395  | 0.236  | 0.121  | 1.76E-04 | 6.08E-07 | 0.068  | 0.92 | SAND            |
| 6     | 0.117      | 0.385     | -3.342    | 1.208 | 1.31E-06 | 0.4  | 0.1    | 1.18 | 0.426  | 0.338  | 0.153  | 2.17E-06 | 1.87E-05 | 0.219  | 0.52 | SANDY CLAY      |
| 7     | 0.063      | 0.384     | -2.109    | 1.33  | 1.53E-06 | 7.12 | 0.1    | 1.18 | 0.42   | 0.314  | 0.299  | 6.30E-06 | 9.90E-06 | 0.175  | 0.6  | SANDY CLAY LOAM |
| 8     | 0.039      | 0.387     | -2.667    | 1.449 | 4.43E-06 | 4.9  | 0.065  | 1.34 | 0.435  | 0.383  | 0.218  | 3.47E-05 | 8.05E-06 | 0.114  | 0.6  | SANDY LOAM      |
| 9     | 0.05       | 0.489     | -0.658    | 1.679 | 5.06E-06 | 5.3  | 0.034  | 1.27 | 0.485  | 0.383  | 0.786  | 7.20E-06 | 2.39E-05 | 0.179  | 0.1  | SILT            |
| 10    | 0.111      | 0.481     | -1.622    | 1.321 | 1.11E-06 | 0.4  | 0.07   | 1.15 | 0.492  | 0.404  | 0.49   | 1.03E-06 | 9.64E-06 | 0.283  | 0.1  | SILTY CLAY      |
| 11    | 0.09       | 0.482     | -0.839    | 1.521 | 1.29E-06 | 7.75 | 0.089  | 1.32 | 0.477  | 0.387  | 0.356  | 1.70E-06 | 2.37E-05 | 0.218  | 0.1  | SILTY CLAY LOAM |
| 12    | 0.065      | 0.439     | -0.506    | 1.663 | 2.11E-06 | 5.3  | 0.067  | 1.27 | 0.485  | 0.36   | 0.786  | 7.20E-06 | 2.39E-05 | 0.179  | 0.25 | SILT LOAM       |

## References
Benham, E., Ahrens, R. J., & Nettleton, W. D. (2009). Clarification of Soil Texture Class Boundaries. United States Department of Agriculture. https://www.nrcs.usda.gov/wps/portal/nrcs/detail/ks/soils/?cid=nrcs142p2_033171

Hengl T, Mendes de Jesus J, Heuvelink GBM, Ruiperez Gonzalez M, Kilibarda M, Blagotić A, et al. (2017) SoilGrids250m: Global gridded soil information based on machine learning. PLoS ONE 12(2): e0169748. doi:10.1371/journal.pone.0169748

Knoben, W. J. M. (2021). Global USDA-NRCS soil texture class map, HydroShare, https://doi.org/10.4211/hs.1361509511e44adfba814f6950c6e742 	


## Control file settings
This section lists all the settings in `control_active.txt` that the code in this folder uses.
- **parameter_soil_hydro_ID**: ID of the Hydroshare resource that contains the global soil texture class map needed by the download API
- **forcing_raw_space**: bounding box of the modelling domain, used to subset global data to the exact extent of the modelling domain
- **parameter_soil_raw_path, parameter_soil_domain_path**: file paths 
- **parameter_soil_tif_name**: name of the .tif that contains the soil classes for the domain