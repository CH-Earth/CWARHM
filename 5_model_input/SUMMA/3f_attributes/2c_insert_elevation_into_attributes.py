# Insert MERIT Hydro elevation in SUMMA set up
# Inserts elevation of each HRU into the attributes `.nc` file. The intersection code stores this value in field `elev_mean`. 
#
# If the field `settings_summa_connect_HRUs` is set to `yes` in the control file, this script also finds the downslope HRU (attribute `downHRUindex`) for the HRUs within each GRU. The most downstream HRU (i.e. the GRU outlet) is set to `0` to follow SUMMA conventions. If `settings_summa_connect_HRUs` is set to `no`, all HRUs are modelled as indepdendent columns and outflow from all HRUs inside each GRU is combined into basin-average outflow. No further action is needed, as `downHRUindex` for each HRU has already been set to `0`.

# modules
import os
import numpy as np
import netCDF4 as nc4
import geopandas as gpd
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
            if setting in line:
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
    
    
# --- Find shapefile location and name
# Path to and name of shapefile with intersection between catchment and soil classes
intersect_path = read_from_control(controlFolder/controlFile,'intersect_dem_path')
intersect_name = read_from_control(controlFolder/controlFile,'intersect_dem_name')

# Specify default path if needed
if intersect_path == 'default':
    intersect_path = make_default_path('shapefiles/catchment_intersection/with_dem') # outputs a Path()
else:
    intersect_path = Path(intersect_path) # make sure a user-specified path is a Path()
    
# Variable names used in shapefile
intersect_hruId_var = read_from_control(controlFolder/controlFile,'catchment_shp_hruid')
intersect_gruId_var = read_from_control(controlFolder/controlFile,'catchment_shp_gruid')


# --- Find where the attributes file is
# Attribute path & name
attribute_path = read_from_control(controlFolder/controlFile,'settings_summa_path')
attribute_name = read_from_control(controlFolder/controlFile,'settings_summa_attributes')

# Specify default path if needed
if attribute_path == 'default':
    attribute_path = make_default_path('settings/SUMMA') # outputs a Path()
else:
    attribute_path = Path(attribute_path) # make sure a user-specified path is a Path()
    
    
# --- Open the shapefile
# Open files
shp = gpd.read_file(intersect_path/intersect_name)


# --- Define downHRUindex values if requested
# Find if this is requested by the user
do_downHRUindex = read_from_control(controlFolder/controlFile,'settings_summa_connect_HRUs')

# Find the downHRUindex value if requested
if do_downHRUindex.lower() == 'yes':
    
    # Find the unique GRU IDs
    gru_ids = shp[intersect_gruId_var].unique()
    
    # Create a temporary field we'll fill
    shp['downHRUindex'] = 0
    
    # Make hruId the index
    shp.set_index(intersect_hruId_var, inplace=True)
    
    # Loop over the GRUs
    for gru_id in gru_ids:
    
        # Select only the GRU we're currently working on
        gru_mask = (shp[intersect_gruId_var] == gru_id)
    
        # Find the soring order of HRUs in this GRU based on their elevations
        tmp_sort = shp[gru_mask]['elev_mean'].argsort()
    
        # Loop over the HRUs in this GRU and set their downHRUindex in the shapefile
        HRUs_seen = 0
        last_HRU = 0
        for HRU,order in tmp_sort.iteritems():
            if order == 0: 
                # most downstream HRU
                print('Filling downHRUindex of HRU {} with HRU {}'.format(last_HRU,HRU)) 
                print('Filling downHRUindex of HRU {} with HRU {}'.format(HRU,0)) 
                if last_HRU != 0: # If there are more HRUs in this GRU ...
                    shp.at[last_HRU, 'downHRUindex'] = int(HRU) # fill the second-to last and also ...
                shp.at[HRU,      'downHRUindex'] = 0   # fill the last (possibly only) HRU
            elif HRUs_seen > 0:
                # not the first iteration
                print('Filling downHRUindex of HRU {} with HRU {}'.format(last_HRU,HRU))        
                shp.at[last_HRU, 'downHRUindex'] = int(HRU)
            HRUs_seen += 1
            last_HRU = HRU
            
    # Reset the index
    shp.reset_index(inplace=True)
    
    
# --- Open the attributes file and fill the placeholder values in the attributes file
# Open the netcdf file for reading+writing
with nc4.Dataset(attribute_path/attribute_name, "r+") as att:
    
    # Loop over the HRUs in the attributes
    for idx in range(0,len(att['hruId'])):
        
        # Find the HRU ID (attributes file) at this index
        attribute_hru = att['hruId'][idx]
    
        # Find the row in the shapefile that contains info for this HRU
        shp_mask = (shp[intersect_hruId_var] == attribute_hru)
        
        # Find the elevation & downHRUindex
        tmp_elev = shp['elev_mean'][shp_mask].values[0]
        tmp_down = shp['downHRUindex'][shp_mask].values[0]
        
        # Replace the value
        print('Replacing elevation {} [m] with {} [m] at HRU {}'.format(att['elevation'][idx],tmp_elev,attribute_hru))
        att['elevation'][idx] = tmp_elev
        
        if do_downHRUindex.lower() == 'yes':
            print('Replacing downHRUindex {} with {} at HRU {}'.format(att['downHRUindex'][idx],tmp_down,attribute_hru))
            att['downHRUindex'][idx] = tmp_down
            
            
# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = attribute_path
log_suffix = '_add_elevation_to_attributes.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = '2c_insert_elevation_into_attributes.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Added elevation to attributes .nc file.']
    for txt in lines:
        file.write(txt) 