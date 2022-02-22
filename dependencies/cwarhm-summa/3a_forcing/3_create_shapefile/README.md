# Create ERA5 shapefile
The shapefile for the forcing data needs to represent the regular latitude/longitude grid of the ERA5 data. We need this for later intersection with the catchment shape(s) so we can create appropriately weighted forcing for each model element.

Notebook/script reads location of merged forcing data and the spatial extent of the data from the control file. 

## Assumptions not included in `control_active.txt`
- Code assumes that the merged forcing contains dimension variables with the names "latitude" and "longitude". This is the case for ERA5. 