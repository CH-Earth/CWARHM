# SUMMA vegetation parameters

## Noah-MP in SUMMA
SUMMA's approach to vegetation parameters is based on that of the Noah-MP land model and relies on look-up tables. Briefly, the user defines for each model element a representative vegetation type as a numerical value (e.g. "evergreen needleleaf forest" might be encoded as "1", "evergreen broadleaf forests" as "2", etc). SUMMA then navigates the look-up table to extract typical values of vegetation properties for the specified vegetation type and uses these values for further computations. 

SUMMA currently has several different look-up tables available in the file `TBL_VEGPARM.TBL` (found in the folder `5_model_input/SUMMA/0_base_settings`). This workflow assumes that the MODIFIED_IGBP_MODIS_NOAH table is used to define vegetation type index values (specified below). Vegetation classes are stored as SUMMA parameters in a variable called "vegTypeIndex", kept in "attributes.nc" (https://summa.readthedocs.io/en/latest/input_output/SUMMA_input/#attribute-and-parameter-files). 

Further details can be found in the Noah-MP documentation, see e.g.: https://ral.ucar.edu/solutions/products/noah-multiparameterization-land-surface-model-noah-mp-lsm


## Download setup instructions
The downloads require registration through NASA's EarthData website. See: https://urs.earthdata.nasa.gov/

Authentication is handled through Python's `requests` package. Store  user details (username and password) in a new file `$HOME/.netrc` (Unix/Linux) or `C:\Users\[user]\.netrc` (Windows) as follows (replace `[name]` and `[pass]` with your own credentials):

```
machine urs.earthdata.nasa.gov
login <USERNAME>
password <PASSWORD>

```
For details, see: https://lpdaac.usgs.gov/resources/e-learning/how-access-lp-daac-data-command-line/

**_Note: given that these passwords are stored as plain text, it is strongly recommended to use a unique password that is different from any other passwords you currently have in use._**


## GDAL requirements
MODIS data is provided in the HDF4 format. This format is not supported by certain GDAL distributions. Ensure your local GDAL install can work with HDF4. See e.g.:
- linux: https://gis.stackexchange.com/questions/135867/gdal-hdf4-driver-on-linux-system
- mac: https://stackoverflow.com/questions/45598772/binding-gdal-with-r-on-osx-mac-cant-open-explore-h4-files-in-r



## MODIS Land Cover Type Product (MCD12Q1) 
MODIS MCD12Q1 data (Friedl et al., 2019) are satellite data of global land cover classes at 500m resolution and are available for years 2001 to 2018. Raw satellite data has already been processed into various vegetation classifications. 

Main information page: https://lpdaac.usgs.gov/products/mcd12q1v006/

Land cover classes doc: https://lpdaac.usgs.gov/documents/101/MCD12_User_Guide_V6.pdf

Current validation status: Stage 2. Product accuracy has been assessed over a widely distributed set of locations and time periods via several ground-truth and validation efforts. (https://lpdaac.usgs.gov/products/mcd12q1v006/, 2020-05-19. Validation definitions: https://landweb.modaps.eosdis.nasa.gov/cgi-bin/QA_WWW/newPage.cgi?fileName=maturity)

#### Data use
Documentation strongly recommends *against* comparing land cover classes between years, due to uncertainty in the land cover determination procedure. We therefore use the most common land cover class across years 2001 to 2018 as the representative class for each grid cell.

#### Known issues
From the documentation:

- The "units" field is missing in the metadata, however, this information can be found in the table above or on page 5 of the User Guide.
- Areas of permanent sea ice are mapped as water if they are identifed as water according to the C6 Land/Water  mask  (Carroll  et  al.,  2009).   Some  land  areas,  for  example  glaciers  within  permanent topographic shadows, were mapped as water according to this mask, which introduces isolated errors in the product.
- Wetlands are under-represented.
- In  areas  of  the  tropics  where  cropland  field  sizes  tend  to  be  much  smaller  than  a  MODIS  pixel, agriculture is sometimes underrepresented (i.e., labeled as natural vegetation).
- Areas of temperate evergreen needleleaf forests are misclassified as broadleaf evergreen forests in Japan, the Pacific Northwest of North America, and Chile.  Similarly, areas of evergreen broadleaf forests are misclassified as evergreen needleleaf forests in Australia and parts of South America.
- Some grassland areas are classified as savannas (sparse forest).
- There is a glacier in Chile that is screened as if it were permanently cloud covered and is partially classified as grassland.


## MODIS to SUMMA
The  MCD12Q1 IGBP land cover classification matches existing SUMMA tables for 17/20 classes. The 3 different tundra classes are missing. See tables below. The workflow code downloads the MODIS data (global domain), subsets these to the modeling domain and finds a representative vegetation class for each model element. The vegetation class for each model element is saved in "attributes.nc", which is part of the SUMMA input files.


## IGBP vegetation classification table
This section shows the classification table as used for the MODIS data (https://lpdaac.usgs.gov/documents/101/MCD12_User_Guide_V6.pdf) and SUMMA's implementation of the table. Because both tables use the same order of classes, no remapping from one to the other is needed. Because classes are only identified numerically in SUMMA's input files, switching to different look-up tables or input data should be done with care.


### IGBP Table as used in MODIS
| Name                                  | Value | Description                                                                                              |
|---------------------------------------|-------|----------------------------------------------------------------------------------------------------------|
| Evergreen   Needleleaf Forests        | 1     | Dominated by   evergreen conifer trees (canopy>2m). Tree cover>60%.                                      |
| Evergreen   Broadleaf Forests         | 2     | Dominated by   evergreen broadleaf and palmatetrees (canopy>2m). Tree cover>60%.                         |
| Deciduous   Needleleaf Forests        | 3     | Dominated by   deciduous needleleaf (larch) trees(canopy>2m). Tree cover>60%.                            |
| Deciduous   Broadleaf Forests         | 4     | Dominated by   deciduous broadleaf trees (canopy>2m). Tree cover>60%                                     |
| Mixed   Forests                       | 5     | Dominated by neither   deciduous nor evergreen(40-60% of each) tree type (canopy>2m). Tree   cover>60%   |
| Closed   Shrublands                   | 6     | Dominated by woody   perennials (1-2m height)>60% cover.                                                 |
| Open   Shrublands                     | 7     | Dominated by woody   perennials (1-2m height)10-60% cover.                                               |
| Woody   Savannas                      | 8     | Tree cover 30-60%   (canopy>2m)                                                                          |
| Savannas                              | 9     | Tree cover 10-30%   (canopy>2m).                                                                         |
| Grasslands                            | 10    | Dominated by   herbaceous annuals (<2m).                                                                 |
| Permanent   Wetlands                  | 11    | Permanently   inundated lands with 30-60% watercover and>10% vegetated cover.                            |
| Croplands                             | 12    | At least 60% of area   is cultivated cropland.                                                           |
| Urban   and Built-up Lands            | 13    | At least 30%   impervious surface area includingbuilding materials, asphalt, and vehicles.               |
| Cropland/Natural   Vegetation Mosaics | 14    | Mosaics of   small-scale cultivation 40-60% withnatural tree, shrub, or herbaceous   vegetation          |
| Permanent   Snow and Ice              | 15    | At least 60% of area   is covered by snow and icefor at least 10 months of the year.                     |
| Barren                                | 16    | At least 60% of area   is non-vegetated barren(sand, rock, soil) areas with less than 10%   veg-etation. |
| Water   Bodies                        | 17    | At least 60% of area   is covered by permanent wa-ter bodies                                             |
| Unclassified                          | 255   | Has not received a   map label because of missinginputs                                                  |

## IGBP Table as currently implemented in SUMMA
Table name: "MODIFIED_IGBP_MODIS_NAOH"

| Value | Name                               |
|-------|------------------------------------|
| 1     | Evergreen Needleleaf Forest        |
| 2     | Evergreen Broadleaf Forest         |
| 3     | Deciduous Needleleaf Forest        |
| 4     | Deciduous Broadleaf Forest         |
| 5     | Mixed Forests                      |
| 6     | Closed Shrublands                  |
| 7     | Open Shrublands                    |
| 8     | Woody Savannas                     |
| 9     | Savannas'                          |
| 10    | Grasslands'                        |
| 11    | Permanent wetlands                 |
| 12    | Croplands'                         |
| 13    | Urban and Built-Up                 |
| 14    | cropland/natural vegetation mosaic |
| 15    | Snow and Ice                       |
| 16    | Barren or Sparsely Vegetate        |
| 17    | Water                              |
| 18    | Wooded Tundra                      |
| 19    | Mixed Tundra                       |
| 20    | Barren Tundra                      |



## References
Friedl, M., Sulla-Menashe, D. (2019). MCD12Q1 MODIS/Terra+Aqua Land Cover Type Yearly L3 Global 500m SIN Grid V006 [Data set]. NASA EOSDIS Land Processes DAAC. Accessed 2020-05-20 from https://doi.org/10.5067/MODIS/MCD12Q1.006






