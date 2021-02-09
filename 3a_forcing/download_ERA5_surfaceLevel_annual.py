# modules
import cdsapi    # copernicus connection
import calendar  # to find days per month
import os        # to check if file already exists
import sys       # to handle command line arguments (sys.argv[0] = name of this file, sys.argv[1] = arg1, ...)
from pathlib import Path
from shutil import copyfile
from datetime import datetime

''' 
Downloads 1 year of ERA5 data as monthly chunks.
Usage: python download_ERA5_surfaceLevel_annual.py <year> <coordinates> <path/to/save/data> 
'''

# Get the year we're downloading from command line argument
year = int(sys.argv[1]) # arguments are string by default; string to integer

# Get the spatial coordinates as the second command line argument
coordinates = sys.argv[2] # string

# Get the path as the second command line argument
forcingPath = Path(sys.argv[3]) # string to Path()

# Start the month loop
for month in range (1,13): # this loops through numbers 1 to 12
       
    # find the number of days in this month
    daysInMonth = calendar.monthrange(year,month) 
        
    # compile the date string in the required format. Append 0's to the month number if needed (zfill(2))
    date = str(year) + '-' + str(month).zfill(2) + '-01/' + \
        str(year) + '-' + str(month).zfill(2) + '-' + str(daysInMonth[1]).zfill(2) 
        
    # compile the file name string
    file = forcingPath / ('ERA5_surface_' + str(year) + str(month).zfill(2) + '.nc')

    # track progress
    print('Trying to download ' + date + ' into ' + str(file))

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
                c.retrieve(
                    'reanalysis-era5-single-levels',
                    {
                        'product_type': 'reanalysis',
                        'format': 'netcdf',
                        'variable': [
                            'mean_surface_downward_long_wave_radiation_flux',                
                            'mean_surface_downward_short_wave_radiation_flux',
                            'mean_total_precipitation_rate', 
                            'surface_pressure',
                        ],
                        'date': date,
                        'time': '00/to/23/by/1',
                        'area': coordinates,	# North, West, South, East. Default: global
                    	'grid': '0.25/0.25',    # Latitude/longitude grid: east-west (longitude) and north-south
                    },
                    file) # file path and name

                # track progress
                print('Successfully downloaded ' + str(file))

            except:
                print('Error downloading ' + str(file) + ' on try ' + str(retries_cur))
                retries_cur += 1
                continue
            else:
                break