# Convert SOILGRIDS data to soil classes
Code to convert SOILGRIDS sand, silt and clay percentages into USDA soil classes. We use the USDA soil triangle definitions (Benham et al, 2009) to assign one of 12 possible soil classes to each combination of sand, silt and clay %. The classes are numbered according to the ROSETTA soil table shown in the primary readme of this part of the SUMMA workflow.

## Scripts
This folder contains the following scripts:
- convert_sandSiltClay_to_soilclass.py
- SOILGRIDS_to_soilclass_sl[1-7].sh
- submit_convertSoilclasses.sh

### convert_sandSiltClay_to_soilclass.py
Accepts a SOILGRIDS soil levels (e.g. "sl1") as a command line argument, loads the sand/silt/clay % data files for this soil level and converts the percentages to a USDA soil class. The command line argument can be used to submit jobs for different soil levels without having to modify the source code. Uses conditional arguments applied to the entire matrix to find the right soil class per pixel.

### SOILGRIDS_to_soilclass_sl[1-7].sh
Settings needed to submit the soilclass conversion on ComputeCanada's Graham.

### submit_convertSoilclasses.sh
Single script that submits the 7 different SOILGRIDS_to_soilclass_sl[1-7] files.

## Required inputs
- SOILGRIDS .tif files with sand, silt and clay percentages (can be sub-set for a specific domain but this is not required)
- Name and location of these SOILGRIDS files
- Soil level for which to do the conversion as a command line argument
- Name and location for the output files

## Generated outputs
Specified sand, silt, clay % data fields are converted into USDA soil classes, following the definitions outlined above and stored in .tif format in the specified output location.

## References
Benham, E., Ahrens, R. J., & Nettleton, W. D. (2009). Clarification of Soil Texture Class Boundaries. United States Department of Agriculture. https://www.nrcs.usda.gov/wps/portal/nrcs/detail/ks/soils/?cid=nrcs142p2_033171