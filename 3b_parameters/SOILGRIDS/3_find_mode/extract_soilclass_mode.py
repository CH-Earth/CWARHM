# Modules
import numpy as np
import scipy.stats as sc
from pathlib import Path
from osgeo import gdal, ogr, osr

# File locations
file_path = Path('/project/6008034/Model_Output/ClimateForcingData/SOILGRIDS_NA_soilclasses')
file_base = 'usda_soilclass_'
file_end = '_NA_250m_ll.tif'
file_dest = 'usda_mode_soilclass_vCompressed'

# auxiliary functions
# -------------------------------------------------------------
# Opens geotif file, extracts data from a single band and computes corner & center coordinates in lat/lon
def open_soilgrids_geotif(file):
    
    # Do the things
    ds = gdal.Open(file) # open the file
    band = ds.GetRasterBand(1) # get the data band; we know there is only a single band per SOILGRIDS file
    data = band.ReadAsArray() # convert to numpy array for further manipulation
    width = ds.RasterXSize # pixel width
    height = ds.RasterYSize # pixel height
    rasterSize = [width,height]
    geoTransform = ds.GetGeoTransform() # geolocation
    boundingBox = np.zeros((5,2)) # coordinates of bounding box
    boundingBox[0,0] = boundingBox[1,0] = geoTransform[0]
    boundingBox[0,1] = boundingBox[2,1] = geoTransform[3]
    boundingBox[2,0] = boundingBox[3,0] = geoTransform[0] + width*geoTransform[1]
    boundingBox[1,1] = boundingBox[3,1] = geoTransform[3] + height*geoTransform[5]
    boundingBox[4,0] = geoTransform[0] + (width/2)*geoTransform[1]
    boundingBox[4,1] = geoTransform[3] + (height/2)*geoTransform[5]
    
    return data, geoTransform, rasterSize, boundingBox

# -------------------------------------------------------------
# Writes data into a new geotif file
# Source: https://gis.stackexchange.com/questions/199477/gdal-python-cut-geotiff-image/199565
def write_geotif_sameDomain(src_file,des_file,des_data):
    
    # load the source file to get the appropriate attributes
    src_ds = gdal.Open(src_file)
    
    # get the geotransform
    des_transform = src_ds.GetGeoTransform()
    
    # get the data dimensions
    ncols = des_data.shape[1]
    nrows = des_data.shape[0]
    
    # make the file
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(des_file,ncols,nrows,1,gdal.GDT_Float32, options = [ 'COMPRESS=DEFLATE' ])
    dst_ds.GetRasterBand(1).WriteArray( des_data ) 
    dst_ds.SetGeoTransform(des_transform)
    wkt = src_ds.GetProjection()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)
    dst_ds.SetProjection( srs.ExportToWkt() )
    
    # close files
    src_ds = None
    des_ds = None

    return

# -------------------------------------------------------------

# Get soil classes for all soil levels
soilclasses = np.dstack((open_soilgrids_geotif(str(file_path / (file_base + 'sl1' + file_end)))[0], \
                         open_soilgrids_geotif(str(file_path / (file_base + 'sl2' + file_end)))[0], \
                         open_soilgrids_geotif(str(file_path / (file_base + 'sl3' + file_end)))[0], \
                         open_soilgrids_geotif(str(file_path / (file_base + 'sl4' + file_end)))[0], \
                         open_soilgrids_geotif(str(file_path / (file_base + 'sl5' + file_end)))[0], \
                         open_soilgrids_geotif(str(file_path / (file_base + 'sl6' + file_end)))[0], \
                         open_soilgrids_geotif(str(file_path / (file_base + 'sl7' + file_end)))[0]))

# Extract mode
mode = sc.mode(soilclasses,axis=2)[0].squeeze()

# Store this in a new geotif file
src_file = str(file_path / (file_base + 'sl1' + file_end))
des_file = str(file_path / (file_dest + file_end))
write_geotif_sameDomain(src_file,des_file,mode)

