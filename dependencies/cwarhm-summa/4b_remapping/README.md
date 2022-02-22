# Mapping of preprocessed data onto model elements
Code to map preprocessed geospatial data and forcing data onto model elements. Remapping of forcing also includes the application of temperature lapse rates. This requires information on the forcing data source elevation (geopotential data, prepared during forcing preprocessing) and information on the elevation of each model element. Model element elevation is obtained from mapping preprocessed DEM data onto model elements. Mapping of the geospatial data thus needs to happen before the forcing is remapped onto model elements.

- `1_topo` includes scripts to map the prepared geospatial data (DEM, soil classes, vegetation types) to Hydrologic Response Units (HRUs);
- `2_forcing` includes scripts to map ERA5 gridded forcing to HRUs, apply temperature lapse rates and finalize the forcing `.nc` files for use by SUMMA. Preparing the forcing files for use by SUMMA is a minor step (it involves the addition of a single scalar variable to each forcing file that contains the time step size of the forcing data) and included here for efficiency. 

## Control file settings
Specified in each sub-folder.
