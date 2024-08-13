# Copy base settings
# Copies the base settings into the mizuRoute settings folder.

# modules
from pathlib import Path
from shutil import copyfile
from geopandas import gpd
import pandas as pd
import xarray as xr
import glob 
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
    
    
# --- Find where the shapefiles are

rootPath = Path( read_from_control(controlFolder/controlFile,'root_path') )
domainName = read_from_control(controlFolder/controlFile,'domain_name')

# CAMELS-spath
CAMELS_spath = read_from_control(controlFolder/controlFile,'camels_spath')

# Specify default path if needed
if CAMELS_spath == 'default':
    CAMELS_spath = rootPath / 'CAMELS-spat'
else:
    CAMELS_spath = Path(CAMELS_spath) # make sure a user-specified path is a Path()


shapefiles_path =  CAMELS_spath / domainName / 'shapefiles' / 'distributed'

river_file_name = domainName + '_distributed_river.shp'
catchment_file_name = domainName + '_distributed_basin.shp'

# --- Find where the river network will be
# River network shapefile path & name
river_network_path = read_from_control(controlFolder/controlFile,'river_network_shp_path')
river_network_name = read_from_control(controlFolder/controlFile,'river_network_shp_name')

# Specify default path if needed
if river_network_path == 'default':
    river_network_path = make_default_path('shapefiles/river_network') # outputs a Path()
else:
    river_network_path = Path(river_network_path) # make sure a user-specified path is a Path()



# --- Find where the river basin shapefile (routing catchments) will be

pd.options.mode.chained_assignment = None # Avoid warning: value is trying to be set on a copy of a slice from a DataFrame

# River network shapefile path & name
river_basin_path = read_from_control(controlFolder/controlFile,'river_basin_shp_path')
river_basin_name = read_from_control(controlFolder/controlFile,'river_basin_shp_name')

# Specify default path if needed
if river_basin_path == 'default':
    river_basin_path = make_default_path('shapefiles/river_basins') # outputs a Path()
else:
    river_basin_path = Path(river_basin_path) # make sure a user-specified path is a Path()
    
    
    
# --- Find where the catchment shapefile will be
# Catchment shapefile path & name
catchment_path = read_from_control(controlFolder/controlFile,'catchment_shp_path')
catchment_name = read_from_control(controlFolder/controlFile,'catchment_shp_name')

# Specify default path if needed
if catchment_path == 'default':
    catchment_path = make_default_path('shapefiles/catchment') # outputs a Path()
else:
    catchment_path = Path(catchment_path) # make sure a user-specified path is a Path()




# --- Modify the the river network shapefile for Mizuroute

shp_river_network = gpd.read_file( shapefiles_path / river_file_name )

shp_river_network = shp_river_network.assign(length = shp_river_network['lengthkm']*1000)
shp_river_network['length'][shp_river_network['length'] <= 0] = 1

# Function to compare if the values of set1 are in set2
def in4set(set1, set2):
    answer = list()
    for x in list(set1) :
        answer.append(x in list(set2))
    return(answer)

# Set the NextDownID of the downstream GRU to 0
max_value = max(shp_river_network['uparea'])
max_index = list(shp_river_network['uparea']).index(max_value)

shp_river_network['NextDownID'][max_index] = 0

shp_river_network.to_file(river_network_path / river_network_name)



# --- Modify the the river basin shapefile for MizuRoute


shp_river_basin = gpd.read_file( shapefiles_path / catchment_file_name )

shp_river_basin = shp_river_basin.assign(area = shp_river_basin['unitarea']*1000000)
shp_river_basin = shp_river_basin.assign(hru_to_seg = shp_river_basin['COMID'])


shp_river_basin.to_file(river_basin_path / river_basin_name)


# --- Modify the the catchment shapefile for SUMMA

shp_catchment = gpd.read_file( shapefiles_path / catchment_file_name )

shp_catchment = shp_catchment.assign(HRU_area = shp_catchment['unitarea']*1000000)
shp_catchment = shp_catchment.assign(HRU_ID = shp_catchment['COMID'])
shp_catchment = shp_catchment.assign(GRU_ID = shp_catchment['COMID'])


# Spatialisation
spa = 'distributed'

if spa == 'distributed':
    spa_name = 'dist' # name for forcing files
else:
    spa_name = spa

# Forcing path
forcing_path =  CAMELS_spath / domainName / 'forcing' / spa

# Forcing data product
forcing_data = read_from_control(controlFolder/controlFile,'forcing_data_name')

forcing_files = glob.glob(str(forcing_path / str(forcing_data + '*.nc')))


nc = xr.open_dataset(forcing_files[0])

lat = nc['latitude']
lon = nc['longitude']

shp_catchment = shp_catchment.assign(center_lat = lat)
shp_catchment = shp_catchment.assign(center_lon = lon)


shp_catchment.to_file(catchment_path / catchment_name)

    
    
# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = river_network_path / '..'
log_suffix = '_make_shapefiles.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = '1_make_shapefiles.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Adapt CAMELS-spat shapefiles for SUMMA and mizuRoute.']
    for txt in lines:
        file.write(txt) 