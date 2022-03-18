''' functions related to mizuroute
'''

import pandas as pd
import netCDF4 as nc4
import geopandas as gpd
import numpy as np
from datetime import datetime
import os, sys
import easymore.easymore as esmr
import itertools


# Function to create new nc variables
def create_and_fill_nc_var(ncid, var_name, var_type, dim, fill_val, fill_data, long_name, units):
    """add a variable var_name to nc4 object ncid

    :param ncid: nc object to add variable to
    :type ncid: nc4.Dataset
    :param var_name: variable name 
    :type var_name: str
    :param var_type: type of variable
    :type var_type: str
    :param dim: dimension of variable
    :type dim: str
    :param fill_val: True or False
    :type fill_val: bool
    :param fill_data: data of the variable
    :type fill_data: as :param:var_type
    :param long_name: long name
    :type long_name: str
    :param units: units
    :type units: str
    """    
    # Make the variable
    ncvar = ncid.createVariable(var_name, var_type, (dim,), fill_val)
    # Add the data
    ncvar[:] = fill_data
    # Add meta data
    ncvar.long_name = long_name
    ncvar.unit = units
    return

def enforce_outlets_from_control(shp_river, river_outlet_ids, river_seg_id, river_down_seg_id):
    """Set basin ids specified as outlet to mizuroute outlet

    Ensure that any segments specified in the control file are identified to
    mizuRoute as outlets, by setting the downstream segment to 0
    This indicates to mizuRoute that this segment has no downstream segment attached to it;
    i.e. is an outlet

    :param shp_river: river shapefile
    :type shp_river: file path .shp
    :param river_outlet_ids: river_seg_ids that need to be set as outlet, comma seperated for multiple
    :type river_outlet_ids: str
    :param river_seg_id: Name of the segment ID column
    :type river_seg_id: str
    :param river_down_seg_id: Name of the downstream segment ID column
    :type river_down_seg_id: str
    """    
    # Set flag and convert variable type if needed
    if 'n/a' in river_outlet_ids:
        enforce_outlets = False
    else:
        enforce_outlets = True
        river_outlet_ids = river_outlet_ids.split(',') # does nothing if string contains no comma
        river_outlet_ids = [int(outlet_id) for outlet_id in river_outlet_ids]

    if enforce_outlets:
        for outlet_id in river_outlet_ids:
            if any(shp_river[river_seg_id] == outlet_id):
                shp_river.loc[shp_river[river_seg_id] == outlet_id, river_down_seg_id] = 0
            else:
                print('outlet_id {} not found in {}'.format(outlet_id,river_seg_id))

def enforce_outlets_by_max_upstream_area(shp_river, river_uparea, river_seg_id, river_down_seg_id):
    """Set mizuroute outlet based on maximum upstream area

    Ensure that any segments specified in the control file are identified to
    mizuRoute as outlets, by setting the downstream segment to 0
    This indicates to mizuRoute that this segment has no downstream segment attached to it;
    i.e. is an outlet

    :param shp_river: river shapefile
    :type shp_river: file path .shp
    :param river_uparea: Name of the upstream area column
    :type river_uparea: str
    :param river_seg_id: Name of the segment ID column
    :type river_seg_id: str
    :param river_down_seg_id: Name of the downstream segment ID column
    :type river_down_seg_id: str
    """    
    river_outlet_id = shp_river[river_seg_id].loc[shp_river[river_uparea].argmax()]
    shp_river.loc[shp_river[river_seg_id] == river_outlet_id, river_down_seg_id] = 0



