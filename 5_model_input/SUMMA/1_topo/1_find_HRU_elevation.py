# Intersect catchment with MERIT DEM
# Finds the mean elevation of each HRU in the model setup with pyQGIS.
#
# Note:
# The pyQGIS function `QgsZonalStatistics` automatically adds the calculated value to the shapefile used as input to the function. The workflow is thus:
# 1. Find the source catchment shapefile;
# 2. Copy the source catchment shapefile to the destintion location;
# 3. Run the zonal statistics algorithm on the copy.

# modules
import os
from pathlib import Path
from shutil import which
from shutil import copyfile
from datetime import datetime
from qgis.core import QgsApplication
from qgis.core import QgsVectorLayer
from qgis.core import QgsRasterLayer
from qgis.analysis import QgsZonalStatistics


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
    
    
# --- Find location of shapefile and DEM
# Catchment shapefile path & name
catchment_path = read_from_control(controlFolder/controlFile,'catchment_shp_path')
catchment_name = read_from_control(controlFolder/controlFile,'catchment_shp_name')

# Specify default path if needed
if catchment_path == 'default':
    catchment_path = make_default_path('shapefiles/catchment') # outputs a Path()
else:
    catchment_path = Path(catchment_path) # make sure a user-specified path is a Path()
    
# DEM path & name
dem_path = read_from_control(controlFolder/controlFile,'parameter_dem_tif_path')
dem_name = read_from_control(controlFolder/controlFile,'parameter_dem_tif_name')

# Specify default path if needed
if dem_path == 'default':
    dem_path = make_default_path('parameters/dem/5_elevation') # outputs a Path()
else:
    dem_path = Path(dem_path) # make sure a user-specified path is a Path()
    
    
# --- Find where the intersection needs to go
# Intersected shapefile path and name
intersect_path = read_from_control(controlFolder/controlFile,'intersect_dem_path')
intersect_name = read_from_control(controlFolder/controlFile,'intersect_dem_name')

# Specify default path if needed
if intersect_path == 'default':
    intersect_path = make_default_path('shapefiles/catchment_intersection/with_dem') # outputs a Path()
else:
    intersect_path = Path(intersect_path) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
intersect_path.mkdir(parents=True, exist_ok=True)


# --- Copy the source catchment shapefile into the destination location
# Find the name without extension
catchment_base = catchment_name.replace('.shp','')

# Loop over directory contents and copy files that match the filename of the shape
for file in os.listdir(catchment_path):
    if catchment_base in file: # copy only the relevant files in case there are more than 1 .shp files
        
        # make the output file name
        _,ext = os.path.splitext(file)                    # extension of current file
        basefile,_ = os.path.splitext(intersect_name)     # name of the intersection file w/o extension
        newfile = basefile + ext                          # new name + old extension
        
        # copy
        copyfile(catchment_path/file, intersect_path/newfile);
        
        
# --- QGIS analysis
# Initialize QGIS
os.environ["QT_QPA_PLATFORM"] = "offscreen" # disable QT trying to connect to display; needed on HPC infrastructure
qgis_path = which('qgis') # find the QGIS install location
QgsApplication.setPrefixPath(qgis_path, True) # supply path to qgis install location
qgs = QgsApplication([], False) # create a reference to the QgsApplication, GUI = False
qgs.initQgis() # load providers

# Convert Path() to string for QGIS
catchment_file = str(intersect_path/intersect_name) # needs to be the copied file because output is automatically added to this
dem_file = str(dem_path/dem_name)

# Load the shape and raster
layer_polygon = QgsVectorLayer(catchment_file,'merit_hydro_basin','ogr')
layer_raster  = QgsRasterLayer(dem_file,'merit_hydro_dem')

# Check we loaded the layers correctly
if not layer_raster.isValid():
    print('Raster layer failed to load')
    
if not layer_polygon.isValid():
    print('Polygon layer failed to load')
    
# Create a zonal statistics object, automatically saved to file
band = 1 # raster band with the data we are after
zonalstats = QgsZonalStatistics(layer_polygon,                 # shapefile
                                layer_raster,                  # .tif
                                'elev_',                       # prefix for the new column added to the shapefile  
                                band,                          # raster band we're interested in
                                stats=QgsZonalStatistics.Mean).calculateStatistics(None)
                                
# Clean memory
qgs.exitQgis()

                                
# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = intersect_path
log_suffix = '_catchment_dem_intersect_log.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = '1_find_HRU_elevation.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()
# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Found mean HRU elevation from MERIT Hydro adjusted elevation DEM.']
    for txt in lines:
        file.write(txt)  
