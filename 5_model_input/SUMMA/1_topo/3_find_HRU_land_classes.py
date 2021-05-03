# Intersect catchment with MODIS-derived IGBP land classes
# Counts the occurence of each land class in each HRU in the model setup with pyQGIS.

# Modules
import os
from pathlib import Path
from shutil import which
from shutil import copyfile
from datetime import datetime
from qgis.core import QgsApplication
from qgis.core import QgsVectorLayer
from qgis.core import QgsRasterLayer
from qgis.core import QgsProcessingFeedback
from qgis.analysis import QgsNativeAlgorithms


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
    
    
# --- Find location of shapefile and land class .tif
# Catchment shapefile path & name
catchment_path = read_from_control(controlFolder/controlFile,'catchment_shp_path')
catchment_name = read_from_control(controlFolder/controlFile,'catchment_shp_name')

# Specify default path if needed
if catchment_path == 'default':
    catchment_path = make_default_path('shapefiles/catchment') # outputs a Path()
else:
    catchment_path = Path(catchment_path) # make sure a user-specified path is a Path()
    
# Forcing shapefile path & name
land_path = read_from_control(controlFolder/controlFile,'parameter_land_mode_path')
land_name = read_from_control(controlFolder/controlFile,'parameter_land_tif_name')

# Specify default path if needed
if land_path == 'default':
    land_path = make_default_path('parameters/landclass/7_mode_land_class') # outputs a Path()
else:
    land_path = Path(land_path) # make sure a user-specified path is a Path()
    
    
# --- Find where the intersection needs to go
# Intersected shapefile path and name
intersect_path = read_from_control(controlFolder/controlFile,'intersect_land_path')
intersect_name = read_from_control(controlFolder/controlFile,'intersect_land_name')

# Specify default path if needed
if intersect_path == 'default':
    intersect_path = make_default_path('shapefiles/catchment_intersection/with_modis') # outputs a Path()
else:
    intersect_path = Path(intersect_path) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
intersect_path.mkdir(parents=True, exist_ok=True)


# --- Initialize QGIS connection
qgis_path = which('qgis') # find the QGIS install location
QgsApplication.setPrefixPath(qgis_path, True) # supply path to qgis install location

# Now import the processing toolbox
import processing # QGIS algorithm runner

# Import all native QGIS algorithms
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms());


# --- QGIS analysis
# Convert Path() to string for QGIS
catchment_file = str(catchment_path/catchment_name)
land_file      = str(land_path/land_name)

# Load the shape and raster
layer_polygon = QgsVectorLayer(catchment_file,'merit_hydro_basin','ogr')
layer_raster  = QgsRasterLayer(land_file,'modis_land_classes')

# Check we loaded the layers correctly
if not layer_raster.isValid():
    print('Raster layer failed to load')
    
if not layer_polygon.isValid():
    print('Polygon layer failed to load')
    
# Specify the parameters for the zonalHistogram function
band = 1 # raster band with the data we are after
params = { 'COLUMN_PREFIX': 'IGBP_',
           'INPUT_RASTER' : layer_raster, 
           'INPUT_VECTOR' : layer_polygon, 
           'OUTPUT'       : str(intersect_path/intersect_name), 
           'RASTER_BAND'  : band }
           
# Run the zonalHistogram
res = processing.run("native:zonalhistogram", params)


# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = intersect_path
log_suffix = '_catchment_modis_intersect_log.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = '3_find_HRU_land_classes.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Counted the occurrence of IGBP land classes within each HRU.']
    for txt in lines:
        file.write(txt) 
