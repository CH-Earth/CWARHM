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
    date = str(year) + '-' + str(month).zfill(2) + '-01/' + \
        str(year) + '-' + str(month).zfill(2) + '-' + str(daysInMonth[1]).zfill(2) 
        
    # compile the file name string
    file = path + 'ERA5_surface_' + str(year) + str(month).zfill(2) + '.nc'

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
                c.retrieve(
                    'reanalysis-era5-single-levels',
                    {
                        'product_type': 'reanalysis',
                        'format': 'netcdf',
                        'variable': [
                            'mean_convective_precipitation_rate', 
                            'mean_convective_snowfall_rate', 
                            'mean_large_scale_precipitation_rate',
                            'mean_large_scale_snowfall_rate', 
                            'mean_surface_downward_long_wave_radiation_flux',                
                            'mean_surface_downward_short_wave_radiation_flux',
                            'mean_total_precipitation_rate', 
                            'surface_pressure',
                        ],
                        'date': date,
                        'time': '00/to/23/by/1',
                        'area': '85/-180/5/-50',	# North, West, South, East. Default: global
                    	        		        # Latitude/longitude grid: east-west (longitude) and north-south

                    },
                    file) # file path and name

                # track progress
                print('Successfully downloaded ' + file)

            except:
                print('Error downloading ' + file + ' on try ' + str(retries_cur))
                retries_cur += 1
                continue
            else:
                break