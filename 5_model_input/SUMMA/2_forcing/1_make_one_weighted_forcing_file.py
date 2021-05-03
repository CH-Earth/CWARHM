# Create one (1) area-weighted forcing file
# We need to find how the ERA5 gridded forcing maps onto the catchment to create area-weighted forcing as SUMMA input. This involves two steps:
# 1. Intersect the ERA5 shape with the user's catchment shape to find the overlap between a given (sub) catchment and the forcing grid;
# 2. Create an area-weighted, catchment-averaged forcing time series.
#
# The EASYMORE package (https://github.com/ShervanGharari/EASYMORE) provides the necessary functionality to do this. EASYMORE performs the GIS step (1, shapefile intersection) and the area-weighting step (2, create new forcing `.nc` files) as part of a single `nc_remapper()` call. To allow for parallelization, EASYMORE can save the output from the GIS step into a restart `.csv` file which can be used to skip the GIS step. This allows (manual) parallelization of area-weighted forcing file generation after the GIS procedures have been run once. The full workflow here is thus:
# 1. [This script] Call `nc_remapper()` with ERA5 and user's shapefile, and one ERA5 forcing `.nc` file;
#    - EASYMORE performs intersection of both shapefiles;
#    - EASYMORE saves the outcomes of this intersection to a `.csv` file;
#    - EASYMORE creates an area-weighted forcing file from a single provided ERA5 source `.nc` file
# 2. [Follow-up script] Call `nc_remapper()` with intersection `.csv` file and all other forcing `.nc` files.
# 3. [Follow-up script] Apply lapse rates to temperature variable.
#
# Parallelization of step 2 (2nd `nc_remapper()` call) requires an external loop that sends (batches of) the remaining ERA5 raw forcing files to individual processors. As with other steps that may be parallelized, creating code that does this is left to the user.

# modules
import os
import glob
import easymore
from pathlib import Path
from shutil import rmtree
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
    
    
# --- Find location of shapefiles
# Catchment shapefile path & name
catchment_path = read_from_control(controlFolder/controlFile,'intersect_dem_path')
catchment_name = read_from_control(controlFolder/controlFile,'intersect_dem_name')

# Specify default path if needed
if catchment_path == 'default':
    catchment_path = make_default_path('shapefiles/catchment_intersection/with_dem') # outputs a Path()
else:
    catchment_path = Path(catchment_path) # make sure a user-specified path is a Path()
    
# Forcing shapefile path & name
forcing_shape_path = read_from_control(controlFolder/controlFile,'forcing_shape_path')
forcing_shape_name = read_from_control(controlFolder/controlFile,'forcing_shape_name')

# Specify default path if needed
if forcing_shape_path == 'default':
    forcing_shape_path = make_default_path('shapefiles/forcing') # outputs a Path()
else:
    forcing_shape_path = Path(forcing_shape_path) # make sure a user-specified path is a Path()
    
    
# --- Find where the intersection needs to go
# Intersected shapefile path. Name is set by EASYMORE as [prefix]_intersected_shapefile.shp
intersect_path = read_from_control(controlFolder/controlFile,'intersect_forcing_path')

# Specify default path if needed
if intersect_path == 'default':
    intersect_path = make_default_path('shapefiles/catchment_intersection/with_forcing') # outputs a Path()
else:
    intersect_path = Path(intersect_path) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
intersect_path.mkdir(parents=True, exist_ok=True)


# --- Find the forcing files (merged ERA5 data)
# Location of merged ERA5 files
forcing_merged_path = read_from_control(controlFolder/controlFile,'forcing_merged_path')

# Specify default path if needed
if forcing_merged_path == 'default':
    forcing_merged_path = make_default_path('forcing/2_merged_data') # outputs a Path()
else:
    forcing_merged_path = Path(forcing_merged_path) # make sure a user-specified path is a Path()
    
# Find files in folder
forcing_files = [forcing_merged_path/file for file in os.listdir(forcing_merged_path) if os.path.isfile(forcing_merged_path/file)]

# Sort the files
forcing_files.sort()


# --- Find where the temporary EASYMORE files need to go
# Location for EASYMORE temporary storage
forcing_easymore_path = read_from_control(controlFolder/controlFile,'forcing_easymore_path')

# Specify default path if needed
if forcing_easymore_path == 'default':
    forcing_easymore_path = make_default_path('forcing/3_temp_easymore') # outputs a Path()
else:
    forcing_easymore_path = Path(forcing_easymore_path) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
forcing_easymore_path.mkdir(parents=True, exist_ok=True)


# --- Find where the area-weighted forcing needs to go
# Location for EASYMORE forcing output
forcing_basin_path = read_from_control(controlFolder/controlFile,'forcing_basin_avg_path')

# Specify default path if needed
if forcing_basin_path == 'default':
    forcing_basin_path = make_default_path('forcing/3_basin_averaged_data') # outputs a Path()