def generate_mizuroute_topology(infile_river_shp, infile_basin_shp, outfile_topology_nc, river_outlet_ids,
    basin_hru_id = 'COMID', basin_hru_to_seg = 'hru_to_seg', basin_hru_area = 'area', 
    river_seg_id = 'COMID', river_down_seg_id = 'NextDownID', river_slope = 'slope', 
    river_length = 'length' , fake_river=False):
    """generate mizuroute topology .nc file

    The network topology contains information about the stream network and the routing basins the network is in. These include:

    1. Unique indices of the stream segment;
    2. Unique indices of the routing basins (HRUs; equivalent to SUMMA GRUs in this setup);
    3. ID of the stream segment each individual segment connects to (should be 0 or negative number to indicate that segment is an outlet);
    4. ID of the stream segment a basin drains into;
    5. Basin area;
    6. Segment slope;
    7. Segment length.

    Values for these settings are taken from the user's shapefiles. See: https://mizuroute.readthedocs.io/en/master/Input_data.html

    :param infile_river_shp: path to river shapefile
    :type infile_river_shp: file path .shp
    :param infile_basin_shp: path to basin shapefile
    :type infile_basin_shp: file path .shp
    :param outfile_topology_nc: path to save output netCDF file
    :type outfile_topology_nc: file path .nc
    :param river_outlet_ids: river_seg_ids that need to be set as outlet, comma seperated for multiple
    :type river_outlet_ids: str
    :param basin_hru_id: name of the routing basin id column in :param:infile_basin_shp , defaults to 'COMID'
    :type basin_hru_id: str, optional
    :param basin_hru_to_seg: name of the column that shows which river segment each HRU connects to, defaults to 'hru_to_seg'
    :type basin_hru_to_seg: str, optional
    :param basin_hru_area: Name of the catchment area column. Area must be in units [m^2], defaults to 'area'
    :type basin_hru_area: str, optional
    :param river_seg_id: Name of the segment ID column in :param:infile_river_shp, defaults to 'COMID'
    :type river_seg_id: str, optional
    :param river_down_seg_id: Name of the downstream segment ID column, defaults to 'NextDownID'
    :type river_down_seg_id: str, optional
    :param river_slope: Name of the slope column. Slope must be in in units [length/length]., defaults to 'slope'
    :type river_slope: str, optional
    :param river_length: Name of the segment length column. Length must be in units [m], defaults to 'length'
    :type river_length: str, optional
    :param fake_river: Flag to attempt creating fake river network for headwater basins , defaults to False
    :type fake_river: bool, optional
    """    
    
    shp_basin = gpd.read_file(infile_basin_shp)
    if os.path.isfile(infile_river_shp):
        # Open the shapefile
        shp_river = gpd.read_file(infile_river_shp)

        # Ensure that the most downstream segment in the river network has a downstream_ID of 0
        # This indicates to mizuRoute that this segment has no downstream segment attached to it
        enforce_outlets_from_control(shp_river, river_outlet_ids, river_seg_id, river_down_seg_id)
        # Make the netcdf file
        with nc4.Dataset(outfile_topology_nc, 'w', format='NETCDF4') as ncid:
            # Set general attributes
            now = datetime.now()
            ncid.setncattr('Author', "Created by SUMMA workflow scripts")
            ncid.setncattr('History', 'Created ' + now.strftime('%Y/%m/%d %H:%M:%S'))
            ncid.setncattr('Purpose', 'Create a river network .nc file for mizuRoute routing')
            # Define the seg and hru dimensions
            num_seg = len(shp_river)
            num_hru = len(shp_basin)
            ncid.createDimension('seg', num_seg)
            ncid.createDimension('hru', num_hru)
            # --- Variables
            create_and_fill_nc_var(ncid, 'segId', 'int', 'seg', False, shp_river[river_seg_id].values.astype(int), 'Unique ID of each stream segment', '-')
            create_and_fill_nc_var(ncid, 'downSegId', 'int', 'seg', False, shp_river[river_down_seg_id].values.astype(int), 'ID of the downstream segment', '-')
            create_and_fill_nc_var(ncid, 'slope', 'f8', 'seg', False, shp_river[river_slope].values.astype(float), 'Segment slope', '-')
            create_and_fill_nc_var(ncid, 'length', 'f8', 'seg', False, shp_river[river_length].values.astype(float), 'Segment length', 'm')
            create_and_fill_nc_var(ncid, 'hruId', 'int', 'hru', False, shp_basin[basin_hru_id].values.astype(int), 'Unique hru ID', '-')
            create_and_fill_nc_var(ncid, 'hruToSegId', 'int', 'hru', False, shp_basin[basin_hru_to_seg].values.astype(int), 'ID of the stream segment to which the HRU discharges', '-')
            create_and_fill_nc_var(ncid, 'area', 'f8', 'hru', False, shp_basin[basin_hru_area].values.astype(float), 'HRU area', 'm^2')
    elif fake_river == True:
        print('river network shapefile does not exist. generate a fake river network.')
        if len(shp_basin) > 1:
            sys.exit('len(shp_basin)>1, indicating this is not a headwater basin! please check!')
        with nc4.Dataset(outfile_topology_nc, 'w', format='NETCDF4') as ncid:
            # Set general attributes
            now = datetime.now()
            ncid.setncattr('Author', "Created by SUMMA workflow scripts")
            ncid.setncattr('History', 'Created ' + now.strftime('%Y/%m/%d %H:%M:%S'))
            ncid.setncattr('Purpose', 'Create a river network .nc file for mizuRoute routing')
            # Define the seg and hru dimensions
            num_seg = len(shp_basin)
            num_hru = len(shp_basin)
            ncid.createDimension('seg', num_seg)
            ncid.createDimension('hru', num_hru)
            # --- Variables
            create_and_fill_nc_var(ncid, 'segId', 'int', 'seg', False, shp_basin[basin_hru_id].values.astype(int), 'Unique ID of each stream segment', '-')
            create_and_fill_nc_var(ncid, 'downSegId', 'int', 'seg', False, np.zeros(num_seg), 'ID of the downstream segment', '-')
            create_and_fill_nc_var(ncid, 'slope', 'f8', 'seg', False, np.ones(num_seg)*1e-5, 'Segment slope', '-')
            create_and_fill_nc_var(ncid, 'length', 'f8', 'seg', False, np.ones(num_seg)*1, 'Segment length', 'm')
            create_and_fill_nc_var(ncid, 'hruId', 'int', 'hru', False, shp_basin[basin_hru_id].values.astype(int), 'Unique hru ID', '-')
            create_and_fill_nc_var(ncid, 'hruToSegId', 'int', 'hru', False, shp_basin[basin_hru_to_seg].values.astype(int), 'ID of the stream segment to which the HRU discharges', '-')
            create_and_fill_nc_var(ncid, 'area', 'f8', 'hru', False, shp_basin[basin_hru_area].values.astype(float), 'HRU area', 'm^2')

