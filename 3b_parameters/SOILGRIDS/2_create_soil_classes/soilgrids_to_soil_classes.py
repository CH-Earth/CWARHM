# SOILGRIDS to soil classes
# We have downloaded sand/silt/clay content at the 7 soil depths provided by SOILGRIDS v2 (data available, paper in pre; SOILGRIDS v1: Hengl et al., 2017). We'll use these fractions to determine the USDA soil class per depth (Benham et al., 2009).

# Sand, silt and clay values are in units `[g/kg]`. 

# Assumes files are name `clay_[depth]_[var]`, `sand_[depth]_[var]` and `silt_[detph]_[var]`, where `[var]` is the download variable and `[depth]` is one of `0-5cm`, `5-15cm`, `15-30cm`, `30-60cm`, `60-100cm` or `100-200cm`.

# References
# Hengl T, Mendes de Jesus J, Heuvelink GBM, Ruiperez Gonzalez M, Kilibarda M, Blagotic A, et al. (2017) SoilGrids250m: Global gridded soil information based on machine learning. PLoS ONE 12(2): e0169748. https://doi.org/10.1371/journal.pone.0169748
#
# Benham, E., Ahrens, R. J., & Nettleton, W. D. (2009). Clarification of Soil Texture Class Boundaries. United States Department of Agriculture. https://www.nrcs.usda.gov/wps/portal/nrcs/detail/ks/soils/?cid=nrcs142p2_033171

# Modules
import os
import gdal
import numpy as np
from pathlib import Path
from shutil import copyfile
from datetime import datetime

# --- Control file handling
# Easy access to control file folder
controlFolder = Path('../../../0_controlFiles')

# Store the name of the 'active' file in a variable
controlFile = 'control_active.txt'

# Function to extract a given setting from the control file
def read_from_control( file, setting ):
    
    # Open 'control_active.txt' and ...
    for line in open(file):
        
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
# Find where the downloads are
rawSoilPath = read_from_control(controlFolder/controlFile,'parameter_soil_raw_path')

# Find where the soil classes need to go
soilClassPath = read_from_control(controlFolder/controlFile,'parameter_soil_class_path')

# Specify the default paths if required 
if rawSoilPath == 'default':
    rawSoilPath = make_default_path('parameters/soilclass/1_SOILGRIDS_raw_data') # outputs a Path()
else:
    rawSoilPath = Path(rawSoilPath) # make sure a user-specified path is a Path()
    
# Specify the default paths if required 
if soilClassPath == 'default':
    soilClassPath = make_default_path('parameters/soilclass/2_usgs_soil_classes') # outputs a Path()
else:
    soilClassPath = Path(soilClassPath) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
soilClassPath.mkdir(parents=True, exist_ok=True)


# --- Find source files
# Find where the downloads are
soil_variable = read_from_control(controlFolder/controlFile,'parameter_soil_value')

# Specify the other parts of the file names
file_clay = 'clay_'
file_sand = 'sand_'
file_silt = 'silt_'
file_end  = '_' + soil_variable + '.tif'
depths    = ['0-5cm', '5-15cm', '15-30cm', '30-60cm', '60-100cm', '100-200cm']
file_des  = 'usda_soilclass_' # prefix of the new files


# --- Function definitions
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
    
# Takes sand/silt/clay percentage and returns USDA soil class
def find_usda_soilclass(sand,silt,clay):
    
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

    # Ensure that locations that have all zeroes do not get assigned a class
    soilclass[(sand == 0) & (silt == 0) & (clay == 0)] = 0 
    
    return soilclass, soiltype
    
# Creates a new geotif file from a template file and data that needs to be saved
def create_new_tif(template_file, data, new_file_name):
    
    # Code based on shared code by S. Gharari (22-Apr-2020)
    
    # get stuff from the template
    ds = gdal.Open(str(template_file)) # open the file
    
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
    

# --- Find soil classes
# Loop over the soil depths
for depth in depths:
    
    # Explicitly create the path
    clay_path = rawSoilPath / (file_clay + depth + file_end)
    sand_path = rawSoilPath / (file_sand + depth + file_end)
    silt_path = rawSoilPath / (file_silt + depth + file_end)
    
    # Get the geotif bands that contain sand/silt/clay and their coordinates
    sand, sand_coord = open_soilgrids_geotif( sand_path )
    silt, silt_coord = open_soilgrids_geotif( silt_path )
    clay, clay_coord = open_soilgrids_geotif( clay_path )
    
    # Break if coordinates do not match
    coords_all_match = np.logical_and( (clay_coord == sand_coord).all(), (clay_coord == silt_coord).all())
    if not coords_all_match:
        print('Coordinates do not match at soil level ' + sl + '. Aborting.')
        
    # Convert the [g/kg] values into [%]
    sand = sand / 10
    silt = silt / 10
    clay = clay / 10
    
    # Compare sand/silt/clay % to USDA soil triangle and assign soil class
    soilclass,_ = find_usda_soilclass(sand,silt,clay)
    
    # Save resulting soil class file as a new .tif, using an existing one as template
    src = rawSoilPath / (file_clay + depth + file_end)
    des = soilClassPath / (file_des + depth + file_end)
    create_new_tif(src,soilclass,des)
    
    
# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.
# Set the log path and file name
logPath = soilClassPath
log_suffix = '_soilgrids_to_soilclass_log.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = 'soilgrids_to_soil_classes.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Converted SOILGRIDS v2 data into soil classes (Benham et al., 2009)\n',
             'Benham, E., Ahrens, R. J., & Nettleton, W. D. (2009). Clarification of Soil Texture Class Boundaries. United States Department of Agriculture. https://www.nrcs.usda.gov/wps/portal/nrcs/detail/ks/soils/?cid=nrcs142p2_033171']
    for txt in lines:
        file.write(txt) 