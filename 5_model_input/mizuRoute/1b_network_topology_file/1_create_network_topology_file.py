# Create network topology .nc file
# Core assumption: routing is only performed between GRUs. It is recommended to route the runoff from HRUs inside a given GRU with SUMMA instead. This allows for lateral flows between HRUs. Routing HRU runoff with mizuRoute means all HRUs within a given GRU are effectively disconnected. 
#
# **_The code here does not generalize to HRU-routing with mizuRoute without changes._**

# modules
import os
import pandas as pd
import netCDF4 as nc4
import geopandas as gpd
from pathlib import Path
from shutil import copyfile
from datetime import datetime


# --- Control file handling
# Easy access to control file folder
controlFolder = Path('../../../0_controlFiles')

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
    
    
# --- Find location of river network shapefile
# River network shapefile path & name
river_network_path = read_from_control(controlFolder/controlFile,'river_network_shp_path')
river_network_name = read_from_control(controlFolder/controlFile,'river_network_shp_name')

# Specify default path if needed
if river_network_path == 'default':
    river_network_path = make_default_path('shapefiles/river_network') # outputs a Path()
else:
    river_network_path = Path(river_network_path) # make sure a user-specified path is a Path()
    
# Find the field names we're after
river_seg_id      = read_from_control(controlFolder/controlFile,'river_network_shp_segid')
river_down_seg_id = read_from_control(controlFolder/controlFile,'river_network_shp_downsegid')
river_slope       = read_from_control(controlFolder/controlFile,'river_network_shp_slope')
river_length      = read_from_control(controlFolder/controlFile,'river_network_shp_length')
river_outlet_id   = float( read_from_control(controlFolder/controlFile,'river_network_shp_outlet_id') )


# --- Find location of river basin shapefile (routing catchments)
# River network shapefile path & name
river_basin_path = read_from_control(controlFolder/controlFile,'river_basin_shp_path')
river_basin_name = read_from_control(controlFolder/controlFile,'river_basin_shp_name')

# Specify default path if needed
if river_basin_path == 'default':
    river_basin_path = make_default_path('shapefiles/river_basins') # outputs a Path()
else:
    river_basin_path = Path(river_basin_path) # make sure a user-specified path is a Path()
    
# Find the field names we're after
basin_hru_id     = read_from_control(controlFolder/controlFile,'river_basin_shp_rm_hruid')
basin_hru_area   = read_from_control(controlFolder/controlFile,'river_basin_shp_area')
basin_hru_to_seg = read_from_control(controlFolder/controlFile,'river_basin_shp_hru_to_seg')


# --- Find where the topology file needs to go
# Topology .nc path and name
topology_path = read_from_control(controlFolder/controlFile,'settings_mizu_path')
topology_name = read_from_control(controlFolder/controlFile,'settings_mizu_topology')

# Specify default path if needed
if topology_path == 'default':
    topology_path = make_default_path('settings/mizuRoute') # outputs a Path()
else:
    topology_path = Path(topology_path) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
topology_path.mkdir(parents=True, exist_ok=True)


# --- Make the river network topology file
# Open the shapefile
shp_river = gpd.read_file(river_network_path/river_network_name)
shp_basin = gpd.read_file(river_basin_path/river_basin_name)

# Find the number of segments and mizuRoute-HRUs (SUMMA-GRUs)
num_seg = len(shp_river)
num_hru = len(shp_basin)

# Ensure that the most downstream segment in the river network has a downstream_ID of 0
# This indicates to mizuRoute that this segment has no downstream segment attached to it
shp_river.loc[shp_river[river_seg_id] == river_outlet_id, river_down_seg_id] = 0

# Function to create new nc variables
def create_and_fill_nc_var(ncid, var_name, var_type, dim, fill_val, fill_data, long_name, units):
    
    # Make the variable
    ncvar = ncid.createVariable(var_name, var_type, (dim,), fill_val)
    
    # Add the data
    ncvar[:] = fill_data    
    
    # Add meta data
    ncvar.long_name = long_name 
    ncvar.unit = units
    
    return 
    
# Make the netcdf file
with nc4.Dataset(topology_path/topology_name, 'w', format='NETCDF4') as ncid:
    
    # Set general attributes
    now = datetime.now()
    ncid.setncattr('Author', "Created by SUMMA workflow scripts")
    ncid.setncattr('History','Created ' + now.strftime('%Y/%m/%d %H:%M:%S'))
    ncid.setncattr('Purpose','Create a river network .nc file for mizuRoute routing')
    
    # Define the seg and hru dimensions
    ncid.createDimension('seg', num_seg)
    ncid.createDimension('hru', num_hru)
    
    # --- Variables
    create_and_fill_nc_var(ncid, 'segId', 'int', 'seg', False, \
                           shp_river[river_seg_id].values.astype(int), \
                           'Unique ID of each stream segment', '-')
    create_and_fill_nc_var(ncid, 'downSegId', 'int', 'seg', False, \
                           shp_river[river_down_seg_id].values.astype(int), \
                           'ID of the downstream segment', '-')
    create_and_fill_nc_var(ncid, 'slope', 'f8', 'seg', False, \
                           shp_river[river_slope].values.astype(float), \
                           'Segment slope', '-')
    create_and_fill_nc_var(ncid, 'length', 'f8', 'seg', False, \
                           shp_river[river_length].values.astype(float), \
                           'Segment length', 'm')
    create_and_fill_nc_var(ncid, 'hruId', 'int', 'hru', False, \
                           shp_basin[basin_hru_id].values.astype(int), \
                           'Unique hru ID', '-') 
    create_and_fill_nc_var(ncid, 'hruToSegId', 'int', 'hru', False, \
                           shp_basin[basin_hru_to_seg].values.astype(int), \
                           'ID of the stream segment to which the HRU discharges', '-')
    create_and_fill_nc_var(ncid, 'area', 'f8', 'hru', False, \
                           shp_basin[basin_hru_area].values.astype(float), \
                           'HRU area', 'm^2')
                           
                           
# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = topology_path
log_suffix = '_make_river_network_topology.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = '1_create_network_topology_file.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Generated network topology .nc file.']
    for txt in lines:
        file.write(txt) 
