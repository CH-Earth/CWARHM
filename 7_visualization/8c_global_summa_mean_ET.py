#!/usr/bin/env python
# coding: utf-8

# # Global SUMMA evapotranspiration
# Plots mean January evapotranspiration per basin. Needs:
# - Catchment shapefiles
# - SUMMA output `scalarTotalET`

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
stats_varId = 'scalarTotalET'

# Define where to save the figure
fig_path = Path('/gpfs/tp/gwf/gwf_cmt/wknoben/CWARHM_data/domain_global/visualization')
fig_name = 'mean_january_1979_evap_FOR_global_v11.jpg'

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
shp[stats_varId] = sims[stats_varId].values * -1 # flip the sign so that evap has a positive value

# Sort the river shapefile so that rivers are sorted from small to large flows
shp = shp.sort_values(by=stats_varId)


# #### Prepare plotting settings
# Basin settings
et_ttl = '(a) Mean simulated total evapotranspiration'
et_lbl = '[kg m-2 s-1]'

# Make a global ET colormap
#colors_low = plt.cm.YlGnBu_r(np.linspace(0,1,256))
#colors_high = plt.cm.YlOrRd(np.linspace(0,1,256))
#all_colors = np.vstack((colors_low, colors_high))
#et_col = matplotlib.colors.LinearSegmentedColormap.from_list('global_et',all_colors)
et_col = 'Spectral_r'
et_min = 0
et_ctr = 1e-5
et_max = 1.5e-4
et_nrm = matplotlib.colors.TwoSlopeNorm(vmin=et_min, vcenter=et_ctr, vmax=et_max)

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
         cmap=et_col, vmin=et_min, vmax=et_max, norm=et_nrm,
         legend=True, legend_kwds={'label': et_lbl, 'extend': 'both', 'shrink':0.25, 'pad': 0},
         zorder=-1)
lake_plt.plot(ax=ax, color=lake_col, zorder=1)
continents.boundary.plot(ax=ax, color='k', zorder=2)

ax.set_title(et_ttl)
ax.axis('off')
plt.savefig(fig_path/fig_name, dpi=100, facecolor='w', bbox_inches='tight')


