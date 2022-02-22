# Create control file
# Populates a text file with the required inputs for a mizuRoute run.

# modules
import os
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
    
    
# --- Find where the control file needs to go
# Forcing file list path & name
control_path = read_from_control(controlFolder/controlFile,'settings_mizu_path')
control_name = read_from_control(controlFolder/controlFile,'settings_mizu_control_file')

# Specify default path if needed
if control_path == 'default':
    control_path = make_default_path('settings/mizuRoute') # outputs a Path()
else:
    control_path = Path(control_path) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
control_path.mkdir(parents=True, exist_ok=True)


# --- Read the required information from control_active.txt
# Get the experiment ID
# ---------------------
experiment_id = read_from_control(controlFolder/controlFile,'experiment_id')

# Paths - settings folder
# -----------------------
path_to_settings = read_from_control(controlFolder/controlFile,'settings_mizu_path')

# Specify default path if needed
if path_to_settings == 'default':
    path_to_settings = make_default_path('settings/mizuRoute') # outputs a Path()
else:
    path_to_settings = Path(path_to_settings) # make sure a user-specified path is a Path()
    
# Paths - SUMMA output/mizuRoute input folder
# -------------------------------------------
path_to_input = read_from_control(controlFolder/controlFile,'experiment_output_summa')

# Specify default path if needed
if path_to_input == 'default':  
    path_to_input = make_default_path('simulations/' + experiment_id + '/SUMMA') # outputs a Path()
else:
    path_to_input = Path(path_to_input) # make sure a user-specified path is a Path()   

# Paths - mizuRoute output folder
# -------------------------------
path_to_output = read_from_control(controlFolder/controlFile,'experiment_output_mizuRoute')

# Specify default path if needed
if path_to_output == 'default':  
    path_to_output = make_default_path('simulations/' + experiment_id + '/mizuRoute') # outputs a Path()
else:
    path_to_output = Path(path_to_output) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
path_to_output.mkdir(parents=True, exist_ok=True)

# Parameter file
# --------------
par_file = read_from_control(controlFolder/controlFile,'settings_mizu_parameters')

# Simulation times
# ----------------
sim_start = read_from_control(controlFolder/controlFile,'experiment_time_start')
sim_end   = read_from_control(controlFolder/controlFile,'experiment_time_end')

# Define default times if needed
if sim_start == 'default':
    raw_time = read_from_control(controlFolder/controlFile,'forcing_raw_time') # downloaded forcing (years)
    year_start,_ = raw_time.split(',') # split into separate variables
    sim_start = year_start + '-01-01 00:00' # construct the filemanager field

if sim_end == 'default':
    raw_time = read_from_control(controlFolder/controlFile,'forcing_raw_time') # downloaded forcing (years)
    _,year_end = raw_time.split(',') # split into separate variables
    sim_end   = year_end   + '-12-31 23:00' # construct the filemanager field
    
# Topology settings
# -----------------
topology_nc  = read_from_control(controlFolder/controlFile,'settings_mizu_topology')

# Variables below are hard-coded in 1_create_network_topology.py to be consistent with mizuRoute docs
topology_seg = 'seg' 
topology_hru = 'hru' 
topology_outlet = '-9999' # Indicates to mizuRoute that it needs to route the full network and not use a subset

# Variable names below are hard-coded in 1_create_network_topology.py to be consistent with mizuRoute docs
topology_var_area       = 'area'
topology_var_length     = 'length'
topology_var_slope      = 'slope'
topology_var_hruId      = 'hruId'
topology_var_hruToSegId = 'hruToSegId'
topology_var_segId      = 'segId'
topology_var_downSegId  = 'downSegId'

# Remap settings
# --------------
remap_flag = read_from_control(controlFolder/controlFile,'river_basin_needs_remap')
if remap_flag.lower() == 'yes':
    do_remap          = 'T'
    remap_nc          = read_from_control(controlFolder/controlFile,'settings_mizu_remap')
    
    # Variables below are hard-coded in 1_remap_summa_catchments_to_routing.py to be consistent with mizuRoute docs
    remap_var_rn_hru  = 'RN_hruId' 
    remap_var_weight  = 'weight' 
    remap_var_hm_gru  = 'HM_hruId'
    remap_var_overlap = 'nOverlaps'
    remap_dim_hm_gru  = 'hru'
    remap_dim_data    = 'data'
