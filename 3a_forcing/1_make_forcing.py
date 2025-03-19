# Copy base settings
# Copies the base settings into the mizuRoute settings folder.

# modules
import pandas as pd
import netCDF4 as nc4
import xarray as xr
import numpy as np
from pathlib import Path
from shutil import copyfile
from datetime import datetime

# --- Control file handling
# Easy access to control file folder
controlFolder = Path('../0_control_files')

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
    
    
# --- Find where the forcing data are

rootPath = Path( read_from_control(controlFolder/controlFile,'root_path') )
domainName = read_from_control(controlFolder/controlFile,'domain_name')

# CAMELS-spath
CAMELS_spath = read_from_control(controlFolder/controlFile,'camels_spath')

# Specify default path if needed
if CAMELS_spath == 'default':
    CAMELS_spath = rootPath / 'CAMELS-spat'
else:
    CAMELS_spath = Path(CAMELS_spath) # make sure a user-specified path is a Path()


# Metadata
metadata_path = CAMELS_spath
metadata_name = "camels-spat-metadata.csv"

df_metadata = pd.read_csv(metadata_path / metadata_name)


country, station_id = domainName.split("_")

# Get categories 
category_value = df_metadata.loc[(df_metadata['Country'] == country) & (df_metadata['Station_id'] == station_id), 'subset_category']

# Ensure category_value is a string
if not category_value.empty:
    category_value = category_value.iloc[0]  # Convert Series to string
else:
    raise ValueError("No matching subset category found.")  # Handle missing value
    
    
# Get timezone 
tz = df_metadata.loc[(df_metadata['Country'] == country) & (df_metadata['Station_id'] == station_id), 'dv_flow_obs_timezone']

# Ensure tz is a string
if not tz.empty:
    tz = tz.iloc[0]  # Convert Series to string
else:
    raise ValueError("No matching time zone found.")  # Handle missing value

# Spatialisation
spa = 'distributed'

# Forcing data product
forcing_name = read_from_control(controlFolder/controlFile,'forcing_data_name')

# Forcing path
forcing_path =  CAMELS_spath / 'forcing' / category_value / forcing_name / (forcing_name + "-" + spa)

# Simulation times
sim_start = read_from_control(controlFolder/controlFile,'experiment_time_start')
sim_end = read_from_control(controlFolder/controlFile,'experiment_time_end')


if sim_start == 'default':
    raw_time = read_from_control(controlFolder/controlFile,'forcing_raw_time') # downloaded forcing (years)
    year_start,_ = raw_time.split(',') # split into separate variables
    sim_start = year_start + '-01-01 00:00' # construct the filemanager field
    

if sim_end == 'default':
    raw_time = read_from_control(controlFolder/controlFile,'forcing_raw_time') # downloaded forcing (years)
    _,year_end = raw_time.split(',') # split into separate variables
    sim_end   = year_end   + '-12-31 23:00' # construct the filemanager field
    

forcing_file = domainName + "_" + forcing_name + "_" + spa +".nc"



# --- Find where the forcing data will be

forcing_summa_path = read_from_control(controlFolder/controlFile,'forcing_summa_path')

# Specify default path if needed
if forcing_summa_path == 'default':
    forcing_summa_path = make_default_path('forcing/4_SUMMA_input') # outputs a Path()
else:
    forcing_summa_path = Path(forcing_summa_path) # make sure a user-specified path is a Path()

# Make the folder if it doesn't exist
forcing_summa_path.mkdir(parents=True, exist_ok=True)


# --- Find the time step size of the forcing data
# Value in control file
data_step = read_from_control(controlFolder/controlFile,'forcing_time_step_size')

# Convert to int
data_step = int(data_step)


# Creation of nc files for SUMMA

# Function to create new nc variables
def create_and_fill_nc_var(ncid, var_name, var_type, dim, fill_val, fill_data, long_name, units):
    
    # Make the variable
    ncvar = ncid.createVariable(var_name, var_type, dim, fill_value = fill_val)
    
    # Add the data
    ncvar[:] = fill_data    
    
    # Add meta data
    ncvar.long_name = long_name 
    ncvar.units = units
    
    return 

def to_datetime(dates):
    date_list = list()
    for date in dates:
        
        timestamp = ((date - np.datetime64('1970-01-01T00:00:00'))
                     / np.timedelta64(1, 's'))
        date_list.append(datetime.utcfromtimestamp(timestamp))
    return(date_list)


    
# open forcing .nc file available in CAMELS-spat
nc_forcing = xr.open_dataset(forcing_path / forcing_file)

