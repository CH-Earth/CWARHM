#!/usr/bin/env python
# coding: utf-8

# # SWE and streamflow
# Plots maximum annual SWE per HRU and mean annual streamflow per stream segment. Needs:
# - Catchment shapefile with HRU delineation
# - River network shapefile with stream segments
# - SUMMA output `scalarSWE`
# - mizuRoute output `KWTroutedRunoff`

# In[1]:


# modules
import os
import numpy as np
import xarray as xr
import geopandas as gpd
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


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


# #### Define where to save the figure

# In[6]:


# Path and filename
fig_path = read_from_control(controlFolder/controlFile,'visualization_folder')
fig_name = 'mean_elevation_per_hru_AND_mean_annual_streamflow_per_segment_AND_mean_max_swe_per_hru_FOR_bowAtBanff_v2.png'

# Specify default path if needed
if fig_path == 'default':
    fig_path = make_default_path('visualization') # outputs a Path()
else:
    fig_path = Path(fig_path) # make sure a user-specified path is a Path()
    
# Make the folder if it doesn't exist
fig_path.mkdir(parents=True, exist_ok=True)


# #### Get shapefile location from control file

# In[7]:


# HM catchment shapefile path & name
hm_catchment_path = read_from_control(controlFolder/controlFile,'catchment_shp_path')
hm_catchment_name = read_from_control(controlFolder/controlFile,'catchment_shp_name')

# Specify default path if needed
if hm_catchment_path == 'default':
    hm_catchment_path = make_default_path('shapefiles/catchment') # outputs a Path()
else:
    hm_catchment_path = Path(hm_catchment_path) # make sure a user-specified path is a Path()


# In[8]:


# Find the GRU and HRU identifiers
hm_gruid = read_from_control(controlFolder/controlFile,'catchment_shp_gruid')
hm_hruid = read_from_control(controlFolder/controlFile,'catchment_shp_hruid')


# #### Get the shapefile with elevation for comparison purposes

# In[9]:


# Intersection of catchment shapefile and DEM; path & name
elev_catchment_path = read_from_control(controlFolder/controlFile,'intersect_dem_path')
elev_catchment_name = read_from_control(controlFolder/controlFile,'intersect_dem_name')

# Specify default path if needed
if elev_catchment_path == 'default':
    elev_catchment_path = make_default_path('shapefiles/catchment_intersection/with_dem') # outputs a Path()
else:
    elev_catchment_path = Path(elev_catchment_path) # make sure a user-specified path is a Path()


# #### Get the shapefile with the river network

# In[10]:


# River network path & name
river_network_path = read_from_control(controlFolder/controlFile,'river_network_shp_path')
river_network_name = read_from_control(controlFolder/controlFile,'river_network_shp_name')

# Specify default path if needed
if river_network_path == 'default':
    river_network_path = make_default_path('shapefiles/river_network') # outputs a Path()
else:
    river_network_path = Path(river_network_path) # make sure a user-specified path is a Path()


# In[11]:


# Find the segment ID
seg_id = read_from_control(controlFolder/controlFile,'river_network_shp_segid')


# #### Find the location of the simulations

# In[12]:


# SUMMA simulation path
summa_output_path = read_from_control(controlFolder/controlFile,'experiment_output_summa')
experiment_id = read_from_control(controlFolder/controlFile,'experiment_id')

# Specify default path if needed
if summa_output_path == 'default':
    summa_output_path = make_default_path('simulations/' + experiment_id + '/SUMMA') # outputs a Path()
else:
    summa_output_path = Path(summa_output_path) # make sure a user-specified path is a Path()


# In[13]:


# Specify the output file name and variable of interest
summa_output_name = experiment_id + '_day.nc'
summa_plot_var = 'scalarSWE'


# In[14]:


# mizuRoute simulation path
mizu_output_path = read_from_control(controlFolder/controlFile,'experiment_output_mizuRoute')
experiment_id = read_from_control(controlFolder/controlFile,'experiment_id')

# Specify default path if needed
if mizu_output_path == 'default':
    mizu_output_path = make_default_path('simulations/' + experiment_id + '/mizuRoute') # outputs a Path()
