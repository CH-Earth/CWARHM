# HRU attributes
The local attributes contain mostly topographic information at the Hydrologic Response Unit level. These include:
1. Unique indices of hydrological response units (HRU)
2. Unique indices of grouped response units (GRU) 
3. Index of GRU to which the HRU belongs
4. Index of downslope HRU (i.e. organization of HRUs within a single GRU; 0 = basin outlet)
5. Longitude of HRU's centroid
6. Latitude of HRU's centroid
7. HRU area
8. HRU elevation
9. Index defining soil type
10. Index defining vegetation type

The file also includes the height at which the forcing data was measured/estimated, which is used in various scaling equations. The file further needs to include variables `tan_slope`, `contourLength` and `slopeTypeIndex` which are not used in the current version of the workflow. Items 1, 2, 3, 5, 6 and 7 should be provided in the catchment shapefile. Item 4 is set to `0` by default (see below). Items 8, 9 and 10 are obtained from the intersection between the catchment shapefile and the MERIT DEM, the SOILGRIDS-derived soil classes and the MERIT vegetation classes. See: https://summa.readthedocs.io/en/latest/input_output/SUMMA_input/#infile_local_attributes


## Groundwater parametrizations
SUMMA includes different ways to parametrize groundwater in cases where a GRU contains multiple HRUs. In a nutshell, these options are:
- Lateral connection between the soil columns of each HRU, where outflow from the lowest (outlet) HRU is equal to basin (i.e. GRU-wide) outflow. This is active when model decision `groundwatr` is `qTopmodl`.
- All HRUs drain into a shared (GRU-wide) aquifer, from which basin (i.e. GRU-wide) outflow is calculated. This is active when model decision `groundwatr` is `bigbuckt`.
- Groundwater is not explicitly parametrized and set to 0. This is active when model decision `groundwatr` is `noXplict`.

The standard `modelDecisions.txt` file provided in this workflow defines the groundwater as `bigBuckt`. Support for `qTopmodl` is planned for the future, but currently not feasible to implement. See below.


### Future support of model decision `qTopmodl`
SUMMA has the ability to simulate lateral connectivity between the soil columns of higher and lower HRUs if model decision `groundwatr` is set to `qTopmodel`. This requires for each HRU specification of the `downHRUindex`, `tan_slope` and `contourLength` variables. Both `tan_slope` and `contour_length` are set to **_default_** values in this iteration of the workflow because determining appropriate values for the `contourLength` variable is non-trivial in a generalized framework such as this workflow. It is therefore strongly recommended to not use the `qTopmodel` option with the files generated through this workflow. Results are unlikely to be meaningful.

The workflow already contains partial support for future inclusion of the `qTopmodel` decision in two key places:
- The workflow control file has an option `settings_summa_connect_HRUs` which can be used to change how the scripts in this folder generate the attributes `.nc` file. If set to `no`, the scripts set variable `downHRUindex` to `0` which indicates that each HRU should be treated as an independent soil column. In combination with model decision `bigBuckt`, this results in the HRUs in a given GRU having a shared aquifer from which baseflow is computed.
- The code that generates the attributes `.nc` file already has the capability to derive appropriate values for `downHRUindex` based on the relative elevation of each HRU in a given GRU. If `qTopmodl` is not used, `downHRUindex` should be set to `0`.



## Assumptions not specified in `control_file.txt`
- Measurement height `mHeight` is fixed at 3 m.