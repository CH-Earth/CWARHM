# modules
import cdsapi    # copernicus connection
import calendar  # to find days per month
import os        # to check if file already exists
import sys       # to handle command line arguments (sys.argv[0] = name of this file, sys.argv[1] = arg1, ...)
from pathlib import Path

# Define the path
#path = Path('/project/6008034/Model_Output/ClimateForcingData/ERA5_NA_invariants/') # Graham
path = Path('/project/gwf/gwf_cmt/ERA5_NA_invariants')

# Make directory if doesn't exist
if not os.path.exists(path):
    os.makedirs(path)

# Download the data for a random year & month (because they are invariant, this doesn't matter)
year = 2019
month = 1
daysInMonth = 31

# compile the date string in the required format. Append 0's to the month number if needed (zfill(2))
date = str(year) + '-' + str(month).zfill(2) + '-01'

# Specify an output string
file = path / 'ERA5_NA_invariants.nc'

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
                    'area': '85/-180/5/-50',
                    'grid': '0.25/0.25', # Latitude/longitude grid: east-west (longitude) and north-south resolution (latitude).
                    'format'  : 'netcdf',
                }, file)
            
            # track progress
            print('Successfully downloaded ' + file)

        except:
            print('Error downloading ' + file + ' on try ' + str(retries_cur))
            retries_cur += 1
            continue
        else:
            break

