# Script to subset a smaller lat/lon region from a larger one. 
#  Reads the region of interest from control_active.txt
#  Assumes we're after raw ERA5 data and reads the output location from control_active.txt

from pathlib import Path
import math
import xarray as xr

# Specify the input file(s)
in_base       = '/project/6008034/CompHydCore/climateForcingData/ERA5/ERA5_for_SUMMA/'
inout_paths   = ['1_ERA5_raw_data',                 '1_ERA5_raw_data',          '0_geopotential']
in_files      = ['ERA5_pressureLevel137_197901.nc', 'ERA5_surface_197901.nc',   'ERA5_geopotential.nc']
control_names = ['forcing_raw_path',                'forcing_raw_path',         'forcing_geo_path']


# --- Control file handling

# Easy access to control file folder
controlFolder = Path('../0_control_files')

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


# --- Define coordinates of interest

# Find the spatial extent the data needs to cover
bounding_box = read_from_control(controlFolder/controlFile,'forcing_raw_space') 
bounding_box = bounding_box.split('/') # split string
bounding_box = [float(value) for value in bounding_box] # string to array

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
    
    # Make outputs
    lon_min = rounded_lon[0]
    lon_max = rounded_lon[1]
    lat_min = rounded_lat[0]
    lat_max = rounded_lat[1]
    
    return lon_min, lon_max, lat_min, lat_max

# Find the rounded bounding box
lon_min, lon_max, lat_min, lat_max = round_coords_to_ERA5(bounding_box)
print('Rounded {} to {},{},{},{}'.format(bounding_box,lat_max,lon_min,lat_min,lon_max))

# --- Subset data

# Function to subset data
def extract_ERA5_subset(infile, outfile, latmin, latmax, lonmin, lonmax):
    with xr.open_dataset(infile) as ds:
        if lonmax > 180:
            # convert ds longitude form -180/180 to 0/360
            lon = ds['longitude'].values
            lon[lon < 0] = lon[lon < 0] + 360
            ds['longitude'] = lon
            ds = ds.sortby('longitude')
        ds_sub = ds.sel(latitude = slice(latmax, latmin), longitude = slice(lonmin, lonmax))
        ds_sub.to_netcdf(outfile)

# Loop
for ix,in_file in enumerate(in_files):
   
    # Find where the data needs to go and make that folder
    outPath = read_from_control(controlFolder/controlFile, control_names[ix])
    
    # Specify the default paths if required
    if outPath == 'default':
        pathString = ''.join(['forcing/',inout_paths[ix]])
        outPath = make_default_path(pathString) # returns Path() object
    else: 
        outPath = Path(outPath) # ensure Path() object

    # Make the folder if it doesn't exist
    outPath.mkdir(parents=True, exist_ok=True)
    
    # Define in and out as strings
    inFull  = str(Path(in_base)/inout_paths[ix]/in_file)
    outFull = str(outPath/in_file)
    
    # Subset the data
    print('Subsetting from {} into {}'.format(inFull,outFull))
    extract_ERA5_subset(inFull, outFull, lat_min, lat_max, lon_min, lon_max)
