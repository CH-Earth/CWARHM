#!/usr/bin/env python
# coding: utf-8

# # Catchment and river network delineation
# Plots the shapefiles provided for use in SUMMA and mizuRoute setup side by side.

# In[1]:

from pathlib import Path
import shutil
# #### Control file handling

# In[2]:


# Easy access to control file folder
controlFolder = Path('../0_control_files')


# In[3]:


# Store the name of the 'active' file in a variable
controlFile = 'control_active.txt'


# In[4]:


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


# In[5]:


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



# #### Define where to find the figure

# In[6]:

rootPath = Path( read_from_control(controlFolder/controlFile,'root_path') )
domainName = read_from_control(controlFolder/controlFile,'domain_name')

# CAMELS-spath
CAMELS_spath = read_from_control(controlFolder/controlFile,'camels_spath')

# Specify default path if needed
if CAMELS_spath == 'default':
    CAMELS_spath = rootPath / 'CAMELS-spat'
else:
    CAMELS_spath = Path(CAMELS_spath) # make sure a user-specified path is a Path()

# Forcing path
fig_path_in =  CAMELS_spath / domainName / 'forcing'



# #### Define where to save the figure

# In[7]:

# Path and filename
fig_path = read_from_control(controlFolder/controlFile,'visualization_folder')

# Specify default path if needed
if fig_path == 'default':
    fig_path = make_default_path('visualization') # outputs a Path()
else:
    fig_path = Path(fig_path) # make sure a user-specified path is a Path()

# Make the folder if it doesn't exist
fig_path.mkdir(parents=True, exist_ok=True)

for png_file in fig_path_in.glob('*.png'):
    shutil.copy(png_file, fig_path)