else:
    do_remap = 'F'
    
# SUMMA output settings
# ---------------------
routing_nc  = experiment_id + '_timestep.nc'
routing_var_flow = read_from_control(controlFolder/controlFile,'settings_mizu_routing_var')
routing_var_flow_units = read_from_control(controlFolder/controlFile,'settings_mizu_routing_units')
routing_dt = read_from_control(controlFolder/controlFile, 'settings_mizu_routing_dt')

# Variables below are hard-coded in SUMMA
routing_dim_time = 'time'  
routing_var_time = 'time'  
routing_dim_id  = 'gru' 
routing_var_id  = 'gruId'

# Calendar setting
routing_nc_calendar = 'standard'

# Misc settings
# -------------
output_vars = read_from_control(controlFolder/controlFile,'settings_mizu_output_vars')
output_freq = read_from_control(controlFolder/controlFile,'settings_mizu_output_freq')
do_basin_route = read_from_control(controlFolder/controlFile,'settings_mizu_within_basin')


# --- Make the file
# Add some extra whitespace so (most of) the comments line up - easier to read that way
pad_to = 20 # should be slightly higher than length of longest setting value for maximum neatness

# Create the file list
with open(control_path / control_name, 'w') as cf:
    
    # Header
    cf.write("! mizuRoute control file generated by SUMMA public workflow scripts \n")
    
    # Folders
    cf.write("!\n! --- DEFINE DIRECTORIES \n")
    cf.write("<ancil_dir>             {:{}}/    ! Folder that contains ancillary data (river network, remapping netCDF) \n".format(path_to_settings.__str__(), pad_to))
    cf.write("<input_dir>             {:{}}/    ! Folder that contains runoff data from SUMMA \n".format(path_to_input.__str__(), pad_to))
    cf.write("<output_dir>            {:{}}/    ! Folder that will contain mizuRoute simulations \n".format(path_to_output.__str__(), pad_to))
    
    # Base parameters
    cf.write("!\n! --- NAMELIST FILENAME \n")
    cf.write("<param_nml>             {:{}}    ! Spatially constant parameter namelist (should be stored in <ancil_dir>) \n".format(par_file, pad_to))
    
    # Simulation settings
    cf.write("!\n! --- DEFINE SIMULATION CONTROLS \n")
    cf.write("<case_name>             {:{}}    ! Simulation case name. This used for output netCDF, and restart netCDF name \n".format(experiment_id, pad_to))
    cf.write("<sim_start>             {:{}}    ! Time of simulation start. format: yyyy-mm-dd or yyyy-mm-dd hh:mm:ss \n".format(sim_start, pad_to))
    cf.write("<sim_end>               {:{}}    ! Time of simulation end. format: yyyy-mm-dd or yyyy-mm-dd hh:mm:ss \n".format(sim_end, pad_to))
    cf.write("<route_opt>             {:{}}    ! Option for routing schemes. 0: both; 1: IRF; 2: KWT. Saves no data if not specified \n".format(output_vars, pad_to))
    cf.write("<newFileFrequency>      {:{}}    ! Frequency for new output files (single, day, month, or annual) \n".format(output_freq, pad_to))
    
    # Topology file
    cf.write("!\n! --- DEFINE TOPOLOGY FILE \n")
    cf.write("<fname_ntopOld>         {:{}}    ! Name of input netCDF for River Network \n".format(topology_nc, pad_to))
    cf.write("<dname_sseg>            {:{}}    ! Dimension name for reach in river network netCDF \n".format(topology_seg, pad_to))
    cf.write("<dname_nhru>            {:{}}    ! Dimension name for RN_HRU in river network netCDF \n".format(topology_hru, pad_to))
    cf.write("<seg_outlet>            {:{}}    ! Outlet reach ID at which to stop routing (i.e. use subset of full network). -9999 to use full network \n".format(topology_outlet, pad_to))   
    cf.write("<varname_area>          {:{}}    ! Name of variable holding hru area \n".format(topology_var_area, pad_to))
    cf.write("<varname_length>        {:{}}    ! Name of variable holding segment length \n".format(topology_var_length, pad_to))
    cf.write("<varname_slope>         {:{}}    ! Name of variable holding segment slope \n".format(topology_var_slope, pad_to))
    cf.write("<varname_HRUid>         {:{}}    ! Name of variable holding HRU id \n".format(topology_var_hruId, pad_to))
    cf.write("<varname_hruSegId>      {:{}}    ! Name of variable holding the stream segment below each HRU \n".format(topology_var_hruToSegId, pad_to))
    cf.write("<varname_segId>         {:{}}    ! Name of variable holding the ID of each stream segment \n".format(topology_var_segId, pad_to))
    cf.write("<varname_downSegId>     {:{}}    ! Name of variable holding the ID of the next downstream segment \n".format(topology_var_downSegId, pad_to))

    # SUMMA output
    cf.write("!\n! --- DEFINE RUNOFF FILE \n")
    cf.write("<fname_qsim>            {:{}}    ! netCDF name for HM_HRU runoff \n".format(routing_nc, pad_to))
    cf.write("<vname_qsim>            {:{}}    ! Variable name for HM_HRU runoff \n".format(routing_var_flow, pad_to))
    cf.write("<units_qsim>            {:{}}    ! Units of input runoff. e.g., mm/s \n".format(routing_var_flow_units, pad_to)) 
    cf.write("<dt_qsim>               {:{}}    ! Time interval of input runoff in seconds, e.g., 86400 sec for daily step \n".format(routing_dt, pad_to)) 
    cf.write("<dname_time>            {:{}}    ! Dimension name for time \n".format(routing_dim_time, pad_to))
    cf.write("<vname_time>            {:{}}    ! Variable name for time \n".format(routing_var_time, pad_to))
    cf.write("<dname_hruid>           {:{}}    ! Dimension name for HM_HRU ID \n".format(routing_dim_id, pad_to)) 
    cf.write("<vname_hruid>           {:{}}    ! Variable name for HM_HRU ID \n".format(routing_var_id, pad_to))
    cf.write("<calendar>              {:{}}    ! Calendar of the nc file if not provided in the time variable of the nc file \n".format(routing_nc_calendar, pad_to))
    
    # Remapping
    cf.write("!\n! --- DEFINE RUNOFF MAPPING FILE \n")
    cf.write("<is_remap>              {:{}}    ! Logical to indicate runoff needs to be remapped to RN_HRU. T or F \n".format(do_remap, pad_to))
    
    if remap_flag.lower() == 'yes':
        cf.write("<fname_remap>           {:{}}    ! netCDF name of runoff remapping \n".format(remap_nc, pad_to))
        cf.write("<vname_hruid_in_remap>  {:{}}    ! Variable name for RN_HRUs \n".format(remap_var_rn_hru, pad_to))
        cf.write("<vname_weight>          {:{}}    ! Variable name for areal weights of overlapping HM_HRUs \n".format(remap_var_weight, pad_to))
        cf.write("<vname_qhruid>          {:{}}    ! Variable name for HM_HRU ID \n".format(remap_var_hm_gru, pad_to))
        cf.write("<vname_num_qhru>        {:{}}    ! Variable name for a numbers of overlapping HM_HRUs with RN_HRUs \n".format(remap_var_overlap, pad_to))
        cf.write("<dname_hru_remap>       {:{}}    ! Dimension name for HM_HRU \n".format(remap_dim_hm_gru, pad_to))
        cf.write("<dname_data_remap>      {:{}}    ! Dimension name for data \n".format(remap_dim_data, pad_to))
    
    # Misc settings
    cf.write("!\n! --- MISCELLANEOUS \n")
    cf.write("<doesBasinRoute>        {:{}}    ! Hillslope routing options. 0 -> no (already routed by SUMMA), 1 -> use IRF".format(do_basin_route, pad_to)) # only for routing option 2
    

# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = control_path
log_suffix = '_make_control_file.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = '1_create_control_file.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Generated control file.']
    for txt in lines:
        file.write(txt) 