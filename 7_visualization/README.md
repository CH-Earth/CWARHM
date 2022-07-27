
# Visualization scripts
Scripts to produce the plots included in the paper "Community Workflows to Advance Reproducibility in Hydrologic Modeling: Separating model-agnostic and model-specific configuration steps in applications of large-domain hydrologic models". Brief description of each file is given below.


## 1. Graphic representation of SUMMA and mizuRoute shapefiles and associated terminology
- File: `1_mizuRoute_and_summa_shapefile.ipynb`
- Paper: Figure A1
- Description: Overview figure of SUMMA GRUs and HRUs on one side, and mizuRoute routing basins and river network on the other.


## 2. Graphic representation of forcing grid
- File: `2_ERA5_download_coordinates_and_catchment_shapefile.ipynb`
- Paper: Figure A5
- Description: Figure used to check if conversion of bounding box found in `control_active.txt` to ERA5 download coordinates works as it should. Also visualizes our assumption that ERA5 point data is representative for a grid cell.


## 3. Visualization of remapping of gridded forcing data to catchment polygons
- File: `3_forcing_grid_vs_catchment_averaged.ipynb`
- Paper: Figure A6
- Description: Figure showing an example of gridded forcing data (1 variable, 1 timestep) and the outcome of remapping this gridded data onto catchment polygons through weighted averaging. 


## 4. Visualization of temperature lapse rate application
- File: `4_temperature_lapse_rates.ipynb`
- Paper: Figure A7
- Description: Four-part figure showing (a) mean subbasin and forcing grid elevation; (b) temperature lapse rates based on the weighted difference between forcing grid and subbasin elevations; &#40;c) example of subbasin-averaged temperature forcing data before lapse rates are applied; (d) example of subbasin-averaged temperature forcing data after lapse rates are applied.


## 5. Visualization of remapping of geospatial parameter fields to catchment polygons
- File: `5_geospatial_parameters_to_model_elements.ipynb`
- Paper: Figure A8
- Description: Figure showing the three geospatial rasters (dem, soil classes, land classes) and the outcome of remapping this gridded data onto catchment polygons. Elevation data are remapped as a catchment-averaged value, land and soil classes are remapped as a majority value per catchment. 


## 6. Visualization of simulated variables on continental scale
- File: `6_SWE_SM_ET_Q_per_GRU.ipynb`
- Paper: Figure 5
- Description: Figure showing statistics calculated from SUMMA and mizuRoute simulations plotted for each subbasin and river reach in the North America domain. A HydroLAKES lake mask is plotted on top. Statistics were calculated and saved using the script `SUMMA_timeseries_to_statistics_parallel.py` found in the repository folder `./CWARHM/0_tools`. HydroLAKES v10 were downloaded on 2021-11-03 from: https://data.hydrosheds.org/file/hydrolakes/HydroLAKES_polys_v10_shp.zip. HydroLAKES main page: https://www.hydrosheds.org/products/hydrolakes


## 7. Visualization of simulated variables on local scale
- File: `7_SWE_and_streamflow_per_HRY.ipynb`
- Paper: Figure 6
- Description: Figure showing statistics calculated from SUMMA and mizuRoute simulations for each subbasin and river reach in a single plot, side-by-side with a plot of subbasin elevations for comparison purposes. Directly uses SUMMA and mizuRoute simulation outputs without any intermediate scripts (like the continental and global plotting code does).


## 8. Visualization of simulated variables on global scale
- Files: `8a_global_sims_to_stats.sh`, `8b_reproject_shapefiles.py`, `8c_global_summa_mean_ET.py`, `8d_global_summa_mean_Q.py`, `8e_global_mizuRoute_mean_IRF.py`
- Paper: Figure 4
- Description: Figure showing statistics calculated from SUMMA and mizuRoute simulations, plotted for each subbasin and river reach globally. A HydroLAKES lake mask is plotted on top (see header 6 for details). Due to the computational effort involved this procedure is split into multiple individual files. Simulation statistics were calculated and saved separately with script `8a_*`. Shapefiles were reprojected from EPSG:4326 (regular lat/lon) to ESRI:54030 (World Robinson) using script `8b_*`. Files `8c_*`, `8d_*` and `8e_*` contain the actual plotting code for global evapotranspiration simulations (SUMMA), global runoff simulations (SUMMA) and global streamflow simulations (mizuRoute) respectively. These three individual files were merged manually into a single one.



