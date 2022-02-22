# Download MODIS MCD12Q1_V6
# Script based on example provided on: https://git.earthdata.nasa.gov/projects/LPDUR/repos/daac_data_download_python/browse
# Requires a `.netrc` file in user's home directory with login credentials for `urs.earthdata.nasa.gov`. See: https://lpdaac.usgs.gov/resources/e-learning/how-access-lp-daac-data-command-line/

# modules
import os
import time
import shutil
import requests
from netrc import netrc
from pathlib import Path
from shutil import copyfile
from datetime import datetime


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
    
    
# --- Get the download settings
# Path and name of file with download links
links_path = read_from_control(controlFolder/controlFile,'parameter_land_list_path')
links_file = read_from_control(controlFolder/controlFile,'parameter_land_list_name')

# Specify the default paths if required 
if links_path == 'default':
    links_path = Path('./') # outputs a Path()
else:
    links_path = Path(links_path) # make sure a user-specified path is a Path()
    
# Find where the data needs to go
modis_path = read_from_control(controlFolder/controlFile,'parameter_land_raw_path')

# Specify the default paths if required 
if modis_path == 'default':
    modis_path = make_default_path('parameters/landclass/1_MODIS_raw_data') # outputs a Path()
else:
    modis_path = Path(modis_path) # make sure a user-specified path is a Path()
    
# Make output dir
modis_path.mkdir(parents=True, exist_ok=True)


# --- Get the authentication info
# authentication url
url = 'urs.earthdata.nasa.gov'

# make the netrc directory
netrc_folder = os.path.expanduser("~/.netrc")

# Get user name and password - not great, but these are stored as plain text on the user's machine regardless..
usr = netrc(netrc_folder).authenticators(url)[0]
pwd = netrc(netrc_folder).authenticators(url)[2]


# --- Do the downloads
# Get the download links from file
file_list = open(links_file, 'r').readlines()

# Retry settings: connection can be unstable, so specify a number of retries
retries_max = 100 

# Loop over the download files
for file_url in file_list:
    
    # Make the file name
    file_name = file_url.split('/')[-1].strip() # Get the last part of the url, strip whitespace and characters
    
    # Check if file already exists (i.e. interupted earlier download) and move to next file if so
    if (modis_path / file_name).is_file():
        continue 
        
    # Make sure the connection is re-tried if it fails
    retries_cur = 1
    while retries_cur <= retries_max:
        try:
            # Send a HTTP request to the server and save the HTTP response in a response object called resp
            # 'stream = True' ensures that only response headers are downloaded initially (and not all file contents too, which are 2GB+)
            with requests.get(file_url.strip(), verify=True, stream=True, auth=(usr,pwd)) as response:
        
                # Decode the response
                response.raw.decode_content = True
                content = response.raw        
        
                # Write to file
                with open(modis_path / file_name, 'wb') as data:
                    shutil.copyfileobj(content, data)
            
                # Progress
                print('Successfully downloaded: {}'.format(file_name))
                time.sleep(3) # sleep for a bit so we don't overwhelm the server
                
        except:
            print('Error downloading ' + file_name + ' on try ' + str(retries_cur))
            retries_cur += 1
            continue
        else:
            break  
        

# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = modis_path
log_suffix = '_modis_download_log.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = 'download_modis_mcd12q1_v6.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Downloaded MODIS MCD12Q1_V6 data with global coverage.']
    for txt in lines:
        file.write(txt) 