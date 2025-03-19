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
# References
# Hengl T, Mendes de Jesus J, Heuvelink GBM, Ruiperez Gonzalez M, Kilibarda M, Blagotic A, et al. (2017) SoilGrids250m: Global gridded soil information based on machine learning. PLoS ONE 12(2): e0169748. https://doi.org/10.1371/journal.pone.0169748
# Benham, E., Ahrens, R. J., & Nettleton, W. D. (2009). Clarification of Soil Texture Class Boundaries. United States Department of Agriculture. https://www.nrcs.usda.gov/wps/portal/nrcs/detail/ks/soils/?cid=nrcs142p2_033171

import pandas as pd
import numpy as np
from osgeo import gdal
from pathlib import Path
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
    
    
# --- Find where the soil is

rootPath = Path( read_from_control(controlFolder/controlFile,'root_path') )
domainName = read_from_control(controlFolder/controlFile,'domain_name')

# CAMELS-spath
CAMELS_spath = read_from_control(controlFolder/controlFile,'camels_spath')

# Specify default path if needed
if CAMELS_spath == 'default':
    CAMELS_spath = rootPath / 'CAMELS-spat'
else:
    CAMELS_spath = Path(CAMELS_spath) # make sure a user-specified path is a Path()
    
# Metadata
metadata_path = CAMELS_spath
metadata_name = "camels-spat-metadata.csv"

df_metadata = pd.read_csv(metadata_path / metadata_name)


country, station_id = domainName.split("_")

# Get categories 
category_value = df_metadata.loc[(df_metadata['Country'] == country) & (df_metadata['Station_id'] == station_id), 'subset_category']

# Ensure category_value is a string
if not category_value.empty:
    category_value = category_value.iloc[0]  # Convert Series to string
else:
    raise ValueError("No matching subset category found.")  # Handle missing value    

# Soil
soil_file_path =  CAMELS_spath / 'geospatial' / category_value / 'soilgrids' / domainName

file_clay = domainName + '_clay_'
file_sand = domainName + '_sand_'
file_silt = domainName + '_silt_'
file_end = '_mean.tif'

# --- Find where the soil will be

parameter_soil_domain_path = read_from_control(controlFolder/controlFile,'parameter_soil_domain_path')

# Specify default path if needed
if parameter_soil_domain_path == 'default':
    parameter_soil_domain_path = make_default_path('parameters/soilclass/2_soil_classes_domain') # outputs a Path()
else:
    parameter_soil_domain_path = Path(parameter_soil_domain_path) # make sure a user-specified path is a Path()

# Make the folder if it doesn't exist
parameter_soil_domain_path.mkdir(parents=True, exist_ok=True)
file_des = 'soil_classes_'
sl_list = ["0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"]


# --- Open SOILGRIDS and convert into soil classes
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
    soilclass[(clay >= 400) & (sand <= 450) & (silt < 400)] = 1
    soilclass[(clay >= 270) & (clay < 400) & (sand > 200) & (sand <= 450)] = 2
    soilclass[(clay >= 70) & (clay < 270) & (silt >= 280) & (silt < 500) & (sand < 520)] = 3
    soilclass[((silt + 15 * clay) >= 150) & ((silt + 2* clay) < 300)] = 4
    soilclass[((silt + 15 * clay) < 150)] = 5
    soilclass[(clay >= 350 )& (sand > 450)] = 6
    soilclass[(clay >= 200) & (clay < 350) & (silt < 280) & (sand > 450)] = 7
    soilclass[((clay >= 70) & (clay < 200) & (sand > 520) & ((silt+2*clay) >= 300)) | ((clay < 70) & (silt < 500) & ((silt+2*clay >= 300)))] = 8
    soilclass[(silt >= 800) & (clay < 120)] = 9
    soilclass[(clay >= 400) & (silt >= 400)] = 10
    soilclass[(clay >= 270) & (clay < 400) & (sand <= 200)] = 11
    soilclass[((silt >= 500) & (clay >= 120) & (clay < 270)) | ((silt >= 500) & (silt < 800) & (clay < 120))] = 12  
    soilclass[(sand == no_data_value) | (silt == no_data_value) | (clay == no_data_value)] = 0
    
    return soilclass, soiltype

# -------------------------------------------------------------------------------------------------------
# Creates a new geotif file from a template file and data that needs to be saved
def create_new_tif(template_file, data, new_file_name):
    
    # Code based on: https://gis.stackexchange.com/questions/164853/reading-modifying-and-writing-a-geotiff-with-gdal-in-python
    
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

# End of function definition ----------------------------------------------------------------------------


for sl in sl_list:

    # For the specified soil depth ...
    # Explicitly create the path
    clay_path = soil_file_path / (file_clay + sl + file_end)
    sand_path = soil_file_path / (file_sand + sl + file_end)
    silt_path = soil_file_path / (file_silt + sl + file_end)
    
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
    noData = -32768
    
    # Compare sand/silt/clay % to USDA soil triangle and assign soil class
    soilclass,_ = find_usda_soilclass(sand,silt,clay,noData)
    
    # Save resulting soil class file as a new .tif, using an existing one as template
    src = soil_file_path / (file_clay + sl + file_end)
    des = parameter_soil_domain_path / (file_des + sl + file_end)
    create_new_tif(src,soilclass,des)



# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = parameter_soil_domain_path
log_suffix = '_convert_sandSiltClay_to_soilclass.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = '3a_convert_sandSiltClay_to_soilclass.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Copy CAMELS-spat soil information to current workflow and convert it to soilclass']
    for txt in lines:
        file.write(txt) 





















