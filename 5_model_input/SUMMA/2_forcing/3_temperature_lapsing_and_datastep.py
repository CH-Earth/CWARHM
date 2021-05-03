# Temperature lapsing and data_step
# The size discrepancy between MERIT basins and the typical coverage of ERA5 grid cells makes it appropriate to apply a temperature lapse rate. This script loops over existing basin-averaged forcing files and applies a lapse rate to the `airtemp` variable. Lapse arte is determined based on the average elevation difference between the basin shape and the ERA5 grid cell(s) that cover the basin.
# 
# In addition, this script adds the `data_step` variable to each forcing file, which SUMMA needs to know the time resolution of the forcing inputs.
#
# Environmental Lapse Rate
# The temperature lapse rate is assumed to have a constant value of `0.0065` `[K m-1]` (Wallace & Hobbs, 2006, p. 421).
#
# Wallace, J., and P. Hobbs (2006), Atmospheric Science: An Introductory Survey, 483 pp., Academic Press, Burlington, Mass

# modules
import os
import numpy as np
import xarray as xr
import pandas as pd
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
    

# --- Find location of intersection file
# Intersected shapefile path. Name is set by EASYMORE as [prefix]_intersected_shapefile.shp
intersect_path = read_from_control(controlFolder/controlFile,'intersect_forcing_path')

# Specify default path if needed
if intersect_path == 'default':
    intersect_path = make_default_path('shapefiles/catchment_intersection/with_forcing') # outputs a Path()
else:
    intersect_path = Path(intersect_path) # make sure a user-specified path is a Path()
    
# Make the file name
domain = read_from_control(controlFolder/controlFile,'domain_name')
intersect_name = domain + '_intersected_shapefile.csv' # can also be .shp, but using the .csv is easier on memory


# --- Find where the EASYMORE-prepared forcing files are
# Forcing files as produced by EASYMORE
forcing_easymore_path = read_from_control(controlFolder/controlFile,'forcing_basin_avg_path')

# Specify default path if needed
if forcing_easymore_path == 'default':
    forcing_easymore_path = make_default_path('forcing/3_basin_averaged_data') # outputs a Path()
else:
    forcing_easymore_path = Path(forcing_easymore_path) # make sure a user-specified path is a Path()
    
# Find the files
_,_,forcing_files = next(os.walk(forcing_easymore_path))


# --- Find the time step size of the forcing data
# Value in control file
data_step = read_from_control(controlFolder/controlFile,'forcing_time_step_size')

# Convert to int
data_step = int(data_step)


# --- Find where the final forcing needs to go
# Location for SUMMA-ready files
forcing_summa_path = read_from_control(controlFolder/controlFile,'forcing_summa_path')

# Specify default path if needed
if forcing_summa_path == 'default':
    forcing_summa_path = make_default_path('forcing/4_SUMMA_input') # outputs a Path()
else:
    forcing_summa_path = Path(forcing_summa_path) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
forcing_summa_path.mkdir(parents=True, exist_ok=True)


# --- Find the area-weighted lapse value for each basin
# Load the intersection file
topo_data = pd.read_csv(intersect_path/intersect_name) 

# Find hruId name in user's shapefile
hru_ID_name = read_from_control(controlFolder/controlFile,'catchment_shp_hruid')
gru_ID_name = read_from_control(controlFolder/controlFile,'catchment_shp_gruid')

# Specify the column names
# Note that column names are truncated at 10 characters in the ESRI shapefile, but NOT in the .csv we use here
gru_ID         = 'S_1_' + gru_ID_name # EASYMORE prefix + user's hruId name
hru_ID         = 'S_1_' + hru_ID_name # EASYMORE prefix + user's hruId name
forcing_ID     = 'S_2_ID'             # fixed name assigned by EASYMORE
catchment_elev = 'S_1_elev_mean'      # EASYMORE prefix + name used in catchment+DEM intersection step
forcing_elev   = 'S_2_elev_m'         # EASYMORE prefix + name used in ERA5 shapefile generation
weights        = 'weight'             # EASYMORE feature

# Define the lapse rate
lapse_rate = 0.0065 # [K m-1]

# Calculate weighted lapse values for each HRU 
# Note that these lapse values need to be ADDED to ERA5 temperature data
topo_data['lapse_values'] = topo_data[weights] * lapse_rate * (topo_data[forcing_elev] - topo_data[catchment_elev]) # [K]

# Find the total lapse value per basin; i.e. sum the individual contributions of each HRU+ERA5-grid overlapping part
lapse_values = topo_data.groupby([gru_ID,hru_ID]).lapse_values.sum().reset_index()

# Sort and set hruID as the index variable
lapse_values = lapse_values.sort_values(hru_ID).set_index(hru_ID)

# Close the main file
del topo_data # hopefully this saves some RAM but this is apparently not so straightforward in Python.. Can't hurt


# --- Loop over forcing files; apply lapse rates and add data-step variable
# Initiate the loop
for file in forcing_files:
    
    # Progress
    print('Starting on ' + file)
    
    # load the data
    with xr.open_dataset(forcing_easymore_path / file) as dat:
    
        # --- Temperature lapse rates
        # Find the lapse rates by matching the HRU order in the forcing file with that in 'lapse_values'
        lapse_values_sorted = lapse_values['lapse_values'].loc[dat['hruId'].values]
    
        # Make a data array of size (nTime,nHru) 
        addThis = xr.DataArray(np.tile(lapse_values_sorted.values, (len(dat['time']),1)), dims=('time','hru')) 
    
        # Subtract lapse values from existing temperature data
        dat['airtemp'] = dat['airtemp'] + addThis
    
        # --- Time step specification 
        dat['data_step'] = data_step
        dat.data_step.attrs['long_name'] = 'data step length in seconds'
        dat.data_step.attrs['units'] = 's'
    
        # --- Save to file in new location
        dat.to_netcdf(forcing_summa_path/file) 
        
        
# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = forcing_summa_path
log_suffix = '_temperature_lapse_and_datastep.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = '3_temperature_lapsing_and_datastep.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Applied temperature lapse rate to forcing data and added data_step variable.']
    for txt in lines:
        file.write(txt) 

