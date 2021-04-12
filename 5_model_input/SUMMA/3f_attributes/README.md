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

## Downslope HRU index
The downslope HRU index can be used to specify how HRU-to-HRU drainage is organized within a given GRU. If this value is set to `0` for all HRUs in a given GRU, the HRUs are modelled as independent soil columns that do not share a groundwater reservoir. Runoff from all HRUs is aggregated to a single GRU-total timeseries, which can optionally be routed (within the GRU) if modeling decisions `subRouting` is set to `timeDlay` (which is the case in the default settings provided with this workflow). Although code is provided to automatically define values for `downHRUindex` based on each HRU's elevation, the `downHRUindex` value is only used when modeling decision `groundwatr` is set to `qTopmodl` which is **_currently not supported_** (see below).

## Model decision `qTopmodl`
SUMMA has the ability to simulate a GRU-wide aquifer if model decision `groundwatr` is set to `qTopmodel`. This requires for each HRU specification of the `downHRUindex`, `tan_slope` and `contourLength` variables. Both `tan_slope` and `contour_length` are set to **_default_** values in this iteration of the workflow because determining appropriate values for the `contourLength` variable is non-trivial in a generalized framework such as this workflow. It is therefore strongly recommended to not use the `qTopmodel` option with the files generated through this workflow. Results are unlikely to be meaningful.

## Assumptions not specified in `control_file.txt`
- Measurement height `mHeight` is fixed at 3 m.