# concatenate SUMMA domain-split outputs into time-split files
# Splits on calendar years by default, months optional

import os
import sys
import glob
import xarray as xr
from pathlib import Path


# --- check args
if len(sys.argv) != 9:
    print(""" Usage: %s <arg1> <arg2> <...> <arg8>
               arg1: summa output directory,       e.g. /path/to/summa/out/
               arg2: summa output file pattern,    e.g. run1_G*_day.nc
               arg3: summa variable of interest,   e.g. averageRoutedRunoff
               arg4: mizuRoute input directory,    e.g. /path/to/mizu/in/
               arg5: mizuRoute input file pattern, e.g. run1_{}.nc
               arg6: first data year,              e.g. 1979
               arg7: final data year,              e.g. 2019
               arg8: flag to split by months,           True/False""" % sys.argv[0])
    sys.exit(0)
    
# otherwise continue
src_dir = sys.argv[1] # e.g. '/path/to/summa/out/'
src_pat = sys.argv[2] # e.g. 'run1_G*_timestep.nc'
src_var = sys.argv[3] # e.g. 'averageRoutedRunoff'
des_dir = sys.argv[4] # e.g. '/path/to/mizu/in/'
des_fil = sys.argv[5] # e.g. 'run1_{}.nc'
split_s = sys.argv[6] # e.g. '1979'
split_e = sys.argv[7] # e.g. '2019'
split_m = sys.argv[8] # Split by months too: True/False


# Settings
#src_dir = '/scratch/wknoben/summaWorkflow_data/domain_NorthAmerica/simulations/run1/SUMMA'
#src_pat = 'run1_G*_timestep.nc'
#src_var = 'averageRoutedRunoff'
#des_dir = '/scratch/wknoben/summaWorkflow_data/domain_NorthAmerica/simulations/run1/intermediate'
#des_fil = 'run1_mizu_in_{}.nc'
#split_s = 1979
#split_e = 2019
#split_m = True

# Print flag
progres = False

# Make sure we're dealing with the right kind of inputs 
src_dir = Path(src_dir) 
des_dir = Path(des_dir)
split_s = int(split_s) 
split_e = int(split_e)

# Ensure the output path exists
des_dir.mkdir(parents=True, exist_ok=True) 

# Get the names of all inputs
src_files = glob.glob(str( src_dir / src_pat ))
src_files.sort()

# define the extraction function
def make_new_file(time):
    
    # Check if the file already exists and skip if sort
    if os.path.isfile(des_dir / des_fil.format(time)):
        print('file for {} already exists. Skipping.'.format(time))
        return
    else:
        print('Starting on file for {}.'.format(time))
    
    # Initialize a variable
    new = None
    
    # Loop over all identified files
    for src_file in src_files:
        
        # Progress print
        if progres:
            print('    ' + src_file)
        
        # Open the subset we need
        ds = xr.open_dataset(src_file).sel(time=time)
        
        # Keep only the variable of interest
        for var,da in ds.data_vars.items():
            if not var == src_var:
                ds = ds.drop(var)
        
        # Store/append
        if new is None:
            new = ds
        else:
            new = xr.merge([new,ds])
            
        ds.close()
            
    # Done looping, save to file
    new.to_netcdf(des_dir / des_fil.format(time))
    
    return # nothing, already saved


# run the loop
for year in range(split_s,split_e+1):
    if split_m:
        for month in range(1,13):
            this_time = str(year)+'-'+str(month).zfill(2)
            make_new_file(this_time)
    else:
        this_time = str(year)
        make_new_file(this_time)