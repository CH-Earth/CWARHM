#!/usr/bin/env python
# coding: utf-8

# Make ERA5 shapefile
# The shapefile for the forcing data needs to represent the regular latitude/longitude grid of the ERA5 data. We need this for later intersection with the catchment shape(s) so we can create appropriately weighted forcing for each model element. 

# Note that ERA5 data should be thought of as being provided for a specific point in space. These points are the lat/lon coordinates found as netcdf dimensions in the data files. Here, these coordinates will act as center points for a grid. Each point is assumed to be representative for an equal-sized area around itself. See: https://confluence.ecmwf.int/display/CKB/ERA5%3A+What+is+the+spatial+reference


# modules
import os
import shapefile # listed for install as "PyShp" library
import numpy as np
import netCDF4 as nc4
import geopandas as gpd
from pathlib import Path
from shutil import copyfile
from datetime import datetime

# ---- Control file handling
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
    

# --- Find location of merged forcing data
# Find the path where the merged forcing is
mergePath = read_from_control(controlFolder/controlFile,'forcing_merged_path')

# Specify the default path if required
if mergePath == 'default':
    mergePath = make_default_path('forcing/2_merged_data')
    
    
# --- Find spatial extent of domain
# Find which locations to download
coordinates = read_from_control(controlFolder/controlFile,'forcing_raw_space')

# Extract values
coordinates = coordinates.split('/') # lat_max, lon_min, lat_min, lon_max

# Re-organize values in the order the rest of the code expects: lat_min, lat_max, lon_min, lon_max
bounding_box = np.array([coordinates[2], coordinates[0],  coordinates[1],  coordinates[3] ])


# --- Find where the shapefile needs to go
# Find the path where the new shapefile needs to go
shapePath = read_from_control(controlFolder/controlFile,'forcing_shape_path')

# Specify the default path if required
if shapePath == 'default':
    shapePath = make_default_path('shapefiles/forcing')
    
# Find name of the new shapefil
shapeName = read_from_control(controlFolder/controlFile,'forcing_shape_name')


# --- Read the source file to find the grid spacing
# Find an .nc file in the forcing path
for file in os.listdir(mergePath):
    if file.endswith('.nc'):
        forcing_file = file
        break
        
# Set the dimension variable names
source_name_lat = "latitude"
source_name_lon = "longitude"

# Open the file and get the dimensions
with nc4.Dataset(mergePath / forcing_file) as src:
    lat = src.variables[source_name_lat][:]
    lon = src.variables[source_name_lon][:]
    
# Find the spacing
half_dlat = abs(lat[1] - lat[0])/2
half_dlon = abs(lon[1] - lon[0])/2


# --- Create the new shape
with shapefile.Writer(shapePath / shapeName) as w:
    w.autoBalance = 1 # turn on function that keeps file stable if number of shapes and records don't line up
    w.field("ID",'N') # create (N)umerical attribute fields, integer
    w.field("lat",'F',decimal=4) # float with 4 decimals
    w.field("lon",'F',decimal=4)
    ID = 0 # start ID counter of empty
    
    for i in range(0,len(lon)):
        for j in range(0,len(lat)):
            ID += 1
            center_lon = lon[i]
            center_lat = lat[j]
            vertices = []
            parts = []
            vertices.append([center_lon-half_dlon, center_lat])
            vertices.append([center_lon-half_dlon, center_lat+half_dlat])
            vertices.append([center_lon          , center_lat+half_dlat])
            vertices.append([center_lon+half_dlon, center_lat+half_dlat])
            vertices.append([center_lon+half_dlon, center_lat])
            vertices.append([center_lon+half_dlon, center_lat-half_dlat])
            vertices.append([center_lon          , center_lat-half_dlat])
            vertices.append([center_lon-half_dlon, center_lat-half_dlat])
            vertices.append([center_lon-half_dlon, center_lat])
            parts.append(vertices)
            w.poly(parts)
            w.record(ID, center_lat, center_lon)
            
            
# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Create a log folder
logFolder = '_workflow_log'
Path( shapePath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = 'create_ERA5_shapefile.py'
copyfile(thisFile, shapePath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + '_pressure_level_log.txt'
with open( shapePath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Created ERA5 regular latitude/longitude grid.']
    for txt in lines:
        file.write(txt) 
