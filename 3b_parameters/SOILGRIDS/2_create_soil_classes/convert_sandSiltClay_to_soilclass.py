# SOILGRIDS
# Downloaded sand/silt/clay content at the 7 soil depths provided by SOILGRIDS (Hengl et al., 2017). Use these fractions to determine the USDA soil class per depth (Benham et al., 2009).
#
# Workflow
#
# Combine separate sand/silt/clay percentages into a single soil class:
# 1. Define modules etc
# 2. Define file locations
# 	- Fixed location
# 	- Handle command line argument that specifies the soil depth
# 3. For each SOILGRIDS soil depth (sl1 to sl7) ...
# 	- Define functions used in the following steps
# 	- Open the CLYPPT_M_[sl]_250m, SLTPPT_M_[sl]_250m, SNDPPT_[sl]_250m .tif files and ...
# 		- Extract the geotif bands that contain sand/silt/clay %
# 	- Compare sand/silt/clay % to USDA soil triangle and assign soil class
#	- Save resulting soil class file as a new .tif
#
# References
# Hengl T, Mendes de Jesus J, Heuvelink GBM, Ruiperez Gonzalez M, Kilibarda M, Blagotic A, et al. (2017) SoilGrids250m: Global gridded soil information based on machine learning. PLoS ONE 12(2): e0169748. https://doi.org/10.1371/journal.pone.0169748
# Benham, E., Ahrens, R. J., & Nettleton, W. D. (2009). Clarification of Soil Texture Class Boundaries. United States Department of Agriculture. https://www.nrcs.usda.gov/wps/portal/nrcs/detail/ks/soils/?cid=nrcs142p2_033171

# 1. Define modules
import os
import sys 				# to handle command line arguments (sys.argv[0] = name of this file, sys.argv[1] = arg1, ...)
import numpy as np
import gdal
from pathlib import Path

# 2. Define file locations
# fixed
file_path = Path('/project/6008034/Model_Output/ClimateForcingData/SOILGRIDS_NA_rawData')
file_clay = 'CLYPPT_M_'
file_sand = 'SNDPPT_M_'
file_silt = 'SLTPPT_M_'
file_end = '_NA_250m_ll.tif'
file_path_des = Path('/project/6008034/Model_Output/ClimateForcingData/SOILGRIDS_NA_soilclasses/')
file_des = 'usda_soilclass_'

# command line argument
sl = str(sys.argv[1])

# Make the output directory
if not os.path.exists(file_path_des):
    os.makedirs(file_path_des)

# 3. Open SOILGRIDS and convert into soil classes
# define a few functions

# Start of function definition --------------------------------------------------------------------------
# Opens geotif file, extracts data from a single band and computes corner & center coordinates in lat/lon
def open_soilgrids_geotif(file):
    
    print('Opening ' + str(file))
    ds = gdal.Open(str(file)) # open the file; enforce string for gdal
    band = ds.GetRasterBand(1) # get the data band; we know there is only a single band per SOILGRIDS file
    data = band.ReadAsArray() # convert to numpy array for further manipulation
    width = ds.RasterXSize # pixel width
    height = ds.RasterYSize # pixel height
    gt = ds.GetGeoTransform() # geolocation
    coords = np.zeros((5,2)) # coordinates of bounding box
    coords[0,0] = coords[1,0] = gt[0]
    coords[0,1] = coords[2,1] = gt[3]
    coords[2,0] = coords[3,0] = gt[0] + width*gt[1]
    coords[1,1] = coords[3,1] = gt[3] + height*gt[5]
    coords[4,0] = gt[0] + (width/2)*gt[1]
    coords[4,1] = gt[3] + (height/2)*gt[5]
    
    return data, coords

