# Script to automatically find the bounding box for a given shapefile. 
# Slightly rounds coordinates outward so that any cutouts based on these coordinates fully cover the modelling domain.

# Modules
import math
import geopandas as gpd
from pathlib import Path

# --- Control file handling
# Easy access to control file folder
controlFolder = Path('../0_control_files')
   
# Store the name of the 'active' file in a variable
controlFile = 'control_active.txt'

# Function to extract a given setting from the control file
def read_from_control( file, setting ):
    
    # Open 'control_active.txt' and ...
    for line in open(file):
        
        # ... find the line with the requested setting
        if setting in line:
            break
    
    # Extract the setting's value\n",
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

# --- Find spatial domain as bounding box of shapefile
# function to round coordinates of a bounding box to ERA5s 0.25 degree resolution
def round_bounding_box(coords):
    
    '''Assumes coodinates are an array: [lon_min,lat_min,lon_max,lat_max].
    Returns separate lat and lon vectors.'''
    
    # Extract values
    lon = [coords[0],coords[2]]
    lat = [coords[1],coords[3]]
    
    # Round to two decimals
    rounded_lon = [math.floor(lon[0]*100)/100, math.ceil(lon[1]*100)/100]
    rounded_lat = [math.floor(lat[0]*100)/100, math.ceil(lat[1]*100)/100]
    
    # Store as control file string
    control_string = '{}/{}/{}/{}'.format(rounded_lat[1],rounded_lon[0],rounded_lat[0],rounded_lon[1])
    
    return control_string, rounded_lat, rounded_lon

# Find name and location of catchment shapefile
shp_path = read_from_control(controlFolder/controlFile, 'catchment_shp_path')
shp_name = read_from_control(controlFolder/controlFile, 'catchment_shp_name')

# Specify default path if needed
if shp_path == 'default':
    shp_path = make_default_path('shapefiles/catchment')
else:
    shp_path = Path(shp_path)

# Open the shapefile
shp = gpd.read_file(shp_path/shp_name)

# Get the latitude and longitude of the bounding box
bounding_box = shp.total_bounds

# Find the rounded bounding box
coordinates,lat,lon = round_bounding_box(bounding_box)

# Print in ERA5 format
print('Specify coordinates as {}/{}/{}/{} in control file.'.format(lat[1],lon[0],lat[0],lon[1]))
