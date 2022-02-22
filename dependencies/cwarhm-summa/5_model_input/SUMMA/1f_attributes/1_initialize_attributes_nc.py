# Initialize attributes.nc
# Create attributes.nc file. This see: https://summa.readthedocs.io/en/master/input_output/SUMMA_input/
#
# Note on HRU order
# HRU order must be the same in forcing, attributes, initial conditions and trial parameter files. Order will be taken from forcing files to ensure consistency.
#
# Fill values
# | Variable       | Value |
# |:---------------|:------|
# | hruId          | taken from the shapefile index values |
# | gruId          | taken from the shapefile index values |
# | hru2gruId      | taken from the shapefile index values |
# | downHRUindex   | 0, each HRU is independent column |
# | longitude      | taken from the shapefile geometry |
# | latitude       | taken from the shapefile geometry |
# | elevation      | placeholder value -999, fill from the MERIT Hydro DEM |
# | HRUarea        | taken from the shapefile attributes |
# | tan_slope      | unused in current set up, fixed at 0.1 [-] |
# | contourLength  | unused in current set up, fixed at 30 [m] |
# | slopeTypeIndex | unused in current set up, fixed at 1 [-] |
# | soilTypeIndex  | placeholder value -999, fill from SOILGRIDS |
# | vegTypeIndex   | placeholder value -999, fill from MODIS veg |
# | mHeight        | temporarily set at 3 [m] |
#
# Assumed modeling decisions
# Note that options:
# - tan_slope
# - contourLength
# - slopeTypeIndex 
# are not set to correct values. `slopeTypeIndex` is a legacy variable that is no longer used. `tan_slope` and `contourLength` are needed for the `qbaseTopmodel` modeling option. These require significant preprocessing of geospatial data and are not yet implemented as part of this workflow.
#
# `downHRUindex` is set to 0, indicating that each HRU will be modeled as an independent column. This can optionally be changed by setting the flag `settings_summa_connect_HRUs` to `yes` in the control file. The notebook that populates the attributes `.nc` file with elevation will in that case also use the relative elevations of HRUs in each GRU to define downslope HRU IDs.

# modules
import os
import pandas as pd
import xarray as xr
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
    
    
# --- Find shapefile location and name
# Catchment shapefile path & name
catchment_path = read_from_control(controlFolder/controlFile,'catchment_shp_path')
catchment_name = read_from_control(controlFolder/controlFile,'catchment_shp_name')

# Specify default path if needed
if catchment_path == 'default':
    catchment_path = make_default_path('shapefiles/catchment') # outputs a Path()
else:
    catchment_path = Path(catchment_path) # make sure a user-specified path is a Path()"
    
# Variable names used in shapefile
catchment_hruId_var = read_from_control(controlFolder/controlFile,'catchment_shp_hruid')
catchment_gruId_var = read_from_control(controlFolder/controlFile,'catchment_shp_gruid')
catchment_area_var = read_from_control(controlFolder/controlFile,'catchment_shp_area')
catchment_lat_var = read_from_control(controlFolder/controlFile,'catchment_shp_lat')
catchment_lon_var = read_from_control(controlFolder/controlFile,'catchment_shp_lon')


# --- Find forcing location and an example file
# Forcing path
forcing_path = read_from_control(controlFolder/controlFile,'forcing_summa_path')

# Specify default path if needed
if forcing_path == 'default':
    forcing_path = make_default_path('forcing/4_SUMMA_input') # outputs a Path()
else:
    forcing_path = Path(forcing_path) # make sure a user-specified path is a Path()
    
# Find a list of forcing files
_,_,forcing_files = next(os.walk(forcing_path))

# Select a random file as a template for hruId order
forcing_name = forcing_files[0]

# Find the forcing measurement height
forcing_measurement_height = float(read_from_control(controlFolder/controlFile,'forcing_measurement_height'))


# --- Find where the attributes need to go
# Attribute path & name
attribute_path = read_from_control(controlFolder/controlFile,'settings_summa_path')
attribute_name = read_from_control(controlFolder/controlFile,'settings_summa_attributes')

# Specify default path if needed
if attribute_path == 'default':
    attribute_path = make_default_path('settings/SUMMA') # outputs a Path()
else:
    attribute_path = Path(attribute_path) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
attribute_path.mkdir(parents=True, exist_ok=True)


# --- Load the catchment shapefile and sort it based on HRU order in the forcing file
# Open the catchment shapefile
shp = gpd.read_file(catchment_path/catchment_name)

# Open the forcing file
forc = xr.open_dataset(forcing_path/forcing_name)

# Get the sorting order from the forcing file
forcing_hruIds = forc['hruId'].values.astype(int) # 'hruId' is prescribed by SUMMA so this variable must exist

# Make the hruId variable in the shapefile the index
shp = shp.set_index(catchment_hruId_var)

# Enforce index as integers
shp.index = shp.index.astype(int)

# Sort the shape based on the forcing HRU order
shp = shp.loc[forcing_hruIds]

# Reset the index so that we reference each row properly in later code
shp = shp.reset_index()


# --- Find number of GRUs and HRUs
# Extract HRU IDs and count unique occurence (should be equal to length of shapefile)
hru_ids = pd.unique(shp[catchment_hruId_var].values)
num_hru = len(hru_ids)

gru_ids = pd.unique(shp[catchment_gruId_var].values)
num_gru = len(gru_ids)