# -------------------------------------------------------------------------------------------------------
# Takes sand/silt/clay percentage and returns USDA soil class
def find_usda_soilclass(sand,silt,clay,no_data_value):
    
    # Based on Benham et al., 2009 and matching the following soil class table:
    # SUMMA-ROSETTA-STAS-RUC soil parameter table
    # 1  'CLAY' 
    # 2  'CLAY LOAM'
    # 3  'LOAM' 
    # 4  'LOAMY SAND'
    # 5  'SAND'
    # 6  'SANDY CLAY'
    # 7  'SANDY CLAY LOAM'
    # 8  'SANDY LOAM'
    # 9  'SILT'
    # 10 'SILTY CLAY'
    # 11 'SILTY CLAY LOAM'
    # 12 'SILT LOAM'

    # Initialize a results array
    soilclass = np.zeros(sand.shape)
    
    # Legend
    soiltype = ['clay','clay loam','loam','loamy sand','sand','sandy clay','sandy clay loam','sandy loam','silt','silty clay','silty clay loam','silt loam']
    
    # Classify
    soilclass[(clay >= 40) & (sand <= 45) & (silt < 40)] = 1
    soilclass[(clay >= 27) & (clay < 40) & (sand > 20) & (sand <= 45)] = 2
    soilclass[(clay >= 7) & (clay < 27) & (silt >= 28) & (silt < 50) & (sand < 52)] = 3
    soilclass[((silt + 1.5 * clay) >= 15) & ((silt + 2* clay) < 30)] = 4
    soilclass[((silt + 1.5 * clay) < 15)] = 5
    soilclass[(clay >= 35 )& (sand > 45)] = 6
    soilclass[(clay >= 20) & (clay < 35) & (silt < 28) & (sand > 45)] = 7
    soilclass[((clay >= 7) & (clay < 20) & (sand > 52) & ((silt+2*clay) >= 30)) | ((clay < 7) & (silt < 50) & ((silt+2*clay >= 30)))] = 8
    soilclass[(silt >= 80) & (clay < 12)] = 9
    soilclass[(clay >= 40) & (silt >= 40)] = 10
    soilclass[(clay >= 27) & (clay < 40) & (sand <= 20)] = 11
    soilclass[((silt >= 50) & (clay >= 12) & (clay < 27)) | ((silt >= 50) & (silt < 80) & (clay < 12))] = 12  
    soilclass[(sand == no_data_value) | (silt == no_data_value) | (clay == no_data_value)] = 0
    
    return soilclass, soiltype

# -------------------------------------------------------------------------------------------------------
# Creates a new geotif file from a template file and data that needs to be saved
def create_new_tif(template_file, data, new_file_name):
    
    # Code based on shared code by S. Gharari (22-Apr-2020)
    
    # get stuff from the template
    ds = gdal.Open(str(template_file)) # open the file
    #band = ds.GetRasterBand(1) # get the band(s)
    #arr = band.ReadAsArray() # read the band array
    
    # get shape from the data
    [cols, rows] = data.shape # get the shape of the geotiff
    
    # create the new file
    driver = gdal.GetDriverByName("GTiff") # specify driver
    outdata = driver.Create(str(new_file_name), rows, cols, 1, gdal.GDT_UInt16, options = [ 'COMPRESS=DEFLATE' ]) # open file
    outdata.SetGeoTransform(ds.GetGeoTransform())# sets same geotransform as input
    outdata.SetProjection(ds.GetProjection())# sets same projection as input
    outdata.GetRasterBand(1).WriteArray(data) # pass the manipulated values 
    outdata.GetRasterBand(1).SetNoDataValue(-1)# if you want these values transparent (0) will be nan I guess
    outdata.FlushCache() # saves to disk!
    
    return 

# End of function definition ----------------------------------------------------------------------------


# For the specified soil depth ...
# Explicitly create the path
clay_path = file_path / (file_clay + sl + file_end)
sand_path = file_path / (file_sand + sl + file_end)
silt_path = file_path / (file_silt + sl + file_end)

# Get the geotif bands that contain sand/silt/clay and their coordinates
sand, sand_coord = open_soilgrids_geotif( sand_path )
silt, silt_coord = open_soilgrids_geotif( silt_path )
clay, clay_coord = open_soilgrids_geotif( clay_path )

# Break if coordinates do not match
coords_all_match = np.logical_and( (clay_coord == sand_coord).all(), (clay_coord == silt_coord).all())
if not coords_all_match:
    print('Coordinates do not match at soil level ' + sl + '. Aborting.')

# Specify the 'no data value' 
# Note: we know this is 255 from running 'gdalinfo [file] -mm' from the command line, there is no easy way to get this programmatically
# See: https://medium.com/planet-stories/a-gentle-introduction-to-gdal-part-1-a3253eb96082
noData = 255

# Compare sand/silt/clay % to USDA soil triangle and assign soil class
soilclass,_ = find_usda_soilclass(sand,silt,clay,noData)

# Save resulting soil class file as a new .tif, using an existing one as template
src = file_path / (file_clay + sl + file_end)
des = file_path_des / (file_des + sl + file_end)
create_new_tif(src,soilclass,des)

























