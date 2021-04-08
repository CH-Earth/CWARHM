# Find mode land class

# Modules
import os
import numpy as np
from pathlib import Path
import scipy.stats as sc
from shutil import copyfile
from datetime import datetime
from osgeo import gdal, ogr, osr

# --- Control file handling
# Easy access to control file folder
controlFolder = Path('../../../0_control_files')

# Store the name of the 'active' file in a variable
controlFile = 'control_active.txt'

# Function to extract a given setting from the control file
def read_from_control( file, setting ):
    
    # Open 'control_active.txt' and ...
    with open(file) as contents:
        for line in contents:
            
            # ... find the line with the requested setting
            if setting in line:
                break
    
    # Extract the setting's value
    substring = line.split('|',1)[1]      # Remove the setting's name (split into 2 based on '|', keep only 2nd part)
    substring = substring.split('#',1)[0] # Remove comments, does nothing if no '#' is found
    substring = substring.strip()         # Remove leading and trailing whitespace, tabs, newlines
       
    # Return this value    
    return substring
    
# Function to specify a default path
def make_default_path(suffix):
    
    # Get the root path
    rootPath = Path( read_from_control(controlFolder/controlFile,'root_path') )
    
    # Get the domain folder
    domainName = read_from_control(controlFolder/controlFile,'domain_name')
    domainFolder = 'domain_' + domainName
    
    # Specify the forcing path
    defaultPath = rootPath / domainFolder / suffix
    
    return defaultPath
    

# --- Find source and destination locations
# Find where the soil classes are
landClassPath = read_from_control(controlFolder/controlFile,'parameter_land_tif_path')

# Specify the default paths if required 
if landClassPath == 'default':
    landClassPath = make_default_path('parameters/landclass/6_tif_multiband') # outputs a Path()
else:
    landClassPath = Path(landClassPath) # make sure a user-specified path is a Path()

# Find where the mode soil class needs to go
modeLandClassPath = read_from_control(controlFolder/controlFile,'parameter_land_mode_path')

# Specify the default paths if required 
if modeLandClassPath == 'default':
    modeLandClassPath = make_default_path('parameters/landclass/7_mode_land_class') # outputs a Path()
else:
    modeLandClassPath = Path(modeLandClassPath) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
modeLandClassPath.mkdir(parents=True, exist_ok=True)

# --- Filenames
# Find the name of the source file
for file in os.listdir(landClassPath):
    if file.endswith(".tif"):
        source_file = file

# New file
dest_file = read_from_control(controlFolder/controlFile,'parameter_land_tif_name')


# --- Function definition
# Opens geotif file, extracts data from a single band and computes corner & center coordinates in lat/lon
def open_geotif(file,band):
    
    # Do the things
    ds = gdal.Open(file) # open the file
    band = ds.GetRasterBand(band) # get the data band; there should be 18 for each of the 18 years
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

# ---  Find mode land class 
# Get land use classes for each year
land_use_classes = np.dstack((open_geotif( str(landClassPath/source_file) ,1)[0], \
                              open_geotif( str(landClassPath/source_file) ,2)[0], \
                              open_geotif( str(landClassPath/source_file) ,3)[0], \
                              open_geotif( str(landClassPath/source_file) ,4)[0], \
                              open_geotif( str(landClassPath/source_file) ,5)[0], \
                              open_geotif( str(landClassPath/source_file) ,6)[0], \
                              open_geotif( str(landClassPath/source_file) ,7)[0], \
                              open_geotif( str(landClassPath/source_file) ,8)[0], \
                              open_geotif( str(landClassPath/source_file) ,9)[0], \
                              open_geotif( str(landClassPath/source_file) ,10)[0], \
                              open_geotif( str(landClassPath/source_file) ,11)[0], \
                              open_geotif( str(landClassPath/source_file) ,12)[0], \
                              open_geotif( str(landClassPath/source_file) ,13)[0], \
                              open_geotif( str(landClassPath/source_file) ,14)[0], \
                              open_geotif( str(landClassPath/source_file) ,15)[0], \
                              open_geotif( str(landClassPath/source_file) ,16)[0], \
                              open_geotif( str(landClassPath/source_file) ,17)[0], \
                              open_geotif( str(landClassPath/source_file) ,18)[0]))

# Extract mode
mode = sc.mode(land_use_classes,axis=2)[0].squeeze()

# Store this in a new geotif file
src_file = str(landClassPath/source_file)
des_file = str(modeLandClassPath/dest_file)
write_geotif_sameDomain(src_file,des_file,mode)


# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = modeLandClassPath
log_suffix = '_mode_over_years_log.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = 'find_mode_landclass.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Found mode landclass over years']
    for txt in lines:
        file.write(txt) 