# --- Create the new attributes file
# Create the new .nc file
with nc4.Dataset(attribute_path/attribute_name, "w", format="NETCDF4") as att:

    # General attributes
    now = datetime.now()
    att.setncattr('Author', "Created by SUMMA workflow scripts")
    att.setncattr('History','Created ' + now.strftime('%Y/%m/%d %H:%M:%S'))

    # Define the dimensions 
    att.createDimension('hru',num_hru)
    att.createDimension('gru',num_gru)
    
    # Define the variables
    var = 'hruId'
    att.createVariable(var, 'i4', 'hru', fill_value = False)
    att[var].setncattr('units', '-')
    att[var].setncattr('long_name', 'Index of hydrological response unit (HRU)')
    
    var = 'gruId'
    att.createVariable(var, 'i4', 'gru', fill_value = False)
    att[var].setncattr('units', '-')
    att[var].setncattr('long_name', 'Index of grouped response unit (GRU)')
    
    var = 'hru2gruId'
    att.createVariable(var, 'i4', 'hru', fill_value = False)
    att[var].setncattr('units', '-')
    att[var].setncattr('long_name', 'Index of GRU to which the HRU belongs')
    
    var = 'downHRUindex'
    att.createVariable(var, 'i4', 'hru', fill_value = False)
    att[var].setncattr('units', '-')
    att[var].setncattr('long_name', 'Index of downslope HRU (0 = basin outlet)')
    
    var = 'longitude'
    att.createVariable(var, 'f8', 'hru', fill_value = False)
    att[var].setncattr('units', 'Decimal degree east')
    att[var].setncattr('long_name', 'Longitude of HRU''s centroid')
    
    var = 'latitude'
    att.createVariable(var, 'f8', 'hru', fill_value = False)
    att[var].setncattr('units', 'Decimal degree north')
    att[var].setncattr('long_name', 'Latitude of HRU''s centroid')
    
    var = 'elevation'
    att.createVariable(var, 'f8', 'hru', fill_value = False)
    att[var].setncattr('units', 'm')
    att[var].setncattr('long_name', 'Mean HRU elevation')
    
    var = 'HRUarea'
    att.createVariable(var, 'f8', 'hru', fill_value = False)
    att[var].setncattr('units', 'm^2')
    att[var].setncattr('long_name', 'Area of HRU')
    
    var = 'tan_slope'
    att.createVariable(var, 'f8', 'hru', fill_value = False)
    att[var].setncattr('units', 'm m-1')
    att[var].setncattr('long_name', 'Average tangent slope of HRU')
    
    var = 'contourLength'
    att.createVariable(var, 'f8', 'hru', fill_value = False)
    att[var].setncattr('units', 'm')
    att[var].setncattr('long_name', 'Contour length of HRU')
    
    var = 'slopeTypeIndex'
    att.createVariable(var, 'i4', 'hru', fill_value = False)
    att[var].setncattr('units', '-')
    att[var].setncattr('long_name', 'Index defining slope')
    
    var = 'soilTypeIndex'
    att.createVariable(var, 'i4', 'hru', fill_value = False)
    att[var].setncattr('units', '-')
    att[var].setncattr('long_name', 'Index defining soil type')
    
    var = 'vegTypeIndex'
    att.createVariable(var, 'i4', 'hru', fill_value = False)
    att[var].setncattr('units', '-')
    att[var].setncattr('long_name', 'Index defining vegetation type')
    
    var = 'mHeight'
    att.createVariable(var, 'f8', 'hru', fill_value = False)
    att[var].setncattr('units', 'm')
    att[var].setncattr('long_name', 'Measurement height above bare ground')
    
    # Progress
    progress = 0
    
    # GRU variable
    for idx in range(0,num_gru):
        att['gruId'][idx] = gru_ids[idx]
    
    # HRU variables; due to pre-sorting, these are already in the same order as the forcing files
    for idx in range(0,num_hru):
        
        # Fill values from shapefile
        att['hruId'][idx]     = shp.iloc[idx][catchment_hruId_var]
        att['HRUarea'][idx]   = shp.iloc[idx][catchment_area_var]
        att['latitude'][idx]  = shp.iloc[idx][catchment_lat_var]
        att['longitude'][idx] = shp.iloc[idx][catchment_lon_var]
        att['hru2gruId'][idx] = shp.iloc[idx][catchment_gruId_var]
        
        # Constants
        att['tan_slope'][idx]      = 0.1                         # Only used in qbaseTopmodel modelling decision
        att['contourLength'][idx]  = 30                          # Only used in qbaseTopmodel modelling decision
        att['slopeTypeIndex'][idx] = 1                           # Needs to be set but not used
        att['mHeight'][idx]        = forcing_measurement_height  # Forcing data height; used in some scaling equations       
        att['downHRUindex'][idx]   = 0   # All HRUs modeled as independent columns; optionally changed when elevation is added to attributes.nc
        
        # Placeholders to be filled later
        att['elevation'][idx]     = -999
        att['soilTypeIndex'][idx] = -999
        att['vegTypeIndex'][idx]  = -999
        
       # Show a progress report
        print(str(progress+1) + ' out of ' + str(num_hru) + ' HRUs completed.')
        
        # Increment the counter
        progress += 1
        
        
# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = attribute_path
log_suffix = '_initialize_attributes.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = '1_initialize_attributes_nc.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Initialized the attributes .nc file.']
    for txt in lines:
        file.write(txt) 