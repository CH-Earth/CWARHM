# Download MERIT Hydro adjusted elevation data
#
# Data source: http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_DEM/index.html. Download requires the user to be registered, which can be done through the website
#
# Workflow:
# - Find data locations;
# - Determine the files that need to be downloaded to cover the modelling domain;
# - Download data.

# Modules
from datetime import datetime
from shutil import copyfile
from pathlib import Path
import numpy as np
import requests
import shutil
import os


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
    
    
# --- Find where to save the files
# Find the path where the raw files need to go
merit_path = read_from_control(controlFolder/controlFile,'parameter_dem_raw_path')

# Specify the default paths if required 
if merit_path == 'default':
    merit_path = make_default_path('parameters/dem/1_MERIT_raw_data') # outputs a Path()
else:
    merit_path = Path(merit_path) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
merit_path.mkdir(parents=True, exist_ok=True)


# --- Find the download area and which MERIT packages cover this area
# Get the download url info
merit_url = read_from_control(controlFolder/controlFile,'parameter_dem_main_url')
merit_template = read_from_control(controlFolder/controlFile,'parameter_dem_file_template')

# Find which locations to download
coordinates = read_from_control(controlFolder/controlFile,'forcing_raw_space')

# Split coordinates into the format the download interface needs
coordinates = coordinates.split('/')

# Store coordinates as floats in individual variables
domain_min_lon = np.array(float(coordinates[1]))
domain_max_lon = np.array(float(coordinates[3]))
domain_min_lat = np.array(float(coordinates[2]))
domain_max_lat = np.array(float(coordinates[0]))

# Define the edges of the download areas
lon_right_edge  = np.array([-150,-120, -90,-60,-30,  0,30,60,90,120,150,180])
lon_left_edge   = np.array([-180,-150,-120,-90,-60,-30, 0,30,60, 90,120,150])
lat_bottom_edge = np.array([-60,-30,0, 30,60]) # NOTE: latitudes -90 to -60 are NOT part of the MERIT domain
lat_top_edge    = np.array([-30,  0,30,60,90]) 

# Define the download variables
dl_lon_all = np.array(['w180','w150','w120','w090','w060','w030','e000','e030','e060','e090','e120','e150'])
dl_lat_all = np.array(['s60','s30','n00','n30','n60'])

# Find the lower-left corners of each download square
dl_lons = dl_lon_all[(domain_min_lon < lon_right_edge) & (domain_max_lon > lon_left_edge)]
dl_lats = dl_lat_all[(domain_min_lat < lat_top_edge) & (domain_max_lat > lat_bottom_edge)]


# --- Get authentication info
# Open the login details file and store as a dictionary
merit_login = {}
with open(os.path.expanduser("~/.merit")) as file:
    for line in file:
        (key, val) = line.split(':')
        merit_login[key] = val.strip() # remove whitespace, newlines
        
# Get the authentication details
usr = merit_login['user']
pwd = merit_login['pass']


# --- Do the downloads
# Retry settings
retries_max = 10

# Loop over the download files
for dl_lon in dl_lons:
    for dl_lat in dl_lats:
        
        # Skip those combinations for which no MERIT data exists
        if (dl_lat == 'n00' and dl_lon == 'w150') or \
           (dl_lat == 's60' and dl_lon == 'w150') or \
           (dl_lat == 's60' and dl_lon == 'w120'):
            continue
        
        # Make the download URL
        file_url = (merit_url + merit_template).format(dl_lat,dl_lon)
        
        # Extract the filename from the URL
        file_name = file_url.split('/')[-1].strip() # Get the last part of the url, strip whitespace and characters
        
        # If file already exists in destination, move to next file
        if os.path.isfile(merit_path / file_name):
            continue
            
        # Make sure the connection is re-tried if it fails
        retries_cur = 1
        while retries_cur <= retries_max:
            try: 

                # Send a HTTP request to the server and save the HTTP response in a response object called resp
                # 'stream = True' ensures that only response headers are downloaded initially (and not all file contents too, which are 2GB+)
                with requests.get(file_url.strip(), auth=(usr, pwd), stream=True) as response:
    
                    # Decode the response
                    response.raw.decode_content = True
                    content = response.raw
    
                    # Write to file
                    with open(merit_path / file_name, 'wb') as data:
                        shutil.copyfileobj(content, data)

                    # print a completion message
                    print('Successfully downloaded ' + file_url)

            except:
                print('Error downloading ' + file_url + ' on try ' + str(retries_cur))
                retries_cur += 1
                continue
            else:
                break
                
                
# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = merit_path
log_suffix = '_merit_dem_download_log.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = 'download_merit_hydro_adjusted_elevation.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Downloaded MERIT Hydro adjusted elevation for area (lat_max, lon_min, lat_min, lon_max) [{}].'.format(coordinates)]
    for txt in lines:
        file.write(txt) 