#!/usr/bin/env python
# coding: utf-8

# # Global SUMMA runoff
# Plots mean January runoff per basin. Needs:
# - Catchment shapefiles
# - SUMMA output `scalarTotalRunoff`

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
basin_path  = Path('/gpfs/tp/gwf/gwf_cmt/wknoben/CWARHM_data/domain_global/shapefiles/robinson')
basin_name  = 'basins_{}_robinson.shp'
basin_basId = 'GRU_ID' 

# Define the lakes shapefile 
lakes_path = Path('/gpfs/tp/gwf/gwf_cmt/wknoben/CWARHM_data/domain_global/shapefiles/robinson')
lakes_name = 'HydroLAKES_polys_v10_robinson.shp'

# Define the continent outline shapefile
continents_path = Path('/gpfs/tp/gwf/gwf_cmt/wknoben/CWARHM_data/domain_global/shapefiles/robinson')
continents_name = 'World_region_Robinson.shp'

# Define the simulation results
stats_path = Path('/gpfs/tp/gwf/gwf_cmt/wknoben/CWARHM_data/domain_global/simulation_stats')
stats_name = 'SUMMA_stat_197901_{}.nc'
stats_basId = 'gruId'
stats_varId = 'scalarTotalRunoff'

# Define where to save the figure
fig_path = Path('/gpfs/tp/gwf/gwf_cmt/wknoben/CWARHM_data/domain_global/visualization')
fig_name = 'mean_january_1979_runoff_FOR_global_v12.png'

# Make the folder if it doesn't exist
fig_path.mkdir(parents=True, exist_ok=True)


# #### Load shapefiles and data
shp_list = []
for domain in domains:
    shp_list.append(gpd.read_file(basin_path/basin_name.format(domain)))
shp = pd.concat(shp_list)

lakes = gpd.read_file(lakes_path / lakes_name)
continents = gpd.read_file(continents_path/continents_name)

# Merge the North AMerica 'COMID's with the 'GRU_ID's the other shapes use
shp[basin_basId].fillna(shp['COMID'], inplace=True)

sims = xr.Dataset()
for domain in domains:
    sim = xr.open_dataset(stats_path/stats_name.format(domain))
    sim = sim.assign_coords(hru=sim[stats_basId].values) # Vars have an 'hru' dim, which has values 1..n. Set to gruIDs instead
    sim = sim.isel(time=0).drop_vars(['time','time_bnds','hruId','gruId']) # Keep only rlevant info (vars, basin IDs)
    if 'gru' in sim.dims:
        sim = sim.drop_dims('gru')
    sims = xr.merge([sims,sim])


# #### Add simulation values to the shape
# Polygon order in the simulation file
seg_ids_sim = sims['hru'].values.astype('int')

# Ensure that the shapefile is in the same order as the sims
shp = shp.set_index(shp[basin_basId].astype('int')) # set the index
shp = shp.reindex(seg_ids_sim) # reindex to be in same order as sims file

# Add the simulations to the shape
shp[stats_varId] = sims[stats_varId].values

# Sort the river shapefile so that rivers are sorted from small to large flows
shp = shp.sort_values(by=stats_varId)

# #### Prepare plotting settings
# Basin settings
q_ttl = '(b) Mean simulated total runoff'
q_lbl = '$[m~s^{-1}]$'
q_col = 'Blues'
q_min = 1e-9
q_max = 1e-7
q_nrm = matplotlib.colors.LogNorm(vmin=q_min, vmax=q_max)

# Lake settings
lake_col = (8/255,81/255,156/255) # blue
lake_min = 100 # km^2

# Lake selection
lake_plt = lakes.loc[lakes['Lake_area'] > lake_min]

# #### Figure
fig, ax = plt.subplots(1, 1, figsize=[120, 90])
plt.rcParams.update({'font.size': 60})
plt.rcParams['patch.antialiased'] = False # Prevents an issue with plotting distortion along the 0 degree latitude and longitude lines

shp.plot(ax=ax, column=stats_varId, 
         cmap=q_col, vmin=q_min, vmax=q_max, norm=q_nrm,
         legend=True, legend_kwds={'label': q_lbl, 'extend': 'both', 'shrink':0.25, 'pad': 0.0},
         zorder=0)
lake_plt.plot(ax=ax, color=lake_col, zorder=1)
continents.boundary.plot(ax=ax, color='k', zorder=2)

ax.set_title(q_ttl)
ax.axis('off')
plt.savefig(fig_path/fig_name, dpi=100, facecolor='w', bbox_inches='tight')