def generate_mizuroute_remap(infile_gruhru_shp, infile_basin_shp, outfile_routingremap_nc,
    rm_shp_hru_id = 'COMID', hm_shp_gru_id = 'GRU_ID', remap_flag = True):
    """Remaps SUMMA GRU to mizuRoute GRU

    Note that this file is **_only_** needed if the defined SUMMA GRUs **_do not_** map 1:1 onto the routing basins as defined for mizuRoute. It is typically easiest to ensure this direct mapping. In cases where the routing basins are different from the GRUs used by SUMMA, this script generates the required mizuRoute input file to do so.

    The optional remap file contains information about how the model elements of the Hydrologic Model (HM; i.e. SUMMA in this setup) map onto the routing basins used by the Routing Model (RM; i.e. mizuRoute). This information includes:
    1. Unique RM HRU IDs of the routing basins;
    2. Unique HM HRU IDs of the modeled basins (note that in this case what mizuRoute calls a "HM HRU" is equivalent to what SUMMA calls a GRU);
    3. The number of HM HRUs each RM HRU is overlapped by;
    4. The weights (relative area) each HM HRU contributes to each RM HRU.

    IDs are taken from the user's shapefiles whereas overlap and weight are calculated based on an intersection of both shapefiles. See: https://mizuroute.readthedocs.io/en/master/Input_data.html

    :param infile_gruhru_shp: _description_
    :type infile_gruhru_shp: _type_
    :param infile_basin_shp: path to basin shapefile
    :type infile_basin_shp: file path .shp
    :param outfile_routingremap_nc: _description_
    :type outfile_routingremap_nc: _type_
    :param rm_shp_hru_id: _description_, defaults to 'COMID'
    :type rm_shp_hru_id: str, optional
    :param hm_shp_gru_id: _description_, defaults to 'GRU_ID'
    :type hm_shp_gru_id: str, optional
    :param hm_shp_gru_id: flag to determine if remapping needs to be run, defaults to 'yes'
    :type hm_shp_gru_id: str, optional
    """
    # only continue if the remap_flag is 'yes'
    # the flag is 'yes' (str) for backwards compatability    
    if remap_flag.lower() != 'yes':
        print('Active control file indicates remapping is not needed. Aborting.')
        return

    # Load both shapefiles
    hm_shape = gpd.read_file(infile_gruhru_shp)
    rm_shape = gpd.read_file(infile_basin_shp)
    
    # Create an EASYMORE object
    esmr_caller = esmr()

    # Project both shapes to equal area
    hm_shape = hm_shape.to_crs('EPSG:6933')
    rm_shape = rm_shape.to_crs('EPSG:6933')

    # Run the intersection
    intersected_shape = esmr.intersection_shp(esmr_caller, rm_shape, hm_shape)

    # Reproject the intersection to WSG84
    intersected_shape = intersected_shape.to_crs('EPSG:4326')

    # Save the intersection to file
    # intersected_shape.to_file(outfile_gru_intersect_basin_shp)

    # --- Pre-process the variables
    # Define a few shorthand variables
    int_rm_id = 'S_1_' + rm_shp_hru_id
    int_hm_id = 'S_2_' + hm_shp_gru_id
    int_weight = 'AP1N'

    # Sort the intersected shape by RM ID first, and HM ID second. This means all info per RM ID is in consecutive rows
    intersected_shape = intersected_shape.sort_values(by=[int_rm_id, int_hm_id])

    # Routing Network HRU ID
    nc_rnhruid = intersected_shape.groupby(int_rm_id).agg({int_rm_id: pd.unique}).values.astype(int)

    # Number of Hydrologic Model elements (GRUs in SUMMA's case) per Routing Network catchment
    nc_noverlaps = intersected_shape.groupby(int_rm_id).agg({int_hm_id: 'count'}).values.astype(int)

    # Hydrologic Model GRU IDs that are associated with each part of the overlap
    multi_nested_list = intersected_shape.groupby(int_rm_id).agg({int_hm_id: list}).values.tolist()  # Get the data
    nc_hmgruid = list(
        itertools.chain.from_iterable(itertools.chain.from_iterable(multi_nested_list)))  # Combine 3 nested list into 1

    # Areal weight of each HM GRU per part of the overlaps
    multi_nested_list = intersected_shape.groupby(int_rm_id).agg({int_weight: list}).values.tolist()
    nc_weight = list(itertools.chain.from_iterable(itertools.chain.from_iterable(multi_nested_list)))

    # --- Make the `.nc` file
    # Find the dimension sizes
    num_hru = len(rm_shape)
    num_data = len(intersected_shape)

    # Make the netcdf file
    with nc4.Dataset(outfile_routingremap_nc, 'w', format='NETCDF4') as ncid:
        # Set general attributes
        now = datetime.now()
        ncid.setncattr('Author', "Created by SUMMA workflow scripts")
        ncid.setncattr('History', 'Created ' + now.strftime('%Y/%m/%d %H:%M:%S'))
        ncid.setncattr('Purpose', 'Create a remapping .nc file for mizuRoute routing')
        # Define the seg and hru dimensions
        ncid.createDimension('hru', num_hru)
        ncid.createDimension('data', num_data)
        # --- Variables
        create_and_fill_nc_var(ncid, 'RN_hruId', 'int', 'hru', False, nc_rnhruid, 'River network HRU ID', '-')
        create_and_fill_nc_var(ncid, 'nOverlaps', 'int', 'hru', False, nc_noverlaps, 'Number of overlapping HM_HRUs for each RN_HRU', '-')
        create_and_fill_nc_var(ncid, 'HM_hruId', 'int', 'data', False, nc_hmgruid, 'ID of overlapping HM_HRUs. Note that SUMMA calls these GRUs', '-')
        create_and_fill_nc_var(ncid, 'weight', 'f8', 'data', False, nc_weight, 'Areal weight of overlapping HM_HRUs. Note that SUMMA calls these GRUs', '-')
