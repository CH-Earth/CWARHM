# ERA5 sanity check
# Checks if forcing data in merged ERA5 files are all:
# - Within user-specified ranges;
# - Not missing;
# - Not NaN.
#
# Also checks the time dimension in each file to find if timesteps are:
# - Not NaN;
# - Consecutive;
# - Equidistant.

# Modules
from pathlib import Path
from datetime import datetime
import netCDF4 as nc4
import numpy as np
import pandas as pd
import os
import sys

# --- User settings
# Location of merged files
path_to_data = Path('/project/gwf/gwf_cmt/wknoben/summaWorkflow_data/domain_NorthAmerica/forcing/2_merged_data')

# Location and name of logfile
log_folder = path_to_data / 'sanity_checks'
log_file = 'log_sanity_checks.txt'

# Make the output folder if doesn't exist
log_folder.mkdir(parents=True, exist_ok=True)

# File pattern
file_base = 'ERA5_merged_'
file_end = '.nc'

# Years to check (Jan-years[0] to Dec-years[1])
years = [1979,2019]

# "Feasible" variable ranges
ranges = {
    'pptrate':  [0,0.05], # 50 mm/h 
    'airpres':  [25000, 175000],
    'airtemp':  [173,373], # +/- 100 degrees C
    'spechum':  [0,1],
    'SWRadAtm': [0,2750], # 2 times solar constant
    'LWRadAtm': [0,1000], 
    'windspd':  [0,150], # 100 km/h above maximum gust known
}

# number of standard deviations to check
n = 8

# --- Standard settings
# Define the variables we want to check
var_names = {'time','pptrate','airpres','airtemp','spechum','SWRadAtm','LWRadAtm','windspd'}

# --- Checks
# Prepare a dictionary to store results in
report = {
    'file name': [],
    'data type': [],
    'data unit': [],
    'num NaNs': [],
    'num missing': [],
    'num < min': [],
    'num > max': []
}

# Open the log file
logFile = open(log_folder / log_file,'w')

# log start
logFile.write('Opened for writing on ' + str(datetime.now()) + '\n');

# Loop over variables first, so that reports aggregated per variable for easy comparison
for var in var_names:

    # Print where we are
    logFile.write('\n')
    logFile.write('Now checking variable // ' + var + ' // \n')
    if var == 'time':
        spacing = "{:20} {:10} {:35} {:10} {:15} {:15}\n"
        logFile.write(spacing.format('file_name',
                                     'data_type','data_unit',
                                     'num NaN',
                                     'consecutive?','equidistant?'))
    else:
        # Create the log headers
        head_min = 'num < {}'.format(ranges[var][0])
        head_max = 'num > {}'.format(ranges[var][1])
        head_low_out = 'num < {}*stdev'.format(n)
        head_upp_out = 'num > {}*stdev'.format(n)
        
        spacing = "{:20} {:10} {:35} {:10} {:18} {:12} {:12} {:15} {:15}\n"
        logFile.write(spacing.format('file_name',
                                     'data_type', 'data_unit',
                                     'num NaN', 'num missing_value',
                                     head_min,head_max,
                                     head_low_out,head_upp_out))
    
    # Loop over all files (year & month)
    for year in range(years[0],years[1]+1):
        for month in range(1,13):
        
            # Specify the file name
            file_name = (file_base + str(year) + str(month).zfill(2) + file_end)
            file_full = path_to_data / file_name

            # Check if this file exists
            if not os.path.isfile(file_full):
                continue
        
            # Open netcdf file for specific year and month
            with nc4.Dataset(file_full) as src:
            
                # Extract the variable into a numpy array
                dat = np.array(src[var][:])
                
                # Get basic information
                chk_size = dat.shape
                chk_isnan = np.isnan(dat).sum()
                
                # Get the information that depends on attributes
                try: chk_type = src[var].dtype
                except: chk_type = 'n/a'
                
                try: chk_units = src[var].units
                except: chk_units = 'n/a'
                
                try:
                    chk_missv = src[var].missing_value
                    chk_missn = (dat == chk_missv).sum()
                except:
                    chk_missv = chk_missn = 'n/a'

                # Get the standard deviation and mean
                stdv = np.std(dat)
                mean = np.mean(dat)
                
                # Count how often the data goes beyond the defined 'sane' ranges
                if var in ranges:
                    chk_min = ranges[var][0]
                    chk_max = ranges[var][1]                    
                    chk_under = (dat < chk_min).sum()
                    chk_over = (dat > chk_max).sum()
                    
                    # outliers
                    chk_neg_out = (dat < mean-n*stdv).sum()
                    chk_pos_out = (dat > mean+n*stdv).sum()                    
                else:
                    chk_under = 'n/a'
                    chk_over = 'n/a'
                
                # Check if time values are consecutive and equidistant
                if var == 'time':
                    if all(np.sort(dat) == dat): chk_cons = True 
                    else: chk_cons = False
                    if all(np.diff(dat) == 1): chk_equid = True 
                    else: chk_equid = False                    
                
                # update the dictionary
                report['file name'].append(file_name)
                report['data type'].append(chk_type)
                report['data unit'].append(chk_units)
                report['num NaNs'].append(chk_isnan)
                report['num missing'].append(chk_missn)
                report['num < min'].append(chk_under)
                report['num > max'].append(chk_over)
                
                # print to file
                if var == 'time':
                    logFile.write(spacing.format(str(file_name),
                                                 str(chk_type),
                                                 str(chk_units),
                                                 str(chk_isnan),
                                                 str(chk_cons),
                                                 str(chk_equid)))
                else:
                    logFile.write(spacing.format(str(file_name),
                                                 str(chk_type),
                                                 str(chk_units),
                                                 str(chk_isnan),
                                                 str(chk_missn),
                                                 str(chk_under),
                                                 str(chk_over),
                                                 str(chk_neg_out),
                                                 str(chk_pos_out)))
                    
# log end
logFile.write('\n')
logFile.write('Finished on ' + str(datetime.now()) + '\n');

# File handling
logFile.close()