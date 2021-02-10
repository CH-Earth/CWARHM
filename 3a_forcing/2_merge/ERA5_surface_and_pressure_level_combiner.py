#!/usr/bin/env python
# coding: utf-8

# Combine separate surface and pressure level downloads
# Creates a single monthly `.nc` file with SUMMA-ready variables for further processing. # Combines ERA5's `u` and `v` wind components into a single directionless wind vector.

# modules
from datetime import datetime
from shutil import copyfile
from pathlib import Path
import netCDF4 as nc4
import numpy as np
import time
import sys
import os

# --- Control file handling
# Easy access to control file folder
controlFolder = Path('../../0_controlFiles')

# Store the name of the 'active' file in a variable
controlFile = 'control_active.txt'

# Function to extract a given setting from the control file
def read_from_control( file, setting ):
    
    # Open 'control_active.txt' and ...
    for line in open(file):
        
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
    
    
# --- Find source and destination paths
# Find the path where the raw forcing is
# Immediately store as a 'Path' to avoid issues with '/' and '\' on different operating systems
forcingPath = read_from_control(controlFolder/controlFile,'forcing_raw_path')

# Find the path where the merged forcing needs to go
mergePath = read_from_control(controlFolder/controlFile,'forcing_merged_path')

# Specify the default paths if required
if forcingPath == 'default':
    forcingPath = make_default_path('forcing/1_ERA5_raw_data')
if mergePath == 'default':
    mergePath = make_default_path('forcing/2_merged_data')
    
# Make the merge folder if it doesn't exist
mergePath.mkdir(parents=True, exist_ok=True)


# --- Find the years to merge
# Find which years were downloaded
years = read_from_control(controlFolder/controlFile,'forcing_raw_time')

# Split the string into 2 integers
years = years.split(',')
years = [int(year) for year in years]


