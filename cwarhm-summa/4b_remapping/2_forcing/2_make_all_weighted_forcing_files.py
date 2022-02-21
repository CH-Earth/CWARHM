# Create all area-weighted forcing files
# We need to find how the ERA5 gridded forcing maps onto the catchment to create area-weighted forcing as SUMMA input. This involves two steps:
# 1. Intersect the ERA5 shape with the user's catchment shape to find the overlap between a given (sub) catchment and the forcing grid;
# 2. Create an area-weighted, catchment-averaged forcing time series.
#
# The EASYMORE package (https://github.com/ShervanGharari/candex_newgen) provides the necessary functionality to do this. EASYMORE performs the GIS step (1, shapefile intersection) and the area-weighting step (2, create new forcing `.nc` files) as part of a single `nc_remapper()` call. To allow for parallelization, EASYMORE can save the output from the GIS step into a restart `.csv` file which can be used to skip the GIS step. This allows (manual) parallelization of area-weighted forcing file generation after the GIS procedures have been run once. The full workflow is thus:
# 1. [Previous script] Call `nc_remapper()` with ERA5 and user's shapefile, and one ERA5 forcing `.nc` file;
#    - EASYMORE performs intersection of both shapefiles;
#    - EASYMORE saves the outcomes of this intersection to a `.csv` file;
#    - EASYMORE creates an area-weighted forcing file from a single provided ERA5 source `.nc` file
# 2. [This script] Call `nc_remapper()` with intersection `.csv` file and all other forcing `.nc` files.
# 3. [Follow-up script] Apply lapse rates to temperature variable.
#
# Parallelization of step 2 (2nd `nc_remapper()` call) requires an external loop that sends (batches of) the remaining ERA5 raw forcing files to individual processors. As with other steps that may be parallelized, creating code that does this is left to the user.

# modules
import os
import easymore
from pathlib import Path
from shutil import rmtree
from shutil import copyfile
from datetime import datetime


# --- Control file handling
# Easy access to control file folder
controlFolder = Path('../../0_control_files')

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
    
    
# --- Find where the EASYMORE restart file is
# Intersected shapefile path. Name is set by EASYMORE as [prefix]_intersected_shapefile.shp
intersect_path = read_from_control(controlFolder/controlFile,'intersect_forcing_path')

# Specify default path if needed
if intersect_path == 'default':
    intersect_path = make_default_path('shapefiles/catchment_intersection/with_forcing') # outputs a Path()
else:
    intersect_path = Path(intersect_path) # make sure a user-specified path is a Path()
    
# Remapping filename
domain = read_from_control(controlFolder/controlFile,'domain_name')
remap_file = domain + '_remapping.csv'


# --- Find the forcing files (merged ERA5 data)
# Location of merged ERA5 files
forcing_merged_path = read_from_control(controlFolder/controlFile,'forcing_merged_path')

# Specify default path if needed
if forcing_merged_path == 'default':
    forcing_merged_path = make_default_path('forcing/2_merged_data') # outputs a Path()
else:
    forcing_merged_path = Path(forcing_merged_path) # make sure a user-specified path is a Path()
    
# Find files in folder
forcing_files = [forcing_merged_path/file for file in os.listdir(forcing_merged_path) if os.path.isfile(forcing_merged_path/file) and file.endswith('.nc')]

# Sort the files
forcing_files.sort()


# --- Find where the area-weighted forcing needs to go
# Location for SUMMA-ready files
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

# ERA5 netcdf variable names
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
esmr.temp_dir = '' # Force this to be empty

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
esmr.remap_csv = str(intersect_path / remap_file)

# Enforce that we want our HRUs returned in the order we put them in
esmr.sort_ID = False

# Flag that we want to skip existing remap files
esmr.overwrite_existing_remap = False

# --- Run EASYMORE - this can be parallelized for speed ups
# Loop over the remaining forcing files
for file in forcing_files[1:]: # skip the first one, as we completed that in the previous script  
    
    # ERA5 forcing files to use
    esmr.source_nc = str(file) # Path() to string
    
    # Note on centroid warnings: in this case we use a regular lat/lon grid to represent ERA5 forcing and ...
    #     centroid estimates without reprojecting are therefore acceptable.
    # Note on deprecation warnings: this is an EASYMORE issue that cannot be resolved here. Does not affect current use.
    esmr.nc_remapper()
    
    
# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = forcing_basin_path
log_suffix = '_create_all_weighted_forcing_file_log.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = '2_make_all_weighted_forcing_files.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Made all remaining weighted forcing files based on restart file from intersected shapefiles of catchment and ERA5.']
    for txt in lines:
        file.write(txt)  