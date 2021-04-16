# Script to download ERA5 geopotential data.
# Geopotential data can be converted into elevation, which is needed for temperature lapsing.

# modules
import cdsapi    # copernicus connection
import calendar  # to find days per month
import os        # to check if file already exists
import math
from pathlib import Path
from shutil import copyfile
from datetime import datetime


# --- Control file handling

# Easy access to control file folder
controlFolder = Path('../../0_control_files')

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
    
    
# --- Find where to save the data

# Find the path where the raw forcing needs to go
geoPath = read_from_control(controlFolder/controlFile,'forcing_geo_path')

# Specify the default paths if required
if geoPath == 'default':
    geoPath = make_default_path('forcing/0_geopotential')
else: 
    geoPath = Path(geoPath) # ensure Path() object 
    
# Make the folder if it doesn't exist
geoPath.mkdir(parents=True, exist_ok=True)


# --- Find spatial domain from control file

# Find the spatial extent the data needs to cover
bounding_box = read_from_control(controlFolder/controlFile,'forcing_raw_space') 
bounding_box = bounding_box.split('/') # split string
bounding_box = [float(value) for value in bounding_box] # string to array

# function to round coordinates of a bounding box to ERA5s 0.25 degree resolution
def round_coords_to_ERA5(coords):
    
    '''Assumes coodinates are an array: [lon_min,lat_min,lon_max,lat_max].
    Returns separate lat and lon vectors.'''
    
    # Extract values
    lon = [coords[1],coords[3]]
    lat = [coords[2],coords[0]]
    
    # Round to ERA5 0.25 degree resolution
    rounded_lon = [math.floor(lon[0]*4)/4, math.ceil(lon[1]*4)/4]
    rounded_lat = [math.floor(lat[0]*4)/4, math.ceil(lat[1]*4)/4]
    
    # Find if we are still in the representative area of a different ERA5 grid cell
    if lat[0] > rounded_lat[0]+0.125:
        rounded_lat[0] += 0.25
    if lon[0] > rounded_lon[0]+0.125:
        rounded_lon[0] += 0.25
    if lat[1] < rounded_lat[1]-0.125:
        rounded_lat[1] -= 0.25
    if lon[1] < rounded_lon[1]-0.125:
        rounded_lon[1] -= 0.25
    
    # Make a download string
    dl_string = '{}/{}/{}/{}'.format(rounded_lat[1],rounded_lon[0],rounded_lat[0],rounded_lon[1])
    
    return dl_string, rounded_lat, rounded_lon

# Find the rounded bounding box
coordinates,_,_ = round_coords_to_ERA5(bounding_box)


# --- Specify date to download

# Geopotential is part of the ERA5 "invariant" data, which are constant through time.
# Therefore, specify an arbitrary date to download
date = '2019-01-01'


# --- Download the data

# Specify a filename
file = geoPath / 'ERA5_geopotential.nc'

# if file doesn't yet exist, download the data
if not os.path.isfile(file):

    # Make sure the connection is re-tried if it fails
    retries_max = 10
    retries_cur = 1
    while retries_cur <= retries_max:
        try:
            
            # connect to Copernicus (requires .cdsapirc file in $HOME)
            c = cdsapi.Client()

            # specify and retrieve data
            c.retrieve('reanalysis-era5-complete', {    # do not change this!
                    'stream': 'oper',
                    'levtype': 'sf',
                    'param': '26/228007/27/28/29/30/43/74/129/160/161/162/163/172',
                    'date': date,
                    'time': '00',#/to/23/by/1',
                    'area': coordinates,
                    'grid': '0.25/0.25', # Latitude/longitude grid: east-west (longitude) and north-south resolution (latitude).
                    'format'  : 'netcdf',
                }, file)
            
            # track progress
            print('Successfully downloaded ' + str(file))

        except:
            print('Error downloading ' + str(file) + ' on try ' + str(retries_cur))
            retries_cur += 1
            continue
        else:
            break
            
            
# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Create a log folder
logFolder = '_era5_invariants_log'
Path( geoPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = 'download_ERA5_geopotential.py'
copyfile(thisFile, geoPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + '_pressure_level_log.txt'
with open( geoPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Downloaded ERA5 geopotential data for space (lat_max, lon_min, lat_min, lon_max) [{}].'.format(coordinates)]
    for txt in lines:
        file.write(txt) 