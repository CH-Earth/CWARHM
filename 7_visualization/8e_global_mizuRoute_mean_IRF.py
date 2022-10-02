#!/usr/bin/env python
# coding: utf-8

# # Global streamflow
# Plots mean January streamflow per stream segment. Needs:
# - River network shapefiles with stream segments
# - mizuRoute output `IRFroutedRUnoff`
# 
# Possibly relevant:
# - Geopandas dataframes are plotted from the first entry to the last. If we put the most import entries last, they will appear on top of the rest. It could be helpful to sort the river network by flow magnitude, so that the smaller segments form the background and we actually see the large-domain patterns.

import glob
import matplotlib
import numpy as np
import xarray as xr
import pandas as pd
import geopandas as gpd
from pathlib import Path
import matplotlib.pyplot as plt

# #### In/out file locations
# Define the domains we're working with
domains    = ['Africa','Europe','NorthAmerica','NorthAsia','Oceania','SouthAmerica','SouthAsia']

# Define the river segment shapefile location and names
river_path  = Path('/gpfs/tp/gwf/gwf_cmt/wknoben/CWARHM_data/domain_global/shapefiles/robinson')
river_name  = 'rivers_{}_robinson.shp'
river_segId = 'COMID' 

# Define the lakes shapefile 
lakes_path = Path('/gpfs/tp/gwf/gwf_cmt/wknoben/CWARHM_data/domain_global/shapefiles/robinson')
lakes_name = 'HydroLAKES_polys_v10_robinson.shp'

# Define the continent outline shapefile
continents_path = Path('/gpfs/tp/gwf/gwf_cmt/wknoben/CWARHM_data/domain_global/shapefiles/robinson')
continents_name = 'World_region_Robinson.shp'

# Define the simulation results
stats_path = Path('/gpfs/tp/gwf/gwf_cmt/wknoben/CWARHM_data/domain_global/simulation_stats')
stats_name = 'mizuRoute_stat_197901_{}.nc'
stats_segId = 'reachID'
stats_varId = 'IRFroutedRunoff'

# Define where to save the figure
fig_path = Path('/gpfs/tp/gwf/gwf_cmt/wknoben/CWARHM_data/domain_global/visualization')
fig_name = 'mean_january_1979_streamflow_per_segment_FOR_global_v12.png'

# Make the folder if it doesn't exist
fig_path.mkdir(parents=True, exist_ok=True)


# #### Load shapefiles and data
shp_list = []
for domain in domains:
    shp_list.append(gpd.read_file(river_path/river_name.format(domain)))
shp = pd.concat(shp_list)

lakes = gpd.read_file(lakes_path / lakes_name)
continents = gpd.read_file(continents_path/continents_name)

sims = xr.Dataset()
for domain in domains:
    sim = xr.open_dataset(stats_path/stats_name.format(domain))
    sim['seg'] = sim[stats_segId]
    sim = sim.isel(time=0).drop_vars(['time','time_bnds']) # Remove all time info because we know these files contain only a monthly mean value
    sims = xr.merge([sims,sim])

# #### Perform a check to see if we have data for each river segment
# Polygon order in the simulation file
seg_ids_sim = sims[stats_segId].values.astype('int')

# Ensure that the shapefile is in the same order as the sims
shp = shp.set_index(shp[river_segId].astype('int')) # set the index
shp = shp.reindex(seg_ids_sim) # reindex to be in same order as sims file

# Add the simulations to the shape
shp[stats_varId] = sims[stats_varId].values

# Sort the river shapefile so that rivers are sorted from small to large flows
shp = shp.sort_values(by='IRFroutedRunoff')

# #### Prepare plotting settings
# River settings
linewidth = np.maximum(np.log10(shp[stats_varId])-2,0)
river_col = 'Blues'
river_ttl = '(c) Mean simulated streamflow'
river_lbl = '$[m^3~s^{-1}]$'
river_min = 1e-1
river_max = 1e5
river_nrm = matplotlib.colors.LogNorm(vmin=river_min, vmax=river_max)

# Lake settings
lake_col = (8/255,81/255,156/255) # blue
lake_min = 100 # km^2

# Lake selection
lake_plt = lakes.loc[lakes['Lake_area'] > lake_min]


# #### Figure
fig, ax = plt.subplots(1, 1, figsize=[120, 90])
plt.rcParams.update({'font.size': 60})

shp.plot(ax=ax, column=stats_varId, 
         linewidth=linewidth,
         cmap=river_col, vmin=river_min, vmax=river_max, norm=river_nrm,
         legend=True, legend_kwds={'label': river_lbl, 'extend': 'both', 'shrink':0.25, 'pad': 0.0},
         zorder=0)
lake_plt.plot(ax=ax, color=lake_col, zorder=1)
continents.boundary.plot(ax=ax, color='k', zorder=2)

ax.set_title(river_ttl)
ax.axis('off')
plt.savefig(fig_path/fig_name, dpi=100, facecolor='w', bbox_inches='tight')

