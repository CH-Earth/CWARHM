# SUMMA vegetation parameters
Based on the soil parameters work, the following questions can be of use in defining the workflow for this part of model set up:
- How are the Noah-MP vegetation tables that SUMMA uses organized?
	- Which vegetation classes are used in the NOAH-MP tables?
	- Which parameters does SUMMA currently use from the NOAH-MP lookup tables?
- Which data does MODIS Vegetation (or something else provide)?
- How do we go from MODIS to vegetation classes (if conversion is needed)?

## Noah-MP in SUMMA
SUMMA parameters (attributes.nc) include a variable called "vegTypeIndex" (https://summa.readthedocs.io/en/latest/input_output/SUMMA_input/#attribute-and-parameter-files). "vegTypeIndex" relates a representative vegetation index value for the model element to various parameters used in SUMMA. Some Noah-MP documentation can be accessed through UCAR: https://ral.ucar.edu/solutions/products/noah-multiparameterization-land-surface-model-noah-mp-lsm

Parameters actually used in SUMMA are:
- Currently difficult to find, because the variable names are short and show many occurrences with grep

## MODIS Vegetation
### MODIS Land Cover Type Product (MCD12Q1)
The  MCD12Q1 IGBP land cover classification matches existing SUMMA tables for 17/20 classes. The 3 different tundra classes are missing.

Provides various different classification schemes. If we can find lookup tables for them we can use these too.

Main information page: https://lpdaac.usgs.gov/products/mcd12q1v006/

Land cover classes doc: https://lpdaac.usgs.gov/documents/101/MCD12_User_Guide_V6.pdf

Current validation status: Stage 2. Product accuracy has been assessed over a widely distributed set of locations and time periods via several ground-truth and validation efforts. (https://lpdaac.usgs.gov/products/mcd12q1v006/, 2020-05-19. Validation definitions: https://landweb.modaps.eosdis.nasa.gov/cgi-bin/QA_WWW/newPage.cgi?fileName=maturity)

#### Description
Provides global land cover classes based on MODIS Terra and Aqua data:

- Temporal domain: annual between 2001-2018
- Spatial domain: global at 500m resolution

#### Data use
Documentation strongly recommends *against* comparing land cover classes between years, due to uncertainty in the land cover determination procedure. Probably best to use the most common land cover class across years 2001 to 2018 as the represntative class for each grid cell.

We'll use the IGBP classification for the moment, because that lets us use the existing lookup table within SUMMA. *NOTE*: current SUMMA IGBP look-up includes three different tundra classes that are not part of theMCD12Q1 data. We might need to revisit this.

#### Known issues
From the documentation:

- The "units" field is missing in the metadata, however, this information can be found in the table above or on page 5 of the User Guide.
- Areas of permanent sea ice are mapped as water if they are identifed as water according to the C6Land/Water  mask  (Carroll  et  al.,  2009).   Some  land  areas,  for  example  glaciers  within  permanenttopographic shadows, were mapped as water according to this mask, which introduces isolated errorsin the product.•Wetlands are under-represented.
- In  areas  of  the  tropics  where  cropland  field  sizes  tend  to  be  much  smaller  than  a  MODIS  pixel,agriculture is sometimes underrepresented (i.e., labeled as natural vegetation).
- Areas of temperate evergreen needleleaf forests are misclassified as broadleaf evergreen forests in Japan,the Pacific Northwest of North America, and Chile.  Similarly, areas of evergreen broadleaf forests aremisclassified as evergreen needleleaf forests in Australia and parts of South America.
- Some grassland areas are classified as savannas (sparse forest).
- There is a glacier in Chile that is screened as if it were permanently cloud covered and is partially classified as grassland.

#### Download
Bulk download via LP DAAC Data Pool and DAAC2DISK. Search and browse via USGS EarthExplorer and NASA Earthdata search.

#### Suggested citation (APA, Chicago)
Friedl, M., Sulla-Menashe, D. (2019). MCD12Q1 MODIS/Terra+Aqua Land Cover Type Yearly L3 Global 500m SIN Grid V006 [Data set]. NASA EOSDIS Land Processes DAAC. Accessed 2020-05-20 from https://doi.org/10.5067/MODIS/MCD12Q1.006

Friedl, M., D. Sulla-Menashe. MCD12Q1 MODIS/Terra+Aqua Land Cover Type Yearly L3 Global 500m SIN Grid V006. 2019, distributed by NASA EOSDIS Land Processes DAAC, https://doi.org/10.5067/MODIS/MCD12Q1.006. Accessed 2020-05-20.

### MODIS Land Cover Dynamics (MCD12Q2)
Provides vegetation dynamics. Might be useful if we want to move beyond lookup tables. 

Doc: https://landweb.modaps.eosdis.nasa.gov/QA_WWW/forPage/user_guide/MCD12Q2_Collection6_UserGuide.pdf

### MODIS Land Leaf Area Index (MOD15A2h, MYD15A2H; MCD15A2H, MCD15A3H)
Provides Leaf Area Index values.

Link: https://modis-land.gsfc.nasa.gov/lai.html

# Chris' suggestions for data handling
My first reaction is I would convert each to a geotiff, and the build [1] a vrt [2] of those tiled geotiffs. You may be able to skip the geotiff, I've never used vrt with anything but and am unsure if that's supported. The VRT skips having to have one comically massive file.
Then use gdalwarp to extract the area of interest [3]. You can try with a shape cutline [4] but I've found that to be very slow on large DEMs.
[1] https://gdal.org/programs/gdalbuildvrt.html
[2] https://gdal.org/drivers/raster/vrt.html
[3] https://gdal.org/programs/gdalwarp.html#cmdoption-gdalwarp-te
[4] https://gdal.org/programs/gdalwarp.html#cmdoption-gdalwarp-cutline

This suggests you can wrap the hdf directly with a vrt and then use warp/translate to cut out what you & reproject if needed
https://jgomezdans.github.io/stitching-together-modis-data.html

## IGBP Table as used in MODIS
Source: https://lpdaac.usgs.gov/documents/101/MCD12_User_Guide_V6.pdf

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

