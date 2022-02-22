# Create file manager
# Populates a text file with the required inputs for a SUMMA run.

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
    
    
# --- Find where the file manager needs to go
# Forcing file list path & name
filemanager_path = read_from_control(controlFolder/controlFile,'settings_summa_path')
filemanager_name = read_from_control(controlFolder/controlFile,'settings_summa_filemanager')

# Specify default path if needed
if filemanager_path == 'default':
    filemanager_path = make_default_path('settings/SUMMA') # outputs a Path()
else:
    filemanager_path = Path(filemanager_path) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
filemanager_path.mkdir(parents=True, exist_ok=True)


# --- Read the required information from the control file
# Get the experiment ID
# ----------------------
experiment_id = read_from_control(controlFolder/controlFile,'experiment_id')

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
    
# Paths - settings folder
# -----------------------
path_to_settings = read_from_control(controlFolder/controlFile,'settings_summa_path')

# Specify default path if needed
if path_to_settings == 'default':
    path_to_settings = make_default_path('settings/SUMMA') # outputs a Path()
else:
    path_to_settings = Path(path_to_settings) # make sure a user-specified path is a Path()
    
# Paths - forcing folder
# ----------------------
path_to_forcing = read_from_control(controlFolder/controlFile,'forcing_summa_path')

# Specify default path if needed
if path_to_forcing == 'default':
    path_to_forcing = make_default_path('forcing/4_SUMMA_input') # outputs a Path()
else:
    path_to_forcing = Path(path_to_forcing) # make sure a user-specified path is a Path()
    
# Paths - output folder
# ---------------------
path_to_output = read_from_control(controlFolder/controlFile,'experiment_output_summa')

# Specify default path if needed
if path_to_output == 'default':  
    path_to_output = make_default_path('simulations/' + experiment_id + '/SUMMA') # outputs a Path()
else:
    path_to_output = Path(path_to_output) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
path_to_output.mkdir(parents=True, exist_ok=True)

# File names of setting files
# ---------------------------
initial_conditions_nc = read_from_control(controlFolder/controlFile,'settings_summa_coldstate')
attributes_nc         = read_from_control(controlFolder/controlFile,'settings_summa_attributes')
trial_parameters_nc   = read_from_control(controlFolder/controlFile,'settings_summa_trialParams')
forcing_file_list_txt = read_from_control(controlFolder/controlFile,'settings_summa_forcing_list')


# - Make the file
# Create the file list
with open(filemanager_path / filemanager_name, 'w') as fm:
    
    # Header
    fm.write("controlVersion       'SUMMA_FILE_MANAGER_V3.0.0' !  file manager version \n")
    
    # Simulation times
    fm.write("simStartTime         '{}' ! \n".format(sim_start))
    fm.write("simEndTime           '{}' ! \n".format(sim_end))
    fm.write("tmZoneInfo           'utcTime' ! \n")
    
    # Prefix for SUMMA outputs
    fm.write("outFilePrefix        '{}' ! \n".format(experiment_id))
    
    # Paths
    fm.write("settingsPath         '{}/' ! \n".format(path_to_settings))
    fm.write("forcingPath          '{}/' ! \n".format(path_to_forcing))
    fm.write("outputPath           '{}/' ! \n".format(path_to_output))
    
    # Input file names
    fm.write("initConditionFile    '{}' ! Relative to settingsPath \n".format(initial_conditions_nc))
    fm.write("attributeFile        '{}' ! Relative to settingsPath \n".format(attributes_nc))
    fm.write("trialParamFile       '{}' ! Relative to settingsPath \n".format(trial_parameters_nc))
    fm.write("forcingListFile      '{}' ! Relative to settingsPath \n".format(forcing_file_list_txt))
    
    # Base files (not domain-dependent)
    fm.write("decisionsFile        'modelDecisions.txt' !  Relative to settingsPath \n")
    fm.write("outputControlFile    'outputControl.txt' !  Relative to settingsPath \n")
    fm.write("globalHruParamFile   'localParamInfo.txt' !  Relative to settingsPath \n")
    fm.write("globalGruParamFile   'basinParamInfo.txt' !  Relative to settingsPatho \n")
    fm.write("vegTableFile         'TBL_VEGPARM.TBL' ! Relative to settingsPath \n")
    fm.write("soilTableFile        'TBL_SOILPARM.TBL' ! Relative to settingsPath \n")
    fm.write("generalTableFile     'TBL_GENPARM.TBL' ! Relative to settingsPath \n")
    fm.write("noahmpTableFile      'TBL_MPTABLE.TBL' ! Relative to settingsPath \n")
    
    
# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.

# Set the log path and file name
logPath = filemanager_path
log_suffix = '_make_file_manager.txt'

# Create a log folder
logFolder = '_workflow_log'
Path( logPath / logFolder ).mkdir(parents=True, exist_ok=True)

# Copy this script
thisFile = '1_create_file_manager.py'
copyfile(thisFile, logPath / logFolder / thisFile);

# Get current date and time
now = datetime.now()

# Create a log file 
logFile = now.strftime('%Y%m%d') + log_suffix
with open( logPath / logFolder / logFile, 'w') as file:
    
    lines = ['Log generated by ' + thisFile + ' on ' + now.strftime('%Y/%m/%d %H:%M:%S') + '\n',
             'Generated file manager.']
    for txt in lines:
        file.write(txt) 