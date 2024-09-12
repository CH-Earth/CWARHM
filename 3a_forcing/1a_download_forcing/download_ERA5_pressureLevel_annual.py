# modules
import cdsapi    # copernicus connection
import calendar  # to find days per month
import os        # to check if file already exists
import sys       # to handle command line arguments (sys.argv[0] = name of this file, sys.argv[1] = arg1, ...)
import math
from pathlib import Path
from shutil import copyfile
from datetime import datetime
import argparse

''' 
Downloads 1 year of ERA5 data as monthly chunks.
Usage: python download_ERA5_pressureLevel_annual.py <year> <coordinates> <path/to/save/data> 
'''

parser = argparse.ArgumentParser(description='Downloads 1 year of ERA5 data as monthly chunks')
parser.add_argument('--year', type = int, required=True)
parser.add_argument('--bounding-box', '-bb', type = str, help='Input north/east/south/west coordinates', required=True)
parser.add_argument('--forcing-path', '-fp', type = str, required=True)

args = parser.parse_args()

# Get the spatial coordinates as the second command line argument
bounding_box = args.bounding_box.split('/') # split string
bounding_box = [float(value) for value in bounding_box] # string to array

# Get the path as the second command line argument
forcingPath = Path(args.forcing_path) # string to Path()

# --- Convert the bounding box to download coordinates
# function to round coordinates of a bounding box to ERA5s 0.25 degree resolution
def round_coords_to_ERA5(coords):
    
    '''Assumes coodinates are an array: [lat_max,lon_min,lat_min,lon_max] (top-left, bottom-right).
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

# --- Start the month loop
for month in range (1,13): # this loops through numbers 1 to 12
       
    # find the number of days in this month
    daysInMonth = calendar.monthrange(args.year,month) 
        
    # compile the date string in the required format. Append 0's to the month number if needed (zfill(2))
    date = "{year}-{month}-01/to/{year}-{month}-{days}".format(year=args.year,
                                                               month=str(month).zfill(2), 
                                                               days=str(daysInMonth[1]).zfill(2))
       
    # compile the file name string
    file = forcingPath / ('ERA5_pressureLevel137_' + str(args.year) + str(month).zfill(2) + '.nc')

    # track progress
    print(f'Trying to download {date} into {file}')

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
                    'class': 'ea',
                    'expver': '1',
                    'stream': 'oper',
                    'type': 'an',
                    'levtype': 'ml',
                    'levelist': '137',
                    'param': '130/131/132/133',
                    'date': date,
                    'time': '00/to/23/by/1',
                    'area': coordinates,
                    'grid': '0.25/0.25', # Latitude/longitude grid: east-west (longitude) and north-south resolution (latitude).
                    'format'  : 'netcdf',
                }, file)
            
                # track progress
                print(f'Successfully downloaded {file}')

            except Exception as e:
                print(f'Error downloading {file} on try {retries_cur}')
                print(str(e))
                retries_cur += 1
                continue
            else:
                break