else:
    forcing_basin_path = Path(forcing_basin_path) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
forcing_basin_path.mkdir(parents=True, exist_ok=True)


# --- EASYMORE
# Initialize an EASYMORE object
esmr = easymore.easymore()

# Author name
esmr.author_name = 'SUMMA public workflow scripts'

# Data license
esmr.license = 'Copernicus data use license: https://cds.climate.copernicus.eu/api/v2/terms/static/licence-to-use-copernicus-products.pdf'

# Case name, used in EASYMORE-generated file naes
esmr.case_name = read_from_control(controlFolder/controlFile,'domain_name')

# ERA5 shapefile and variable names
# Variable names can be hardcoded because we set them when we generate this shapefile as part of the workflow
esmr.source_shp     = forcing_shape_path/forcing_shape_name # shapefile
esmr.source_shp_lat = read_from_control(controlFolder/controlFile,'forcing_shape_lat_name') # name of the latitude field
esmr.source_shp_lon = read_from_control(controlFolder/controlFile,'forcing_shape_lon_name') # name of the longitude field

# Catchment shapefile and variable names
esmr.target_shp = catchment_path/catchment_name
esmr.target_shp_ID  = read_from_control(controlFolder/controlFile,'catchment_shp_hruid') # name of the HRU ID field
esmr.target_shp_lat = read_from_control(controlFolder/controlFile,'catchment_shp_lat')   # name of the latitude field
esmr.target_shp_lon = read_from_control(controlFolder/controlFile,'catchment_shp_lon')   # name of the longitude field

# ERA5 netcdf file and variable names
esmr.source_nc = str(forcing_files[0]) # first file in the list; Path() to string
esmr.var_names = ['airpres',
                  'LWRadAtm',
                  'SWRadAtm',
                  'pptrate',
                  'airtemp',
                  'spechum',
                  'windspd'] # variable names of forcing data - hardcoded because we prescribe them during ERA5 merging
esmr.var_lat   = 'latitude'  # name of the latitude dimensions
esmr.var_lon   = 'longitude' # name of the longitude dimension
esmr.var_time  = 'time'      # name of the time dimension

# Temporary folder where the EASYMORE-generated GIS files and remapping file will be saved
esmr.temp_dir = str(forcing_easymore_path) + '/' # Path() to string; ensure the trailing '/' EASYMORE wants

# Output folder where the catchment-averaged forcing will be saved
esmr.output_dir = str(forcing_basin_path) + '/' # Path() to string; ensure the trailing '/' EASYMORE wants

# Netcdf settings
esmr.remapped_dim_id = 'hru'     # name of the non-time dimension; prescribed by SUMMA
esmr.remapped_var_id = 'hruId'   # name of the variable associated with the non-time dimension
esmr.format_list     = ['f4']    # variable type to save forcing as. Single entry here will be used for all variables
esmr.fill_value_list = ['-9999'] # fill value

# Flag that we do not want the data stored in .csv in addition to .nc
esmr.save_csv  = False

# Flag that we currently have no remapping file
esmr.remap_csv = ''  

# Enforce that we want our HRUs returned in the order we put them in
esmr.sort_ID = False

# Run EASYMORE
# Note on centroid warnings: in this case we use a regular lat/lon grid to represent ERA5 forcing and ...
#     centroid estimates without reprojecting are therefore acceptable.
# Note on deprecation warnings: this is a EASYMORE issue that cannot be resolved here. Does not affect current use.
esmr.nc_remapper()


# --- Move files to prescribed locations
# Remapping file 
remap_file = esmr.case_name + '_remapping.csv'
copyfile( esmr.temp_dir + remap_file, intersect_path / remap_file);

# Intersected shapefile
for file in glob.glob(esmr.temp_dir + esmr.case_name + '_intersected_shapefile.*'):
    copyfile( file, intersect_path / os.path.basename(file));
    
# Remove the temporary EASYMORE directory to save space
try:
    rmtree(esmr.temp_dir)
except OSError as e:
    print ("Error: %s - %s." % (e.filename, e.strerror))  
    
    
# --- Code provenance - intersection shapefile
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = intersect_path
log_suffix = '_catchment_forcing_intersect_log.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = '1_make_one_weighted_forcing_file.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Intersect shapefiles of catchment and ERA5.']
    for txt in lines:
        file.write(txt) 


# --- Code provenance - weighted forcing file
# Generates a basic log file in the domain folder and copies the control file and itself there.        

# Set the log path and file name
logPath = forcing_basin_path
log_suffix = '_create_one_weighted_forcing_file_log.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = '1_make_one_weighted_forcing_file.ipynb'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Made a weighted forcing file based on intersect shapefiles of catchment and ERA5.']
    for txt in lines:
        file.write(txt)  