# Create SUMMA-to-mizuRoute catchment remapping file
# Creates a remap `.nc` file for cases where the routing catchments are different from the catchments used to run SUMMA. While mizuRoute is able to perform routing from grid-based outputs, SUMMA does not produce these and the code here is not setup to work with gridded model outputs.
#
# **_This code assumes routing occurs at the GRU level of SUMMA outputs. SUMMA-HRU-level routing is not supported._**

# modules
import itertools
import pandas as pd
import netCDF4 as nc4
import geopandas as gpd
from pathlib import Path
from shutil import copyfile
import candex.candex as cndx
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
    
    
# --- Check if remapping is needed
# Get the remap flag
do_remap = read_from_control(controlFolder/controlFile,'river_basin_needs_remap')

# Check
if do_remap.lower() != 'yes':
    print('Active control file indicates remapping is not needed. Aborting.')
    exit()
    

# --- Find location of hydrologic model (HM) catchment shapefile
# HM catchment shapefile path & name
hm_catchment_path = read_from_control(controlFolder/controlFile,'catchment_shp_path')
hm_catchment_name = read_from_control(controlFolder/controlFile,'catchment_shp_name')

# Specify default path if needed
if hm_catchment_path == 'default':
    hm_catchment_path = make_default_path('shapefiles/catchment') # outputs a Path()
else:
    hm_catchment_path = Path(hm_catchment_path) # make sure a user-specified path is a Path()
    
# Find the fields we're interested in
hm_shp_gru_id = read_from_control(controlFolder/controlFile,'catchment_shp_gruid')


# --- Find location of routing model (RM) catchment shapefile
# Routing model catchment shapefile path & name
rm_catchment_path = read_from_control(controlFolder/controlFile,'river_basin_shp_path')
rm_catchment_name = read_from_control(controlFolder/controlFile,'river_basin_shp_name')

# Specify default path if needed
if rm_catchment_path == 'default':
    rm_catchment_path = make_default_path('shapefiles/river_basins') # outputs a Path()
else:
    rm_catchment_path = Path(rm_catchment_path) # make sure a user-specified path is a Path()
    
# Find the fields we're interested in
rm_shp_hru_id = read_from_control(controlFolder/controlFile,'river_basin_shp_rm_hruid')


# --- Find where the intersection needs to go
# Intersected shapefile path. Name is set by CANDEX as [prefix]_intersected_shapefile.shp
intersect_path = read_from_control(controlFolder/controlFile,'intersect_routing_path')
intersect_name = read_from_control(controlFolder/controlFile,'intersect_routing_name')

# Specify default path if needed
if intersect_path == 'default':
    intersect_path = make_default_path('shapefiles/catchment_intersection/with_routing') # outputs a Path()
else:
    intersect_path = Path(intersect_path) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
intersect_path.mkdir(parents=True, exist_ok=True)


# --- Find where the remapping file needs to go
# Remap .nc path and name
remap_path = read_from_control(controlFolder/controlFile,'settings_mizu_path')
remap_name = read_from_control(controlFolder/controlFile,'settings_mizu_remap')

# Specify default path if needed
if remap_path == 'default':
    remap_path = make_default_path('settings/mizuRoute') # outputs a Path()
else:
    remap_path = Path(remap_path) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
remap_path.mkdir(parents=True, exist_ok=True)


# --- Call CANDEX to do the intersection
# Load both shapefiles
hm_shape = gpd.read_file(hm_catchment_path/hm_catchment_name)
rm_shape = gpd.read_file(rm_catchment_path/rm_catchment_name)

# Create a CANDEX object
candex_caller = cndx()

# Project both shapes to equal area
hm_shape = hm_shape.to_crs('EPSG:6933')
rm_shape = rm_shape.to_crs('EPSG:6933')

# Run the intersection
intersected_shape = cndx.intersection_shp(candex_caller,rm_shape,hm_shape)

# Reproject the intersection to WSG84
intersected_shape = intersected_shape.to_crs('EPSG:4326')

# Save the intersection to file
intersected_shape.to_file(intersect_path/intersect_name)


# --- Pre-process the variables
# Define a few shorthand variables
int_rm_id = 'S_1_' + rm_shp_hru_id
int_hm_id = 'S_2_' + hm_shp_gru_id
int_weight = 'AP1N'

# Sort the intersected shape by RM ID first, and HM ID second. This means all info per RM ID is in consecutive rows
intersected_shape = intersected_shape.sort_values(by=[int_rm_id,int_hm_id])

# Routing Network HRU ID
nc_rnhruid = intersected_shape.groupby(int_rm_id).agg({int_rm_id: pd.unique}).values.astype(int)

# Number of Hydrologic Model elements (GRUs in SUMMA's case) per Routing Network catchment
nc_noverlaps = intersected_shape.groupby(int_rm_id).agg({int_hm_id: 'count'}).values.astype(int)

# Hydrologic Model GRU IDs that are associated with each part of the overlap
multi_nested_list = intersected_shape.groupby(int_rm_id).agg({int_hm_id: list}).values.tolist() # Get the data
nc_hmgruid = list(itertools.chain.from_iterable(itertools.chain.from_iterable(multi_nested_list))) # Combine 3 nested list into 1

# Areal weight of each HM GRU per part of the overlaps
multi_nested_list = intersected_shape.groupby(int_rm_id).agg({int_weight: list}).values.tolist() 
nc_weight = list(itertools.chain.from_iterable(itertools.chain.from_iterable(multi_nested_list))) 


# --- Make the `.nc` file
# Find the dimension sizes
num_hru  = len(rm_shape)
num_data = len(intersected_shape)

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
with nc4.Dataset(remap_path/remap_name, 'w', format='NETCDF4') as ncid:
    
    # Set general attributes
    now = datetime.now()
    ncid.setncattr('Author', "Created by SUMMA workflow scripts")
    ncid.setncattr('History','Created ' + now.strftime('%Y/%m/%d %H:%M:%S'))
    ncid.setncattr('Purpose','Create a remapping .nc file for mizuRoute routing')
    
    # Define the seg and hru dimensions
    ncid.createDimension('hru', num_hru)
    ncid.createDimension('data', num_data)
    
    # --- Variables
    create_and_fill_nc_var(ncid, 'RN_hruId', 'int', 'hru', False, nc_rnhruid, \
                           'River network HRU ID', '-')
    create_and_fill_nc_var(ncid, 'nOverlaps', 'int', 'hru', False, nc_noverlaps, \
                           'Number of overlapping HM_HRUs for each RN_HRU', '-')
    create_and_fill_nc_var(ncid, 'HM_hruId', 'int', 'data', False, nc_hmgruid, \
                           'ID of overlapping HM_HRUs. Note that SUMMA calls these GRUs', '-')
    create_and_fill_nc_var(ncid, 'weight', 'f8', 'data', False, nc_weight, \
                           'Areal weight of overlapping HM_HRUs. Note that SUMMA calls these GRUs', '-')
                           

# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = remap_path
log_suffix = '_make_remapping_file.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = '1_remap_summa_catchments_to_routing.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Generated remapping .nc file for Hydro model catchments to routing model catchments.']
    for txt in lines:
        file.write(txt) 