else:
    mizu_output_path = Path(mizu_output_path) # make sure a user-specified path is a Path()


# In[15]:


# Specify the variable of interest
mizu_output_name = 'run1*.nc'
mizu_plot_var = 'KWTroutedRunoffroutedRunoff'


# #### Load the shape and data

# In[16]:


# catchment shapefile
shp_catchment = gpd.read_file(hm_catchment_path/hm_catchment_name)


# In[17]:


# river shapefile
shp_river = gpd.read_file(river_network_path/river_network_name)


# In[18]:


# catchment with DEM
shp_elev = gpd.read_file(elev_catchment_path/elev_catchment_name)


# In[19]:


# SUMMA simulations
sim_summa = xr.open_dataset(summa_output_path/summa_output_name)


# In[20]:


# mizuRoute simulations
mizu_files = [mizu_output_path/file for file in os.listdir(mizu_output_path) if file.endswith('.nc')] # find all files
sim_mizu = xr.merge( xr.open_dataset(file) for file in mizu_files) # open all files into a single dataset


# #### Add a water year definition

# In[21]:


# Define in which month the water year starts
water_year_start = 'Oct' # Assumed to be on the 1st of the month


# In[22]:


# Convert month the number 
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
start_month = months.index(water_year_start) + 1 # add 1 to account for 0-based indexing in Python


# In[23]:


# Add a water year variable for grouping
sim_summa['water_year'] = sim_summa['time'].dt.year # set initial year
sim_mizu['water_year'] = sim_mizu['time'].dt.year # set initial year


# In[24]:


# Overwrite the year for months that are part of the water year that started last calendar year
# sim_summa['water_year'].loc[sim_summa['time'].dt.month < start_month] -= 1
# sim_mizu['water_year'].loc[sim_mizu['time'].dt.month < start_month] -= 1


# #### Preprocessing

# In[25]:


# Select only complete water years
complete_water_years_summa = (sim_summa['water_year'] > min(sim_summa['water_year'])) & (sim_summa['water_year'] < max(sim_summa['water_year']))
complete_water_years_mizu = (sim_mizu['water_year'] > min(sim_mizu['water_year'])) & (sim_mizu['water_year'] < max(sim_mizu['water_year']))


# In[26]:


# Find the mean maximum water-year SWE per HRU
plot_dat_summa = sim_summa[summa_plot_var].sel(time=complete_water_years_summa).groupby(sim_summa['water_year'].sel(time=complete_water_years_summa)).max(dim='time').mean(dim='water_year')


# In[27]:


# Find the mean water-year streamflow per HRU
plot_dat_mizu = sim_mizu[mizu_plot_var].sel(time=complete_water_years_mizu).groupby(sim_mizu['water_year'].sel(time=complete_water_years_mizu)).mean(dim='time').mean(dim='water_year')


# In[28]:


# Match the accummulated values to the correct HRU IDs in the SUMMA shapefile
hru_ids_shp = shp_catchment[hm_hruid] # hru order in shapefile
shp_catchment['plot_var'] = plot_dat_summa.sel(hru=hru_ids_shp.values)


# In[29]:


# Match the accummulated values to the correct stream IDs in the shapefile
seg_ids_shp = shp_river[seg_id] # stream segment order in shapefile
shp_river['plot_var'] = plot_dat_mizu.sel(seg=np.where(sim_mizu['reachID'].values == seg_ids_shp.values.astype('int'))[0])


# In[30]:


# Get the units of our plotting variable
units_summa = sim_summa[summa_plot_var].units
units_mizu = sim_mizu[mizu_plot_var].units



# In[41]:


# Format the units into something nicer
units_summa = '$kg~m^{-2}$' # LaTeX syntax: $ for math mode, ~ for space, ^ for superscript, _ for subscript, {} to group
units_mizu  = '$m^3~s^{-1}$'


# In[38]:


# Create a shapefile with only GRU boundaries for overlay
hm_grus_only = shp_catchment[[hm_gruid,'geometry']] # keep only the gruId and geometry
hm_grus_only = hm_grus_only.dissolve(by=hm_gruid) # Dissolve HRU delineation


