# Create SUMMA-ready forcing files

The scripts in this folder accomplish several goals:
- SUMMA expects its forcing inputs with dimensions `(hru,time)` meaning that we need to convert the downloaded ERA5 data from it's source dimensions `(lat,lon,time)` into SUMMA's required format. 
- The forcing data is given at grid points, which we initially assume are representative values for a grid cell that extends 0.125 degrees in the cardinal directions around the point. We have created a shapefile that outlines this grid as part of the forcing pre-processing. In this setup, SUMMA is run with catchments (and not over a grid), so we need to map the gridded forcing data to the catchments. 
- In our setup, the ERA5 grid cells are fairly large compared to the spatial extent of our catchment delineation. It is therefore unlikely that the raw ERA5 data is equally representative for all catchments. To somewhat account for the impact of topography on meteorological conditions, we apply a lapse rate of `0.0065` `[K m-1]` (Wallace and Hobbs, 2006) to the temperature data. 
Some further details are provided below. 


## Remapping of forcing data
We need to find how the ERA5 gridded forcing maps onto the catchment to create area-weighted forcing as SUMMA input. This involves two steps:
1. Intersect the ERA5 shape with the user's catchment shape to find the overlap between a given (sub) catchment and the forcing grid;
2. Create an area-weighted, catchment-averaged forcing time series.

The CANDEX package (https://github.com/ShervanGharari/candex_newgen) provides the necessary functionality to do this. CANDEX performs the GIS step (1, shapefile intersection) and the area-weighting step (2, create new forcing `.nc` files) as part of a single `run_candex()` call. To allow for parallelization, CANDEX can save the output from the GIS step into a restart `.csv` file which can be used to skip the GIS step. This allows (manual) parallelization of area-weighted forcing file generation after the GIS procedures have been run once. The workflow here is thus:
1. [Script 1] Call `run_candex()` with ERA5 and user's shapefile, and one ERA5 forcing `.nc` file;
    - CANDEX performs intersection of both shapefiles;
    - CANDEX saves the outcomes of this intersection to a `.csv` file;
    - CANDEX creates an area-weighted forcing file from a single provided ERA5 source `.nc` file
2. [Script 2] Call `run_candex()` with intersection `.csv` file and all other forcing `.nc` files.

Parallelization of step 2 (2nd `run_candex()` call) requires an external loop that sends (batches of) the remaining ERA5 raw forcing files to individual processors. As with other steps that may be parallelized, creating code that does this is left to the user.


## Temperature lapse rate
The size discrepancy between MERIT basins and the typical coverage of ERA5 grid cells makes it appropriate to apply a temperature lapse rate. Script 3 loops over existing basin-averaged forcing files and applies a lapse rate to the `airtemp` variable. Lapse rate is determined based on the average elevation difference between the basin shape and the ERA5 grid cell(s) that cover the basin. The lapse rate is set to `0.0065` `[K m-1]` (Wallace and Hobbs, 2006) as a global average value.


## Assumptions not included in `control_actve.txt`
The applied lapse rate is hard-coded in script 3. This is a globally average value that the script applies based on elevation differences only. Both the choice of value and methodology can be improved for local regions. We refer the user to the discussion in Wallace and Hobbs (2006).


## References
Wallace, J., and P. Hobbs (2006), Atmospheric Science: An Introductory Survey, 483 pp., Academic Press, Burlington, Mass