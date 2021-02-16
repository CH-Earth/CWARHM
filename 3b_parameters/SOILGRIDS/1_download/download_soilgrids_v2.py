# Download SOILGRIDS
# Code to download SOILGRIDS sand, silt & clay content maps, subset to the domain specified in the control file. The download workflow is:
# 1. Connect to the particular service for the data product we want to download (for a list of these, see: https://www.isric.org/explore/soilgrids/faq-soilgrids#What_do_the_filename_codes_mean or https://maps.isric.org/);
# 2. Specify the spatial extent and the soil depths we want;
# 3. Download data

# Notes on data scaling
# SOILGRIDS v2 native resolution is 250m in Homolosine projection. For consistency with the rest of the workflow, we download the data in the Marinus (WSG84) projection instead. Download resolution therefore is specified in lat/lon degrees. See: https://gis.stackexchange.com/questions/387025/how-can-i-download-soilgrids-v2-data-through-wcs-in-epsg4326-keeping-as-close

# modules
import math
from pathlib import Path
from shutil import copyfile
from datetime import datetime
from owslib.wcs import WebCoverageService # download util

# --- Control file handling
# Easy access to control file folder
controlFolder = Path('../../../0_controlFiles')

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
    

# --- Find where to save the data
# Find the path where the raw soil maps need to go
soilPath = read_from_control(controlFolder/controlFile,'parameter_soil_raw_path')

# Specify the default paths if required 
if soilPath == 'default':
    soilPath = make_default_path('parameters/soilclass/1_SOILGRIDS_raw_data') # outputs a Path()
else:
    soilPath = Path(soilPath) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
soilPath.mkdir(parents=True, exist_ok=True)


# --- Find spatial domain and data type to download
# Find which locations to download
coordinates = read_from_control(controlFolder/controlFile,'forcing_raw_space')

# Split coordinates into the format the download interface needs
coordinates = coordinates.split('/')

# Put coordinates in correct order in a tuple and convert to float
coordinates = (float(coordinates[1]), # minimum longitude
               float(coordinates[2]), # minimum latitude
               float(coordinates[3]), # maximum longitude
               float(coordinates[0])) # maximum latitude   
               
# Find which quantile/mean/uncertainty to download
download_value = read_from_control(controlFolder/controlFile,'parameter_soil_value')


# --- Specify download settings
# Specify the maps we want
url_base  = 'http://maps.isric.org/mapserv?map=/map/'
url_soils = ['sand','silt','clay']
url_end   = '.map'

# CRS
crs  = 'urn:ogc:def:crs:EPSG::4326'  # Should be supported by SOILGRIDS under wcs v1.0.0

# Data format
data_format = 'GEOTIFF_INT16' # Should be supported by SOILGRIDS under wcs v1.0.0

# Spatial resolution
if crs == 'urn:ogc:def:crs:EPSG::152160':
    resx,resy = 250,250 # [m]; native data projection and resolution

elif crs == 'urn:ogc:def:crs:EPSG::4326':
    # see: https://gis.stackexchange.com/questions/387025/how-can-i-download-soilgrids-v2-data-through-wcs-in-epsg4326-keeping-as-close
    a,b = 6378137,6356752 # [m]; major,minor axis of WSG84 datum
    phi_a = (coordinates[1]+coordinates[3])/2 # middle value of domain of interest - lat
    phi_b = (coordinates[0]+coordinates[2])/2 # middle value of domain of interest - lon
    resx  = abs(250 / (2*math.pi*a/360) * math.cos(phi_a)) # download resolution in degrees that minimizes distortion
    resy  = abs(250 / (2*math.pi*((a+b)/2)/360) ) # download resolution that minimizes distortion at middle latitudes
    
    
# --- Data download
# Loop over soil types
for soil in url_soils:
    
    # Construct the url
    url = url_base + soil + url_end
    
    # Connect through the appropriate web server
    # Note, use v1.0.0 instead of v2.0.1 because specification of bounding box in regular lat/lon is easier
    wcs = WebCoverageService(url, version='1.0.0')
    
    # Find the data names that contain the value we want; e.g. 'mean'
    identifiers = []
    for idf in list(wcs.contents):
        if download_value in idf:
            identifiers.append(idf)
            
    # Loop over the files (i.e. different depths)
    for current_id in identifiers:
        
        # Get data information
        data = wcs.contents[current_id]
        
        # Check that it is available in the crs we want
        if not crs in str( data.supportedCRS ):  # converted CRS objects to str for checking
            raise Exception ('Requested CRS {} not supported.'.format(crs))
            
        # Check that data is available in our format
        if not data_format in data.supportedFormats:
            raise Exception ('Requested format {} not supported.'.format(frmt))
            
        # Check that the bounding box is within available bounds
        if 'EPSG::4326' in crs: # This is necessary because this code specifically gets the EPSG:4326 bounding box
            coverage = data.boundingBoxWGS84 # available    
            bounding_box = (
                max(coverage[0],coordinates[0]),
                max(coverage[1],coordinates[1]),
                min(coverage[2],coordinates[2]),
                min(coverage[3],coordinates[3])) # limit the request to what is available; does nothing if request is within available bounds
            
        # Print
        print('File:   {} \nBbox:   {} \nCRS:    {} \nFormat: {} \n'.format(current_id,bounding_box,crs,data_format))
        
        # Get the response
        response = wcs.getCoverage(identifier = current_id,
                                   crs = crs,
                                   bbox = bounding_box,
                                   resx = resx, resy = resy,
                                   format = data_format)
        
        # Write the response to file
        with open( soilPath / (current_id + '.tif'), 'wb') as file:
            file.write(response.read())

# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = soilPath
log_suffix = '_soilgrids_download_log.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = 'download_soilgrids_v2.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Downloaded SOILGRIDS v2 data for space (lat_max, lon_min, lat_min, lon_max) [{}].'.format(coordinates)]
    for txt in lines:
        file.write(txt) 