# --- Merge the files
# Loop through all years and months
for year in range(years[0],years[1]+1):
    for month in range (1,13):

        # Define file names 
        data_pres = 'ERA5_pressureLevel137_' + str(year) + str(month).zfill(2) + '.nc'
        data_surf = 'ERA5_surface_' + str(year) + str(month).zfill(2) + '.nc'
        data_dest = 'ERA5_NA_' + str(year) + str(month).zfill(2) + '.nc'

        # Step 1: convert lat/lon in the pressure level file to range [-180,180], [-90,90]
        # Extract the variables we need for the similarity check in a way that closes the files implicitly
        with nc4.Dataset(forcingPath / data_pres) as src1, nc4.Dataset(forcingPath / data_surf) as src2:
            pres_lat = src1.variables['latitude'][:]
            pres_lon = src1.variables['latitude'][:]
            pres_time = src1.variables['time'][:]
            surf_lat = src2.variables['latitude'][:]
            surf_lon = src2.variables['latitude'][:]
            surf_time = src2.variables['time'][:]

        # Update the pressure level coordinates
        pres_lat[pres_lat > 90] = pres_lat[pres_lat > 90] - 180
        pres_lon[pres_lon > 180] = pres_lon[pres_lon > 90] - 360

        # Step 2: check that coordinates and time are the same between the both files
        # Compare dimensions (lat, long, time)
        flag_loc_and_time_same = [all(pres_lat == surf_lat), all(pres_lon == surf_lon), all(pres_time == surf_time)]

        # Check that they are all the same
        if not all(flag_loc_and_time_same):
            err_txt = 'Dimension mismatch while merging ' + data_pres + ' and ' + data_surf + '. Check latitude, longitude and time dimensions in both files. Continuing with next files.'
            print(err_txt)
            continue

        # Step 3: combine everything into a single .nc file
        # Order of writing things:
        # - Meta attributes from both source files
        # - Dimensions (lat, lon, time)
        # - Variables: long, lat and time
        # - Variables: forcing at surface
        # - Variables: forcing at pressure level 137

        # Define the variables we want to transfer
        variables_surf_transfer = ['longitude','latitude','time']
        variables_surf_convert = ['sp','mtpr','msdwswrf','msdwlwrf']
        variables_pres_convert = ['t','q']
        attr_names_expected = ['scale_factor','add_offset','_FillValue','missing_value','units','long_name','standard_name'] # these are the attributes we think each .nc variable has             
        loop_attr_copy_these = ['units','long_name','standard_name'] # we will define new values for _FillValue and missing_value when writing the .nc variables' attributes

        # Open the destination file and transfer information
        with nc4.Dataset(forcingPath / data_pres) as src1, nc4.Dataset(daforcingPathta_path / data_surf) as src2, nc4.Dataset(mergePath / data_dest, "w") as dest: 
    
            # === Some general attributes
            dest.setncattr('History','Created ' + time.ctime(time.time()))
            dest.setncattr('Language','Written using Python')
            dest.setncattr('Reason','(1) ERA5 surface and pressure files need to be combined into a single file (2) Wind speed U and V components need to be combined into a single vector (3) Forcing variables need to be given to SUMMA without scale and offset')
    
            # === Meta attributes from both sources
            for name in src1.ncattrs():
                dest.setncattr(name + ' (pressure level (10m) data)', src1.getncattr(name))
            for name in src2.ncattrs():
                dest.setncattr(name + ' (surface level data)', src1.getncattr(name))
    
            # === Dimensions: latitude, longitude, time
            # NOTE: we can use the lat/lon from the surface file (src2), because those are already in proper units. If there is a mismatch between surface and pressure we shouldn't have reached this point at all due to the check above
            for name, dimension in src2.dimensions.items():
                if dimension.isunlimited():
                    dest.createDimension( name, None)
                else:
                    dest.createDimension( name, len(dimension))
    
            # === Get the surface level generic variables (lat, lon, time)
            for name, variable in src2.variables.items():
        
                # Transfer lat, long and time variables because these don't have scaling factors
                if name in variables_surf_transfer:
                    dest.createVariable(name, variable.datatype, variable.dimensions, fill_value = -999)
                    dest[name].setncatts(src1[name].__dict__)
                    dest.variables[name][:] = src2.variables[name][:]
            
            # === For the forcing variables, we need to:
            # 1. Extract them (this automatically applies scaling and offset with nc4) and apply non-negativity constraints
            # 2. Create a .nc variable with the right SUMMA name and file type
            # 3. Put all data into the new .nc file
    
            # ===  Transfer the surface level data first, for no particular reason
            # This should contain surface pressure (sp), downward longwave (msdwlwrf), downward shortwave (msdwswrf) and precipitation (mtpr)
            for name, variable in src2.variables.items():
    
                # Check that we are only using the names we expect, and thus the names for which we have the required code ready
                if name in variables_surf_convert:
            
                    # 0. Reset the dictionary that we keep attribute values in
                    loop_attr_source_values = {name: 'n/a' for name in attr_names_expected}
            
                    # 1a. Get the values of this variable from the source (this automatically applies scaling and offset)
                    loop_val = variable[:]

                    # 1b. Apply non-negativity constraint. This is intended to remove very small negative data values that sometimes occur
                    loop_val[loop_val < 0] = 0
            
                    # 1c. Get the attributes for this variable from source
                    for attrname in variable.ncattrs():
                        loop_attr_source_values[attrname] = variable.getncattr(attrname)
            
                    # 2a. Find what this ERA5 variable should be called in SUMMA
                    if name == 'sp':
                        name_summa = 'airpres'
                    elif name == 'msdwlwrf':
                        name_summa = 'LWRadAtm'
                    elif name == 'msdwswrf':
                        name_summa = 'SWRadAtm'
                    elif name == 'mtpr':
                        name_summa = 'pptrate'            
                    else:
                        name_summa = 'n/a/' # no name so we don't start overwriting data if a new name is not defined for some reason
            
                    # 2b. Create the .nc variable with the proper SUMMA name
                    # Inputs: variable name as needed by SUMMA; data type: 'float'; dimensions; no need for fill value, because thevariable gets populated in this same script
                    dest.createVariable(name_summa, 'f4', ('time','latitude','longitude'), fill_value = False)
            
                    # 3a. Select the attributes we want to copy for this variable, based on the dictionary defined before the loop starts
                    loop_attr_copy_values = {use_this: loop_attr_source_values[use_this] for use_this in loop_attr_copy_these}
            
                    # 3b. Copy the attributes FIRST, so we don't run into any scaling/offset issues
                    dest[name_summa].setncattr('missing_value',-999)
                    dest[name_summa].setncatts(loop_attr_copy_values)
            
                    # 3c. Copy the data SECOND
                    dest[name_summa][:] = loop_val
            
            # === Transfer the pressure level variables next, using the same procedure as above
            for name, variable in src1.variables.items():
                if name in variables_pres_convert:
            
                    # 0. Reset the dictionary that we keep attribute values in
                    loop_attr_source_values = {name: 'n/a' for name in attr_names_expected}
            
                    # 1a. Get the values of this variable from the source (this automatically applies scaling and offset)
                    loop_val = variable[:] 
            
                    # 1b. Get the attributes for this variable from source
                    for attrname in variable.ncattrs():
                        loop_attr_source_values[attrname] = variable.getncattr(attrname)
            
                    # 2a. Find what this ERA5 variable should be called in SUMMA
                    if name == 't':
                        name_summa = 'airtemp'
                    elif name == 'q':
                        name_summa = 'spechum'
                    elif name == 'u':
                        name_summa = 'n/a/' # we shouldn't reach this part of the code, because 'u' is not specified in 'variables_pres_convert'
                    elif name == 'v':
                        name_summa = 'n/a' # as with 'u', because both are needed to calculate total wind speed first
                    else:
                        name_summa = 'n/a/' # no name so we don't start overwriting data if a new name is not defined for some reason
            
                    # 2b. Create the .nc variable with the proper SUMMA name
                    # Inputs: variable name as needed by SUMMA; data type: 'float'; dimensions; no need for fill value, because thevariable gets populated in this same script
                    dest.createVariable(name_summa, 'f4', ('time','latitude','longitude'), fill_value = False)
            
                    # 3a. Select the attributes we want to copy for this variable, based on the dictionary defined before the loop starts
                    loop_attr_copy_values = {use_this: loop_attr_source_values[use_this] for use_this in loop_attr_copy_these}
            
                    # 3b. Copy the attributes FIRST, so we don't run into any scaling/offset issues
                    dest[name_summa].setncattr('missing_value',-999)
                    dest[name_summa].setncatts(loop_attr_copy_values)
            
                    # 3c. Copy the data SECOND
                    dest[name_summa][:] = loop_val
            
            # === Calculate combined wind speed and store
            # 1a. Get the values of this variable from the source (this automatically applies scaling and offset)
            pres_u = src1.variables['u'][:]
            pres_v = src1.variables['v'][:]
    
            # 1b. Create the variable attribute 'units' from the source data. This lets us check if the source units match (they should match)
            unit_u = src1.variables['u'].getncattr('units')
            unit_v = src1.variables['v'].getncattr('units')
            unit_w = '(({})**2 + ({})**2)**0.5'.format(unit_u,unit_v) 
    
            # 2a. Set the summa_name
            name_summa = 'windspd'
    
            # 2b. Create the .nc variable with the proper SUMMA name
            # Inputs: variable name as needed by SUMMA; data type: 'float'; dimensions; no need for fill value, because thevariable gets populated in this same script
            dest.createVariable(name_summa,'f4',('time','latitude','longitude'),fill_value = False)
    
            # 3a. Set the attributes FIRST, so we don't run into any scaling/offset issues
            dest[name_summa].setncattr('missing_value',-999)
            dest[name_summa].setncattr('units',unit_w)
            dest[name_summa].setncattr('long_name','wind speed at the measurement height, computed from ERA5 U and V-components')
            dest[name_summa].setncattr('standard_name','wind_speed')
    
            # 3b. Copy the data SECOND
            # Creating a new variable first and writing to .nc later seems faster than directly writing to .nc
            pres_w = ((pres_u**2)+(pres_v**2))**0.5
            dest[name_summa][:] = pres_w
    
        print('Finished merging {} and {} into {}'.format(data_surf,data_pres,data_dest))
        

# --- Code provenance
# Create a log folder
logFolder = '_workflow_log'
Path( mergePath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = 'ERA5_surface_and_pressure_level_combiner.ipynb'
copyfile(thisFile, mergePath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + '_pressure_level_log.txt'
with open( mergePath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Merged ERA5 pressure and surface level data into single files.']
    for txt in lines:
        file.write(txt) 

