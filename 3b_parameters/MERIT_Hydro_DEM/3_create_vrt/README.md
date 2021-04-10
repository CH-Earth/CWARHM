# Combine .geotiff tiles into .vrt
The MERIT Hydro DEM is composed of smaller .tif files that contain part of the global map. We need to combine these into a single map for further analysis.

## Virtual Dataset (VRT)
Gdal VRT's are "a mosaic of the list of input GDAL datasets" (https://gdal.org/programs/gdalbuildvrt.html). Essentially this stiches together the individual .tif files and allows further GDAL operations on the data.

## Scripts
### make_merit_dem_vrt.sh
Loops over the individual MERIT Hydro DEM folders (each folder represents a larger square of the Earth's surface, each file in a folder is a smaller square of data inside this larger square) and stiches those together into a single virtual data set. It only extracts band 1 which contains the surface elevation in [m] (see MERIT Hydro docs or use 'gdalinfo <path/to/merit/tif/file>').

## Input required
- Downloaded and extracted .tif files
- Location of the folder that contains these files
- Location and names for list of files output and vrt output

## Output generated
- GDAL .vrt files that contain the MERIT Hydro elevation data, stiched together into a single map.

## MERIT Hydro reference page
http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_Hydro/

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
