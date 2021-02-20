# Combine .hdf into .vrt
The satellite data is composed of small .hdf files that contain part of the global map. We need to combine these into a single map (per year of data) for further analysis.

## Virtual Dataset (VRT)
Gdal VRT's are "a mosaic of the list of input GDAL datasets" (https://gdal.org/programs/gdalbuildvrt.html). Essentially this stiches together the individual .hdf files and allows further GDAL operations on the data.

## Scripts
### make_vrt_per_year.sh
Loops over years 2001 to 2018, creates a list of MODIS tiles for the given year and stiches those together into a single virtual data set for each year. It extracts only sub dataset 1, i.e. the IBGP classification sub dataset (see MODIS docs or use 'gdalinfo <path/to/modis/hdf/file>').

## Input required
- Downloaded .hdf files
- Location of the folder that contains these files
- Location and names for list of files output and vrt output

## Output generated
- GDAL .vrt files that contain the MODIS data for year X, stiched together into a single map.

## Notes
- Python can read .vrt files (source: https://jgomezdans.github.io/stitching-together-modis-data.html)

```
import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal

g = gdal.Open ( "mosaic_sinu.vrt" ) # Open file
data = g.ReadAsArray() # Read contents
mdata = np.ma.array ( data, mask=data>30000 ) # Mask data
cmap = plt.cm.jet # Set colormap
cmap.set_bad ( 'k' ) # Set masked values to black
# Next line scales the GPP data by 0.0001 to get the right units
# and plots it.
plt.imshow ( mdata*0.0001, interpolation='nearest', vmax=0.007, cmap=cmap)
plt.colorbar ( orientation='horizontal' )
```