if forcing_name =="daymet":
    nc_forcing = nc_forcing.assign(tmean=(nc_forcing["tmin"] + nc_forcing["tmax"]) / 2)

# name of the output forcing .nc file for SUMMA
forcing_summa_name = forcing_file    


variable_mapping = {
    "air_pressure": {
        "era5": "sp",
        "rdrs": "RDRS_v2.1_P_P0_SFC",
    },
    "longwave_radiation": {
        "era5": "msdwlwrf",
        "rdrs": "RDRS_v2.1_P_FI_SFC"
        
    },
    "shortwave_radiation": {
        "era5": "msdwswrf",
        "daymet": "srad",
        "rdrs": "RDRS_v2.1_P_FB_SFC"
    },
    "precipitation": {
        "era5": "mtpr",
        "daymet": "prcp",
        "rdrs": "RDRS_v2.1_A_PR0_SFC",
        "em_earth": "prcp",
    },
    "air_temperature": {
        "era5": "t",
        "daymet": "tmean",  # Daymet has tmax and tmin
        "rdrs": "RDRS_v2.1_P_TT_1.5m",
        "em_earth": "tmean",
    },
    "windspeed": {
        "era5": "w",
        "rdrs": "RDRS_v2.1_P_UVC_10m",  # U and V components
    },
    "specific_humidity": {
        "era5": "q",
        "rdrs": "RDRS_v2.1_P_HU_1.5m",  # Relative humidity
    },
}


        
# Make the netcdf file
with nc4.Dataset(forcing_summa_path/forcing_summa_name, 'w', format='NETCDF4') as ncid:
        
    # Set general attributes
    now = datetime.now()
    ncid.setncattr('Author', "Created by SUMMA workflow scripts using CAMELS-spat database")
    ncid.setncattr('History','Created ' + now.strftime('%Y/%m/%d %H:%M:%S'))
    ncid.setncattr('Purpose','Create forcing .nc files for SUMMA')
    ncid.setncattr('Conventions', nc_forcing.attrs['Conventions'])
    ncid.setncattr('Source', nc_forcing.attrs['Source'])
        
    # Define the seg and hru dimensions
    ncid.createDimension('hru', len(nc_forcing['hru']))
    ncid.createDimension('time', len(nc_forcing['time']))
        
    # Time Variable        
    timevalue = to_datetime(nc_forcing['time'].values)
        
    time_varid = ncid.createVariable('time', nc_forcing['time'].encoding['dtype'], ('time', ))
        
    time_varid[:] = nc4.date2num(timevalue, \
                                 units = nc_forcing['time'].encoding['units'], \
                                 calendar = nc_forcing['time'].encoding['calendar']);
        
    time_varid.long_name = nc_forcing['time'].attrs['long_name']
    time_varid.units = nc_forcing['time'].encoding['units']
    time_varid.calendar = nc_forcing['time'].encoding['calendar']
    time_varid.standard_name = nc_forcing['time'].attrs['standard_name']
    time_varid.axis = nc_forcing['time'].attrs['axis']
        
        
    # Other Variables    
    create_and_fill_nc_var(ncid, 'latitude', \
                           nc_forcing['latitude'].encoding['dtype'], \
                           ('hru',), \
                           False, \
                           nc_forcing['latitude'].values[0, :].astype(float), \
                           nc_forcing['latitude'].attrs['long_name'], \
                           nc_forcing['latitude'].attrs['units'])
            
    create_and_fill_nc_var(ncid, 'longitude', \
                           nc_forcing['longitude'].encoding['dtype'], \
                           ('hru',), \
                           False, \
                           nc_forcing['longitude'].values[0, :].astype(float), \
                           nc_forcing['longitude'].attrs['long_name'], \
                           nc_forcing['longitude'].attrs['units'])
            
    create_and_fill_nc_var(ncid, 'hruId', \
                           nc_forcing['hruId'].encoding['dtype'], \
                           ('hru',), \
                           False, \
                           (10 * nc_forcing['hruId'].values[0, :]).astype(int), \
                           nc_forcing['hruId'].attrs['long_name'], \
                           nc_forcing['hruId'].attrs['units'])
    
    
    airpres_var = variable_mapping["air_pressure"].get(forcing_name)
    if airpres_var is not None:
        create_and_fill_nc_var(ncid, 'airpres', \
                               nc_forcing[airpres_var].encoding['dtype'], \
                               ('time','hru',), \
                               nc_forcing[airpres_var].encoding['_FillValue'], \
                               nc_forcing[airpres_var].values.astype(float), \
                               nc_forcing[airpres_var].attrs['long_name'], \
                               nc_forcing[airpres_var].attrs['units'])
    else:
        print(f"Warning: Air pressure data not available for {forcing_name}. Skipping...")
    
    longwave_radiation = variable_mapping["longwave_radiation"].get(forcing_name)    
    if airpres_var is not None:
        create_and_fill_nc_var(ncid, 'LWRadAtm', \
                               nc_forcing[longwave_radiation].encoding['dtype'], \
                               ('time','hru',), \
                               nc_forcing[longwave_radiation].encoding['_FillValue'], \
                               nc_forcing[longwave_radiation].values.astype(float), \
                               nc_forcing[longwave_radiation].attrs['long_name'], \
                               nc_forcing[longwave_radiation].attrs['units'])
    else:
        print(f"Warning: Long-wave radiation data not available for {forcing_name}. Skipping...")
            
    shortwave_radiation = variable_mapping["shortwave_radiation"].get(forcing_name)     
    if airpres_var is not None:
        create_and_fill_nc_var(ncid, 'SWRadAtm', \
                               nc_forcing[shortwave_radiation].encoding['dtype'], \
                               ('time','hru',), \
                               nc_forcing[shortwave_radiation].encoding['_FillValue'], \
                               nc_forcing[shortwave_radiation].values.astype(float), \
                               nc_forcing[shortwave_radiation].attrs['long_name'], \
                               nc_forcing[shortwave_radiation].attrs['units'])
    else:
        print(f"Warning: Short-wave radiation data not available for {forcing_name}. Skipping...")            
            
    precipitation = variable_mapping["precipitation"].get(forcing_name)  
    if airpres_var is not None:      
        create_and_fill_nc_var(ncid, 'pptrate', \
                               nc_forcing[precipitation].encoding['dtype'], \
                               ('time','hru',), \
                               nc_forcing[precipitation].encoding['_FillValue'], \
                               nc_forcing[precipitation].values.astype(float), \
                               nc_forcing[precipitation].attrs['long_name'], \
                               nc_forcing[precipitation].attrs['units'])
    else:
        print(f"Warning: Precipitation data not available for {forcing_name}. Skipping...")            
            
    air_temperature = variable_mapping["air_temperature"].get(forcing_name) 
    if airpres_var is not None:
        create_and_fill_nc_var(ncid, 'airtemp', \
                               nc_forcing[air_temperature].encoding['dtype'], \
                               ('time','hru',), \
                               nc_forcing[air_temperature].encoding['_FillValue'], \
                               nc_forcing[air_temperature].values.astype(float), \
                               nc_forcing[air_temperature].attrs['long_name'], \
                               nc_forcing[air_temperature].attrs['units'])
    else:
        print(f"Warning: Air temperature data not available for {forcing_name}. Skipping...")
            
    specific_humidity = variable_mapping["specific_humidity"].get(forcing_name)   
    if airpres_var is not None:
        create_and_fill_nc_var(ncid, 'spechum', \
                               nc_forcing[specific_humidity].encoding['dtype'], \
                               ('time','hru',), \
                               nc_forcing[specific_humidity].encoding['_FillValue'], \
                               nc_forcing[specific_humidity].values.astype(float), \
                               nc_forcing[specific_humidity].attrs['long_name'], \
                               nc_forcing[specific_humidity].attrs['units'])
    else:
        print(f"Warning: Specific humidity data not available for {forcing_name}. Skipping...")            

    windspeed = variable_mapping["windspeed"].get(forcing_name)     
    if airpres_var is not None:           
        create_and_fill_nc_var(ncid, 'windspd', \
                               nc_forcing[windspeed].encoding['dtype'], \
                               ('time','hru',), \
                               nc_forcing[windspeed].encoding['_FillValue'], \
                               nc_forcing[windspeed].values.astype(float), \
                               nc_forcing[windspeed].attrs['long_name'], \
                               nc_forcing[windspeed].attrs['units'])
    else:
        print(f"Warning: Windspeed data not available for {forcing_name}. Skipping...")            
            
            
    # Data step Variable
    datastep_varid = ncid.createVariable('data_step', 'int32')
        
    datastep_varid[:] = data_step
        
    datastep_varid.long_name = 'data step length in seconds'
    datastep_varid.units = 's'

    
    
# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = forcing_summa_path
log_suffix = '_make_forcing.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = '1_make_forcing.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Adapt CAMELS-spat forcing data for SUMMA and mizuRoute.']
    for txt in lines:
        file.write(txt) 