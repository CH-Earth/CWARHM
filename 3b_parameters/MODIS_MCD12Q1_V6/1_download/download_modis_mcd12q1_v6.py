"""

Download MODIS MCD12Q1_V6

This script downloads all required MODIS data, approximately 5669 files with a total of 24.67 GB
Based on example provided on: https://git.earthdata.nasa.gov/projects/LPDUR/repos/daac_data_download_python/browse

***NOTE***
Requires a `.netrc` file in user's home directory with login credentials for `urs.earthdata.nasa.gov`.
See: https://lpdaac.usgs.gov/resources/e-learning/how-access-lp-daac-data-command-line/
"""

# Import Modules
import os,sys,glob
import time
import shutil
import requests
import concurrent
from concurrent.futures.thread import ThreadPoolExecutor
from netrc import netrc
from pathlib import Path
from shutil import copyfile
import subprocess

#Import local modules
from workflow_utility_functions import read_from_control,make_default_path, create_log_file
thisFile = os.path.basename(sys.argv[0])

# --- Control file handling
# Easy access to control file folder
controlFolder = Path('../../../0_control_files')

# Store the name of the 'active' file in a variable
controlFile = 'control_active.txt'

def request_get(file_url,output_file, usr, pwd):
    '''Function to request and download data, given user credentials'''

    try:
        res = requests.get(file_url, verify=True, stream=True, auth=(usr, pwd))

        # Decode the response
        res.raw.decode_content = True
        content = res.raw

        # Write to file
        with open(output_file, 'wb') as data:
            shutil.copyfileobj(content, data)

    except:
        logger.warning(f'File {file_url} was not downloaded correctly, on attempt {retries_cur} of {retires_max}')
        retries_cur += 1

    return None

def run_modis_download(file_list,usr,pwd,modis_path):
    '''Download the needed files using Threading'''

    with ThreadPoolExecutor() as executor:
        futures = []
        for file_url_raw in file_list:

            file_url = file_url_raw.strip()
            file_name = file_url.split('/')[-1].strip()  # Get the last part of the url, strip whitespace and characters

            #Check if file already exists  and move to next file if so
            if (modis_path / file_name).is_file():
                logger.debug(f'File {file_name} exists, skipping download')
            else:
                #Set the output file name, and submit the download request
                output_file = os.path.join(modis_path, file_name)
                futures.append(executor.submit(request_get, file_url, output_file, usr, pwd))

                logger.info(f'Downloading file: {file_name} from: {file_url}')

    return None

def download_check(file_list, modis_path,retries_cur):
    '''This function checks that all needed files are downloaded, and if not will try again '''

    check_folder = str(modis_path) + "/*.hdf"
    file_list_check = glob.glob(check_folder)

    file_list.sort()
    file_list_check.sort()

    if len(file_list) == len(file_list_check):
        logger.info(f'All required files have been downloaded')
        download_complete_bool = True
    else:
        logger.warning(f'Required files were not downloaded, another attempt will be made')
        download_complete_bool = False
        retries_cur += 1

    return download_complete_bool,retries_cur

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
    modis_path = make_default_path('parameters/landclass/1_MODIS_raw_data',controlFolder,controlFile) # outputs a Path()
else:
    modis_path = Path(modis_path) # make sure a user-specified path is a Path()
    
# Make output dir
modis_path.mkdir(parents=True, exist_ok=True)

# Set the log path and file name
logPath = modis_path
log_suffix = '_modis_download_'

# Create a log folder
logFolder = '_workflow_log'
Path(logPath / logFolder).mkdir(parents=True, exist_ok=True)

#Create a logging file
logger = create_log_file(logPath / logFolder,thisFile,suffix=log_suffix)

# Get the authentication info
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

logger.info('Downloading MODIS MCD12Q1_V6 data with global coverage.')

check_folder = str(modis_path)+"/*.hdf"
file_list_check = glob.glob(check_folder)

file_list.sort()
file_list_check.sort()

download_complete_bool = False
retries_cur = 1
retries_max = 10

"""This is the main download loop"""
while download_complete_bool == False:

    #Run download given complete list
    run_modis_download(file_list, usr, pwd, modis_path)
    #Check if number of files meets the length of the list
    download_complete_bool,retries_cur = download_check(file_list, modis_path,retries_cur)

    #Break when all files are downloaded
    if download_complete_bool == True:
        break

    #If there are too many retries, then break
    if retries_cur >= retries_max:
        logger.error(f'Maximum number of tries ({retries_max}) has been reached, aborting')
        break

# --- Code provenance
# Generates copies the control file and itself there.
#Copy the control file
copyfile(controlFolder / controlFile, logPath / logFolder / controlFile)
# Copy this script
copyfile(thisFile, logPath / logFolder / thisFile)


