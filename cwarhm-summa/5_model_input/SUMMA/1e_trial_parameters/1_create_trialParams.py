# Create trialParams.nc
# Creates empty `trialParams.nc` file for SUMMA runs. This file will initially be empty, but can later be populated with parameter values the user whishes to test.
#
# Note on HRU order
#HRU order must be the same in forcing, attributes, initial conditions and trial parameter files. Order will be taken from forcing files to ensure consistency.

# modules
import os
import numpy as np
import xarray as xr
import netCDF4 as nc4
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


# --- Find where the trial parameter file needs to go
# Trial parameter path & name
parameter_path = read_from_control(controlFolder/controlFile,'settings_summa_path')
parameter_name = read_from_control(controlFolder/controlFile,'settings_summa_trialParams')

# Specify default path if needed
if parameter_path == 'default':
    parameter_path = make_default_path('settings/SUMMA') # outputs a Path()
else:
    parameter_path = Path(parameter_path) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
parameter_path.mkdir(parents=True, exist_ok=True)


# --- Find order and number of HRUs in forcing file
# Open the forcing file
forc = xr.open_dataset(forcing_path/forcing_name)

# Get the sorting order from the forcing file
forcing_hruIds = forc['hruId'].values.astype(int) # 'hruId' is prescribed by SUMMA so this variable must exist

# Number of HRUs
num_hru = len(forcing_hruIds)


# --- Read any other trial parameters that need to be specified
num_tp = int( read_from_control(controlFolder/controlFile,'settings_summa_trialParam_n') )

# read the names and values of trial parameters to specify
all_tp = {}
for ii in range(0,num_tp):
    
    # Get the values
    par_and_val = read_from_control(controlFolder/controlFile,f'settings_summa_trialParam_{ii+1}')
    
    # Split into parameter and value
    arr = par_and_val.split(',')
    
    # Convert value(s) into float
    if len(arr) > 2:
        # Store all values as an array of floats    
        val = np.array(arr[1:], dtype=np.float32)
    else: 
        # Convert the single value to a float
        val = float( arr[1] )
        
    # Store in dictionary
    all_tp[arr[0]] = val


# --- Make the trial parameter file
# Create the empty trial params file
with nc4.Dataset(parameter_path/parameter_name, "w", format="NETCDF4") as tp:
    
    # === Some general attributes
    now = datetime.now()
    tp.setncattr('Author', "Created by SUMMA workflow scripts")
    tp.setncattr('History','Created ' + now.strftime('%Y/%m/%d %H:%M:%S'))
    tp.setncattr('Purpose','Create a trial parameter .nc file for initial SUMMA runs')
    
    # === Define the dimensions 
    tp.createDimension('hru',num_hru)
    
    # === Variables ===
    var = 'hruId'
    tp.createVariable(var, 'i4', 'hru', fill_value = False)
    tp[var].setncattr('units', '-')
    tp[var].setncattr('long_name', 'Index of hydrological response unit (HRU)')
    tp[var][:] = forcing_hruIds
    
    # Loop over any specified trial parameters and store in file
    for var,val in all_tp.items():
        tp.createVariable(var, 'f8', 'hru', fill_value = False)
        tp[var][:] = val  
    
    
# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = parameter_path
log_suffix = '_make_trial_parameter_file.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = '1_create_trialParams.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Generated trial parameter .nc file.']
    for txt in lines:
        file.write(txt) 