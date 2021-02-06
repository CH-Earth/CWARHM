# modules
import cdsapi    # copernicus connection
import calendar  # to find days per month
import os        # to check if file already exists
import sys       # to handle command line arguments (sys.argv[0] = name of this file, sys.argv[1] = arg1, ...)

# Get the year we're downloading from commandline argument
year = int(sys.argv[1])

# Define the path
path = '/project/gwf/gwf_cmt/ERA5_NA_rawData/'

# Start the month loop
# Use calendar to find how many days a given month has
# Print the first day and last day of the month like; '1979-01-01/to/1979-01-31'

for month in range (1,13): # this loops through numbers 1 to 12
       
    # find the number of days in this month
    daysInMonth = calendar.monthrange(year,month) 
        
    # compile the date string in the required format. Append 0's to the month number if needed (zfill(2))
    date = str(year) + '-' + str(month).zfill(2) + '-01/to/' + \
        str(year) + '-' + str(month).zfill(2) + '-' + str(daysInMonth[1]).zfill(2) 
        
    # compile the file name string
    file = path + 'ERA5_pressureLevel137_' + str(year) + str(month).zfill(2) + '.nc'

    # track progress
    print('Trying to download ' + date + ' into ' + file)

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