# #### Define where the outlet is

# In[32]:


outlet_lat,outlet_lon = 51.167,-115.555


# In[33]:


def add_outlet(ax,lat,lon):
    ax.plot(lon,lat,linestyle='None',marker='o',color='r',markersize=10,label='outlet')
    return


# #### Figure

# In[34]:


# Set a colormap
cmap_elev = 'terrain'
cmap_q = 'Blues'
cmap_swe = 'pink'


# In[35]:


size = 16
plt.rcParams.update({'font.size': size, 
                     'axes.labelsize': size, 
                     'xtick.labelsize': size, 
                     'ytick.labelsize': size})


# In[43]:


fig, axs = plt.subplots(1,2,figsize=(20,10))
plt.tight_layout()

# --- elevation
axId = 0

# Data
shp_elev.plot(ax=axs[axId], column='elev_mean',edgecolor='k', cmap = cmap_elev, legend=False)
hm_grus_only.plot(ax=axs[axId],facecolor='none',edgecolor='k',linewidth=2) 
# add_outlet(axs[axId],outlet_lat,outlet_lon)

# Custom colorbar
cax = fig.add_axes([0.46, 0.1, 0.02, 0.5])
vmin,vmax = shp_elev['elev_mean'].min(),shp_elev['elev_mean'].max()
sm = plt.cm.ScalarMappable(cmap=cmap_elev, norm=plt.Normalize(vmin=vmin, vmax=vmax))
sm._A = []
cbr = fig.colorbar(sm, cax=cax)
cbr.ax.set_title('$[m.a.s.l.]$')

# Custom legend
lines = [Line2D([0], [0], color='k', lw=2),
         Line2D([0], [0], color='k', lw=1),
         Line2D([0], [0], color='r', linestyle='None', marker='.', markersize=10, lw=2)]
label = ['SUMMA GRUs',
         'SUMMA HRUs',
         'Outlet']
axs[axId].legend(lines,label,loc='lower left');

# Chart junk
axs[axId].set_title('(a) Mean HRU elevation derived from MERIT DEM');
axs[axId].set_frame_on(False)
axs[axId].set_xlabel('Longitude [degrees East]')
axs[axId].set_ylabel('Latitude [degrees North]')


# --- mean flow
axId = 1

# Data
shp_catchment.plot(ax=axs[axId], column='plot_var',edgecolor='k', cmap = cmap_swe, legend=False)
hm_grus_only.plot(ax=axs[axId],facecolor='none',edgecolor='k',linewidth=2) 
shp_river.plot(ax=axs[axId], column='plot_var', cmap=cmap_q,linewidth=5)
# add_outlet(axs[axId],outlet_lat,outlet_lon)

# Custom colorbars
cax = fig.add_axes([0.96, 0.1, 0.02, 0.5])
vmin,vmax = shp_catchment['plot_var'].min(),shp_catchment['plot_var'].max()
sm = plt.cm.ScalarMappable(cmap=cmap_swe, norm=plt.Normalize(vmin=vmin, vmax=vmax))
sm._A = []
cbr = fig.colorbar(sm, cax=cax)
cbr.ax.set_title('[{}]'.format(units_summa))

cax = fig.add_axes([1.02, 0.1, 0.02, 0.5])
vmin,vmax = shp_river['plot_var'].min(),shp_river['plot_var'].max()
sm = plt.cm.ScalarMappable(cmap=cmap_q, norm=plt.Normalize(vmin=vmin, vmax=vmax))
sm._A = []
cbr = fig.colorbar(sm, cax=cax)
cbr.ax.set_title('[{}]'.format(units_mizu))

# Chart junk
axs[axId].set_title('(b) Mean annual max SWE and mean annual Q');
axs[axId].set_frame_on(False)
axs[axId].set_xlabel('Longitude [degrees East]')


# Save 
plt.savefig(fig_path/fig_name, bbox_inches='tight', transparent=True, dpi=300)


# In[ ]:




