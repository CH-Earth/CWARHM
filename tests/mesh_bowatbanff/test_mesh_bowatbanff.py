import os
import shutil
import sys


#%%
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from pathlib import Path
import xarray as xr
import geopandas as gpd

from cwarhm.model_specific_processing import mesh as mesh
from cwarhm.model_agnostic_processing import HRU as HRU
import cwarhm.util.util as utl

# set paths
# results_folder_path: path to save the results
# test_data_path: path with the input test data
os.chdir(os.path.dirname(os.path.realpath(__file__)))
results_folder_path = Path("/Users/ayx374/Documents/project/chwarm_test_results/domain_BowAtBanff_mesh")

# read control file
control_options = utl.read_summa_workflow_control_file('control_Bow_at_Banff_test.txt')


#%%
# create mesh topology
mesh.generate_mesh_topology(control_options['river_network_shp_path'], 
    control_options['river_basin_shp_path'],
    os.path.join(control_options['settings_routing_path'],control_options['settings_routing_topology']),
    control_options['settings_make_outlet'])
ranks, drain_db = mesh.reindex_topology_file(os.path.join(control_options['settings_routing_path'],control_options['settings_routing_topology']))
drain_db.to_netcdf(os.path.join(control_options['settings_routing_path'],control_options['settings_routing_topology']))

# calculate land use fractions for MESH GRUS from CWARHM-SUMMA GRU/HRU land use counts
gdf_land_use_counts = gpd.read_file(os.path.join(
                        control_options['intersect_land_path'],control_options['intersect_land_name']))
df_gru_land_use_fractions = HRU.gru_fraction_from_hru_counts(gdf_land_use_counts)

# set names for discretization
fraction_type = ['Evergreen Needleleaf Forests','Woody Savannas','Savannas',
'Grasslands', 'Permanent Wetlands', 'Urban and Built-up Lands', 'Permanent Snow and Ice',
'Barren','Water Bodies']
# and add fractions and Grouped Response Unit info to the drainage_db
drain_db = mesh.add_gru_fractions_to_drainage_db(drain_db, df_gru_land_use_fractions, fraction_type)
drain_db.to_netcdf(os.path.join(control_options['settings_routing_path'],control_options['settings_routing_topology']))

# remap forcing data from grids, to MESH GRUs (CWARHM-SUMMA maps to SUMMA HRUs)
HRU.map_forcing_data(control_options['river_basin_shp_path'],
                    control_options['forcing_merged_path']+'/*200803.nc',
                    control_options['forcing_basin_avg_path']+'/',
                    var_names = ['LWRadAtm', 'SWRadAtm', 'pptrate', 'airpres', 'airtemp', 'spechum', 'windspd'],
                    var_lon='longitude', var_lat='latitude',
                    case_name = control_options['domain_name'] , 
                    temp_dir=control_options['intersect_forcing_path']+'/' ,
                    esmr_kwargs={
                        'var_names_remapped':['FI', 'FB', 'PR', 'P0', 'TT', 'HU', 'UV']
                    }
                    )