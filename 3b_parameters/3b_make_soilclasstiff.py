# Modules
import numpy as np
import scipy.stats as sc
from pathlib import Path
from osgeo import gdal, osr
from shutil import copyfile
from datetime import datetime

# --- Control file handling
# Easy access to control file folder
controlFolder = Path('../0_control_files')

# Store the name of the 'active' file in a variable
controlFile = 'control_active.txt'

# Function to extract a given setting from the control file
def read_from_control( file, setting ):
    
    # Open 'control_active.txt' and ...
    with open(file) as contents:
        for line in contents:
            
            # ... find the line with the requested setting
            if setting in line and not line.startswith('#'):
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
    
    

# --- Find where the soil will be

parameter_soil_domain_path = read_from_control(controlFolder/controlFile,'parameter_soil_domain_path')

# Specify default path if needed
if parameter_soil_domain_path == 'default':
    parameter_soil_domain_path = make_default_path('parameters/soilclass/2_soil_classes_domain') # outputs a Path()
else:
    parameter_soil_domain_path = Path(parameter_soil_domain_path) # make sure a user-specified path is a Path()


file_base = 'soil_classes_'
file_end = '_mean.tif'
file_dest = 'soil_classes'

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

    return

# -------------------------------------------------------------

# Get soil classes for all soil levels
soilclasses = np.dstack((open_soilgrids_geotif(str(parameter_soil_domain_path / (file_base + '0-5cm' + file_end)))[0], \
                         open_soilgrids_geotif(str(parameter_soil_domain_path / (file_base + '5-15cm' + file_end)))[0], \
                         open_soilgrids_geotif(str(parameter_soil_domain_path / (file_base + '15-30cm' + file_end)))[0], \
                         open_soilgrids_geotif(str(parameter_soil_domain_path / (file_base + '30-60cm' + file_end)))[0], \
                         open_soilgrids_geotif(str(parameter_soil_domain_path / (file_base + '60-100cm' + file_end)))[0], \
                         open_soilgrids_geotif(str(parameter_soil_domain_path / (file_base + '100-200cm' + file_end)))[0]))

# Extract mode
mode = sc.mode(soilclasses,axis=2)[0].squeeze()

# Store this in a new geotif file
src_file = str(parameter_soil_domain_path / (file_base + '0-5cm' + file_end))
des_file = str(parameter_soil_domain_path / (file_dest + '.tif'))
write_geotif_sameDomain(src_file,des_file,mode)



# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = parameter_soil_domain_path
log_suffix = '_make_soilclasstiff.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = '3b_make_soilclasstiff.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Aggregate the information to create soil class tiff']
    for txt in lines:
        file.write(txt) 