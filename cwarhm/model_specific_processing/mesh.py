'''functions to write MESH specific input files'''

import cwarhm.model_specific_processing.mizuroute as mizu
import pandas as pd
import netCDF4 as nc4
import geopandas as gpd
import xarray as xr
import numpy as np
from datetime import datetime
from datetime import date
import warnings
import ntpath


def generate_mesh_topology(infile_river_shp, infile_basin_shp, outfile_topology_nc, river_outlet_ids,
    basin_hru_id = 'COMID', basin_hru_to_seg = 'hru_to_seg', basin_hru_area = 'area', 
    river_seg_id = 'COMID', river_down_seg_id = 'NextDownID', river_slope = 'slope', 
    river_length = 'length' , fake_river=False):
    """generate mesh topology .nc file

    This function is based on :py:func:mizuroute:generate_mizuroute_topology
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
    shp_river = gpd.read_file(infile_river_shp)

    # Added by MESH workflow
    # sort basin to be consistent with river
    shp_basin = shp_basin.sort_values(by=basin_hru_id)
    
    # convert area to m^2
    # Note: if area unit is already based on m**2, it is not requried to covert m**2
    # shp_basin[basin_hru_area].values[:] = shp_basin[basin_hru_area].values[:]*10**6
    
    # covert river_length to m
    # Note: if length unit is already based on m, it is not requried to covert m
    # shp_river[river_length].values[:]   = shp_river[river_length].values[:]*1000
    
    # adding centroid of each subbasin.
    # Note: the more accurate should be done in equal area projection
    warnings.simplefilter('ignore') # silent the warning
    shp_basin['lon'] = shp_basin.centroid.x
    shp_basin['lat'] = shp_basin.centroid.y
    warnings.simplefilter('default') # back to normal
    
    # specifying other variables
    # Note: the river width and manning is optional. The manning coefficient is specified in the MESH
    # hydrology configuration file 
    shp_river['width']   = 50
    shp_river['manning'] = 0.03

    #%% Find the number of segments and subbasins
    num_seg = len(shp_river)
    num_hru = len(shp_basin)
 
    # finished edit by MESH workflow

    # Ensure that the most downstream segment in the river network has a downstream_ID of 0
    # This indicates to mizuRoute that this segment has no downstream segment attached to it
    mizu.enforce_outlets_from_control(shp_river, river_outlet_ids, river_seg_id, river_down_seg_id)
    # Make the netcdf file
    with nc4.Dataset(outfile_topology_nc, 'w', format='NETCDF4') as ncid:
        # Set general attributes
        now = datetime.now()
        ncid.setncattr('Author', "Created by MESH vector-based workflow scripts")
        ncid.setncattr('History','Created ' + now.strftime('%Y/%m/%d %H:%M:%S'))
        ncid.setncattr('Purpose','Create a river network .nc file for WATROUTE routing')
        # Define the seg and hru dimensions
        # it can be renamed to 'subbasin'
        # Added by MESH workflow
        ncid.createDimension('n', num_seg)
        # ncid.createDimension('hru', num_hru)
        # finished edit by MESH workflow

        # --- Variables
        mizu.create_and_fill_nc_var(ncid, 'segId', 'int', 'n', False, shp_river[river_seg_id].values.astype(int), 'Unique ID of each stream segment', '-')
        mizu.create_and_fill_nc_var(ncid, 'downSegId', 'int', 'n', False, shp_river[river_down_seg_id].values.astype(int), 'ID of the downstream segment', '-')
        mizu.create_and_fill_nc_var(ncid, 'slope', 'f8', 'n', False, shp_river[river_slope].values.astype(float), 'Segment slope', '-')
        # added by MESH workflow
        mizu.create_and_fill_nc_var(ncid, 'lon', 'f8', 'n', False, \
                            shp_basin['lon'].values.astype(float), \
                            'longitude', '-')     
        mizu.create_and_fill_nc_var(ncid, 'lat', 'f8', 'n', False, \
                            shp_basin['lat'].values.astype(float), \
                            'latitude', '-')
        # finished edit by MESH workflow 
        mizu.create_and_fill_nc_var(ncid, 'length', 'f8', 'n', False, shp_river[river_length].values.astype(float), 'Segment length', 'm')
        mizu.create_and_fill_nc_var(ncid, 'hruId', 'int', 'n', False, shp_basin[basin_hru_id].values.astype(int), 'Unique hru ID', '-')
        mizu.create_and_fill_nc_var(ncid, 'hruToSegId', 'int', 'n', False, shp_basin[basin_hru_to_seg].values.astype(int), 'ID of the stream segment to which the HRU discharges', '-')
        mizu.create_and_fill_nc_var(ncid, 'area', 'f8', 'n', False, shp_basin[basin_hru_area].values.astype(float), 'HRU area', 'm^2')
            # added by MESH workflow
        mizu.create_and_fill_nc_var(ncid, 'width', 'f8', 'n', False, \
                            shp_river['width'].values.astype(float), \
                            'width', 'm')                      
        mizu.create_and_fill_nc_var(ncid, 'manning', 'f8', 'n', False, \
                            shp_river['manning'].values.astype(float), \
                            'manning', '-')  
        # finished edit by MESH workflow

#%% Function reindex to extract drainage database variables
def reindex_topology_file(in_ddb: str):
    """reindex topology file to match MESH requirements

    MESH requires stream segment IDs to be ordered from highest to lowest 
    segment by receiving order, from 1 to the total number of segments in 
    the domain (NA). This information is passed to MESH from the 
    "drainage database" (or basin information file), where the IDs 
    of stream segments are defined in the "Rank" variable, and the 
    receiving order is defined in the "Next" variable, which contains 
    the ID of the segment that the current stream segment flows in to.

    :param in_ddb: topology netcdf file as created by :func:generate_mesh_topology
    :type in_ddb: str (file path)
    :return: the new ranks
    :rtype: list
    :return: topology xarray dataset extended with the new ranks
    :rtype: xarray dataset
    """    
    #% reading the input DDB
    drainage_db = xr.open_dataset(in_ddb)
    drainage_db.close()
        
    # Count the number of outlets
    outlets = np.where(drainage_db['downSegId'].values == 0)[0]
        
    # %  Re-indexing seg_id and tosegment
    # Get the segment ID associated with the outlet.
    first_index = drainage_db['segId'].values[outlets[0]]
        
    # Create a copy of the 'downSegId' field.
    old_next = drainage_db['downSegId'].values.copy()
        
    ## Set the current 'Next' and 'Rank' values.
    # total number of values
    current_next = len(drainage_db['segId'])
    # total number of values less number of outlets
    current_rank = current_next - len(outlets)
        
    ## Create dummy arrays for new values.
    # size of 'segId''
    new_next = [0]*len(drainage_db['segId'])
    # empty list (to push values to)
    next_rank = []
    # list to append positions of new 'rank', first element is position of outlet
    new_rank = [outlets[0]]
        
    # % Reorder seg_id and tosegment
    while (first_index != -1):
        for i in range(len(old_next)):
            if (old_next[i] == first_index):
                # save rank of current 'next'
                next_rank.append(drainage_db['segId'].values[i])
                # assign next using new ranking
                new_next[i] = current_next
                # save the current position corresponding to the new 'rank'
                new_rank.append(i)
                current_rank -= 1
                # override input value to mark as completed
                old_next[i] = 0
                break
        if (len(next_rank) == 0):
                # no more IDs to process
                first_index = -1
        elif (not np.any(old_next == first_index)):
            # take next rank by 'next' order
            first_index = next_rank[0]
            # drop that element from the list
            del next_rank[0]
            # deincrement the 'next' rank
            current_next -= 1

    new_rank = np.flip(new_rank)
        
    # % reordering
    for m in ['area', 'length', 'slope', 'lon', 'lat', 'hruId',
                'segId', 'hruToSegId', 'downSegId', 'width', 'manning']:
        drainage_db[m].values = drainage_db[m].values[new_rank]

    # Reorder the new 'Next'.
    new_next = np.array(new_next)[new_rank]
        
    # % check if channel slope values match the minimum threshold
    min_slope = 0.000001
    drainage_db['slope'].values[drainage_db['slope'].values < min_slope] = min_slope
        
    # % Adding the updated Rank and Next variables to the file
    drainage_db['Rank'] = (['n'], np.array(range(1, len(new_rank) + 1),
                            dtype = 'int32')) # ordered list from 1:NA
    drainage_db['Rank'].attrs.update(standard_name = 'Rank',
                        long_name = 'Element ID', units = '1', _FillValue = -1)
        
    drainage_db['Next'] = (['n'], new_next.astype('int32')) # reordered 'new_next'
    drainage_db['Next'].attrs.update(standard_name = 'Next',
                        long_name = 'Receiving ID', units = '1', _FillValue = -1)

    # % Adding missing attributes and renaming variables
    # Add 'axis' and missing attributes for the 'lat' variable.
    drainage_db['lat'].attrs['standard_name'] = 'latitude'
    drainage_db['lat'].attrs['units'] = 'degrees_north'
    drainage_db['lat'].attrs['axis'] = 'Y'
        
    # Add 'axis' and missing attributes for the 'lon' variable.
    drainage_db['lon'].attrs['standard_name'] = 'longitude'
    drainage_db['lon'].attrs['units'] = 'degrees_east'
    drainage_db['lon'].attrs['axis'] = 'X'
        
    # Add or overwrite 'grid_mapping' for each variable (except axes).
    for v in drainage_db.variables:
        if (drainage_db[v].attrs.get('axis') is None):
            drainage_db[v].attrs['grid_mapping'] = 'crs'
        
    # Add the 'crs' itself (if none found).
    if (drainage_db.variables.get('crs') is None):
        drainage_db['crs'] = ([], np.int32(1))
        drainage_db['crs'].attrs.update(grid_mapping_name = 'latitude_longitude', longitude_of_prime_meridian = 0.0, semi_major_axis = 6378137.0, inverse_flattening = 298.257223563)
        
    # Rename variables.
    for old, new in zip(['area', 'length', 'slope', 'manning'], ['GridArea', 'ChnlLength', 'ChnlSlope', 'R2N']):
        drainage_db = drainage_db.rename({old: new})
        
    # Rename the 'subbasin' dimension (from 'n').
    drainage_db = drainage_db.rename({'n': 'subbasin'})
        
    # % Specifying the NetCDF "featureType"
    # Add a 'time' axis with static values set to today (in this case, time is not actually treated as a dimension).
    drainage_db['time'] = (['subbasin'], np.zeros(len(new_rank)))
    drainage_db['time'].attrs.update(standard_name = 'time', units = ('days since %s 00:00:00' % date.today().strftime('%Y-%m-%d')), axis = 'T')
        
    # Set the 'coords' of the dataset to the new axes.
    drainage_db = drainage_db.set_coords(['time', 'lon', 'lat'])
        
    # Add (or overwrite) the 'featureType' to identify the 'point' dataset.
    drainage_db.attrs['featureType'] = 'point'
        
    return new_rank, drainage_db

def add_gru_fractions_to_drainage_db(drainage_db, gru_fractions, fraction_type: list):
    """add gru fraction variable and gru dimension to drainage db

    drainage database is generated using :func:generate_mesh_topology
    followed by :func:reindex_topology_file

    :param drainage_db: MESH drainage database as from :func:generate_mesh_topology
    :type drainage_db: xarray.core.dataset.Dataset
    :param gru_fractions: _description_
    :type gru_fractions: pandas.core.frame.DataFrame
    :param fraction_type: list of the names of the classes used in discretization
    :type fraction_type: list
    :return: MESH drainage database with GRU information
    :rtype: xarray.core.dataset.Dataset
    """    
    hru_id = list(drainage_db.hruId.values)
    # number of classes
    n_classes = len(gru_fractions.columns)
    n_grus = len(hru_id)
    # set array
    frac_array = np.empty((n_grus,n_classes))
    for i,id in enumerate(hru_id):
        frac_array[i,:] = gru_fractions.loc[str(id),:]

    drainage_db["GRU"] = (["subbasin", "gru"], frac_array)
    drainage_db['GRU'].attrs['standard_name'] = 'GRU'
    drainage_db['GRU'].attrs['long_name'] = 'Group Response Unit'
    drainage_db['GRU'].attrs['units'] = '-'
    drainage_db['GRU'].attrs['_FillValue'] = -1

    drainage_db["LandUse"] = (["gru"], fraction_type)

    return drainage_db  

def reindex_forcing_file(input_forcing, drainage_db, input_basin):
    """reindex forcing file according to rank in mesh drainage database

    In the final postprocessing part of the forcing dataset, it is required to 
    reorder the forcing variables based on the remapped "Rank" IDs from the basin 
    information file "drainage_database". Because EASYMORE remaps the forcing 
    variables based on the MERIT Hydro catchment IDs (COMID), the order of 
    forcing variables may not match the order of the "Rank" variable. 
    Therefore, the fields in the remapped forcing files must be remapped to be 
    compatible with the "drainage_database" file used for MESH. 
    Three input data files are required for this process, the "drainage_databse", 
    remapped forcing files, and the MERIT Hydro catchment shapefile used in the 
    previous steps. The following section code block executes the reordering 
    operation.

    :param input_forcing: basin averaged forcing generated with EASYMORE
    :type input_forcing: xarray.Dataset
    :param drainage_db: mesh drainage database
    :type drainage_db: xarray.Dataset
    :param input_basin: shapefile with the catchment IDs (COMID)
    :type input_basin: geopandas.GeoDataframe
    :return: reordered forcing file for MESH
    :rtype: xarray.Dataset
    """       

    # set lon and lat as coordinates, not variables
    input_forcing = input_forcing.set_coords(['latitude','longitude'])
    data_variables = list(input_forcing.keys())
    lon = input_forcing.variables['longitude'].values
    lat = input_forcing.variables['latitude'].values

    # %% extract indices of forcing ids based on the drainage database
    n = len(drainage_db.hruId)
    ind = []
    hruid =  drainage_db.variables['hruId']

    for i in range(n):
        fid = np.where(np.int32(input_basin['COMID'].values) == hruid[i].values)[0]
        ind = np.append(ind, fid)

    ind = np.int32(ind)

    # %% reorder input forcing
    forc_vec = xr.Dataset(
        {
            data_variables[0]: (["subbasin", "time"], input_forcing[data_variables[0]].values[:,ind].transpose()),
        },
        coords={
            "time": input_forcing['time'].values.copy(),
            "lon": (["subbasin"], lon),
            "lat": (["subbasin"], lat),
        }
        )
    for n in data_variables[1::]:
        forc_vec[n] = (("subbasin", "time"), input_forcing[n].values[: , ind].transpose())
        forc_vec[n].coords["time"]          = input_forcing['time'].values.copy()
        forc_vec[n].coords["lon"]           = (["subbasin"], lon)
        forc_vec[n].coords["lat"]           = (["subbasin"], lat)
        forc_vec[n].attrs["units"]          = input_forcing[n].units
        forc_vec[n].attrs["grid_mapping"]   = 'crs'
        forc_vec[n].encoding['coordinates'] = 'time lon lat'

    # %% update meta data attribuetes
    now = datetime.now()
    forc_vec.attrs['Conventions'] = 'CF-1.6'
    forc_vec.attrs['License']     = 'The data were written by CWARHM'
    forc_vec.attrs['history']     = 'Created ' + now.strftime('%Y/%m/%d %H:%M:%S')
    forc_vec.attrs['featureType'] = 'timeSeries'         
    
    # editing lat attribute
    forc_vec['lat'].attrs['standard_name'] = 'latitude'
    forc_vec['lat'].attrs['units']         = 'degrees_north'
    forc_vec['lat'].attrs['axis']          = 'Y'
    
    # editing lon attribute
    forc_vec['lon'].attrs['standard_name'] = 'longitude'
    forc_vec['lon'].attrs['units']         = 'degrees_east'
    forc_vec['lon'].attrs['axis']          = 'X'
    
    # editing time attribute
    forc_vec['time'].attrs['standard_name'] = 'time'
    forc_vec['time'].attrs['axis']          = 'T'
    forc_vec['time'].encoding['calendar']   = 'gregorian'
    forc_vec.encoding.update(unlimited_dims = 'time')
    
    # coordinate system
    forc_vec['crs'] = drainage_db['crs'].copy()
    
    # Define a variable for the points and set the 'timeseries_id' (required for some viewers).
    forc_vec['subbasin'] = (['subbasin'], drainage_db['segId'].values.astype(np.int32).astype('S20'))
    forc_vec['subbasin'].attrs['cf_role'] = 'timeseries_id'

    return forc_vec

    
class MeshClassIniFile():
    """A python class to write the CLASS.ini file for the Land-Surface scheme "CLASS" in MESH

    Attributes
    ----------
    filepath : str
        path to write the ini file to
    n_gru : int
        number of GRU's
    """    
    def __init__(self, filepath, n_GRU, pd_datetime_start,
                title='Default set-up created with CWARHM', name="Bart van Osnabrugge",
                place="University of Saskatchewan"
                ):
        """
        :param filepath: path to write the ini file to
        :type filepath: str
        :param n_GRU: number of GRU's
        :type n_GRU: int
        """        
        self.filepath = filepath
        self.n_gru = n_GRU
        self.pd_datetime_start = pd_datetime_start
        self.title = title
        self.name = name
        self.place = place
    
    def set_header(self,title,name,place):
        '''sets first three lines with header information'''
        line1 = "{:<70}".format(title)+'01 TITLE'
        line2 = "{:<70}".format(name)+'02 NAME'
        line3 = "{:<70}".format(place)+'03 PLACE'
        self.header = line1+'\n'+line2+'\n'+line3+'\n'

    def set_area_info(self,deglat=0.00,deglon=0.00,windspeed_ref_height=40.00,
                        temp_humid_ref_height=40.00, surface_roughness_height=50.00,
                        ground_cover_flag=-1, ILW=1, n_grid=0):
        '''sets line 4 DEGLAT/DEGLON/ZRFM/ZRFH/ZBLD/GC/ILW/NL/NM'''
        n_GRU = self.n_gru
        line4 = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t'.format(
            deglat,deglon,windspeed_ref_height,temp_humid_ref_height,
            surface_roughness_height,ground_cover_flag,ILW,n_grid,n_GRU
        ).expandtabs(4)
        line4 = "{:<70}".format(line4)+'04 DEGLAT/DEGLON/ZRFM/ZRFH/ZBLD/GC/ILW/NL/NM'
        self.area_info = line4
    
    def GRU_part_template(self):
        self.GRU_template = \
        '''
        _FCAN-NL#_    _FCAN-BL#_    _FCAN-C#_   _FCAN-G#_   _FCAN-U#_     _LAMX-NL#_    _LAMX-BL#_    _LAMX-C#_   _LAMX-G#_       05Land class type/fcanrow/pamxrow
        _LNZ0-NL#_    _LNZ0-BL#_    _LNZ0-C#_   _LNZ0-G#_   _LNZ0-U#_     _LAMN-NL#_    _LAMN-BL#_    _LAMN-C#_   _LAMN-G#_       06lnz0row/pamnrow
        _ALVC-NL#_    _ALVC-BL#_    _ALVC-C#_   _ALVC-G#_   _ALVC-U#_     _CMAS-NL#_    _CMAS-BL#_    _CMAS-C#_   _CMAS-G#_       07alvcrow/cmasrow
        _ALIC-NL#_    _ALIC-BL#_    _ALIC-C#_   _ALIC-G#_   _ALIC-U#_     _ROOT-NL#_    _ROOT-BL#_    _ROOT-C#_   _ROOT-G#_       08alirow/rootrow
        _RSMN-NL#_    _RSMN-BL#_    _RSMN-C#_   _RSMN-G#_                 _QA50-NL#_    _QA50-BL#_    _QA50-C#_   _QA50-G#_       09rsmnrow/qa50row
        _VPDA-NL#_    _VPDA-BL#_    _VPDA-C#_   _VPDA-G#_                 _VPDB-NL#_    _VPDB-BL#_    _VPDB-C#_   _VPDB-G#_       10vpdarow/vpbprow
        _PSGA-NL#_    _PSGA-BL#_    _PSGA-C#_   _PSGA-G#_                _PSGB-NL#_    _PSGB-BL#_    _PSGB-C#_   _PSGB-G#_       11psgarow/psgbrow
        _DRN-#_       _SDEP-#_      _FARE-#_    _DDEN-#_                                                                          12drnrow/sdeprow/farerow/ddenrow
        _XSLOPE-#_    _GRKF-#_      _MANN-#_    _KSAT-#_   1                                                                      13xslprow/grkfrow/manrow/WFCIROW/midrow
        _SAND1-#_     _SAND2-#_     _SAND3-#_                                                                                     14sand
        _CLAY1-#_     _CLAY2-#_     _CLAY3-#_                                                                                     15clay
        _ORGM1-#_     _ORGM2-#_     _ORGM3-#_                                                                                     16org
        _TBAR1-#_     _TBAR2-#_     _TBAR3-#_     _TCAN-#_      _TSNO-#_      _TPND-#_                                            17temperature-soil/can/sno/pnd
        _THLQ1-#_     _THLQ2-#_     _THLQ3-#_     _THIC1-#_     _THIC2-#_     _THIC3-#_   _ZPND-#_                                18soil moisture-soil/ice/pnd
        _RCAN-#_      _SCAN-#_      _SNO-#_       _ALBS-#_      _RHOS-#_      _GRO-#_                                             19rcan/scan/sno/albs/rho/gro
        '''

    def write_default_GRU_part(self):
        '''Writes 15 lines for a single GRU parameters and initialization values'''
        GRU_default_block = \
        '''
0.00    0.00    0.00    0.00    1.00    0.00    0.00    0.00    0.00  05 5xFCAN/4xLAMX
0.00    0.00    0.00    0.00    0.30    0.00    0.00    0.00    0.00  06 5xLNZ0/4xLAMN
0.00    0.00    0.00    0.00    0.09    0.00    0.00    0.00    0.00  07 5xALVC/4xCMAS
0.00    0.00    0.00    0.00    0.15    0.00    0.00    0.00    0.00  08 5xALIC/4xROOT
0.00    0.00    0.00    0.00            0.00    0.00    0.00    0.00  09 4xRSMN/4xQA50
0.00    0.00    0.00    0.00            0.00    0.00    0.00    0.00  10 4xVPDA/4xVPDB
0.00    0.00    0.00    0.00            0.00    0.00    0.00    0.00  11 4xPSGA/4xPSGB
0.00    1.91    1.00    7.41                                          12 DRN/SDEP/FARE/DD
0.106    0.57   0.015 3.9E-05       1 Urban                           13 XSLP/XDRAINH/MANN/KSAT/MID         | 4F8.1, I8
23        25        33                                                14 3xSAND                             | 3F10.1
11        12        15                                                15 3xCLAY                             | 3F10.1
0.00      0.00      0.00                                              16 3xORGM                             | 3F10.1
5.00      5.00      5.00      0.00      0.00      0.00                17 3xTBAR/TCAN/TSNO/TPND              | 6F10.2
0.20      0.20      0.20      0.00      0.00      0.00      0.00      18 3xTHLQ/3xTHIC/ZPND                 | 7F10.3
0.00      0.00      0.00      0.00      0.00      0.00                19 RCAN/SCAN/SNO/ALBS/RHOS/GRO        | 2F10.4,F10.2,F10.3,F10.4,F10.3
        '''
        return GRU_default_block

    def set_start_end_times(self,pd_datetime_start):
        '''Write dates to control CLASS point outputs and the start date'''
        line_fill = "1\t1\t1\t1\t".expandtabs(10)
        line20 = "{:<70}".format(line_fill)+'20 (not used, but 4x integer values are required)'
        line21 = "{:<70}".format(line_fill)+'21 (not used, but 4x integer values are required)'
        
        iyear = pd_datetime_start.year
        ijday = pd_datetime_start.dayofyear
        iminutes = pd_datetime_start.minute
        ihour = pd_datetime_start.hour

        start_time_line = "{}\t{}\t{}\t{}\t".format(ihour,iminutes,ijday,iyear).expandtabs(10)
        start_time_line = "{:<70}".format(start_time_line)+'22 IHOUR/IMINS/IJDAY/IYEAR'
        self.start_end_times = line20+'\n'+line21+'\n'+start_time_line


    def build_default_ini_file(self):
        self.set_header(self.title,self.name,self.place)
        self.set_area_info()
        self.set_start_end_times(self.pd_datetime_start)

    
    def write_ini_file(self):
        with open(self.filepath,'w') as inif:
            inif.write(self.header)
            inif.write(self.area_info)
            for n in range(self.n_gru):
                inif.write(self.write_default_GRU_part())
            inif.write(self.start_end_times)

class MeshRunOptionsIniFile():
    """Class to edit Mesh Run options and write ini file
    """    
    def __init__(self, inifilepath, forcing_file=None) -> None:
        
        self.inifilepath = inifilepath
        self.template = self.get_template()
        self.flags = self.set_default_flags()
        if forcing_file:
            print('forcing setting parsed from forcing file')
            self.set_flags_from_ff(forcing_file)
        else:
            print('forcing flags are set as default and need to be set manually')
        self.write_ini_file()
        
    
    def get_template(self):
        template =  \
'''MESH input run options file
##### Control Flags #####
----#
$NOCF$                                                   # Number of control flags 
SHDFILEFLAG              $SHDFILEFLAG$
BASINFORCINGFLAG         $SHDFILEFLAG$ start_date=$STARTDATE$ hf=$HF$ time_shift=$TIMESHIFT$ fname=$FNAME$
BASINSHORTWAVEFLAG       name_var=$BASINSHORTWAVEFLAG$
BASINHUMIDITYFLAG        name_var=$BASINHUMIDITYFLAG$
BASINRAINFLAG            name_var=$BASINRAINFLAG$
BASINPRESFLAG            name_var=$BASINPRESFLAG$
BASINLONGWAVEFLAG        name_var=$BASINLONGWAVEFLAG$
BASINWINDFLAG            name_var=$BASINWINDFLAG$
BASINTEMPERATUREFLAG     name_var=$BASINTEMPERATUREFLAG$
TIMESTEPFLAG             $TIMESTEPFLAG$
INPUTPARAMSFORMFLAG      $INPUTPARAMSFORMFLAG$
IDISP                    $IDISP$                          #02 Vegetation Displacement Height Calculation  | A20, I4
IZREF                    $IZREF$                          #03 Atmospheric Model Reference Height          | A20, I4
IPCP                     $IPCP$                           #04 Rainfall-Snowfall Partition distribution    | A20, I4
IWF                      $IWF$                            #08 Water Flow control                          | A20, I4
FROZENSOILINFILFLAG      $FROZENSOILINFILFLAG$            #22 frozen soil infiltration flag               | A20, I4
SAVERESUMEFLAG           $SAVERESUMEFLAG$
RESUMEFLAG               $RESUMEFLAG$
INTERPOLATIONFLAG        $INTERPOLATIONFLAG$
SOILINIFLAG              $SOILINIFLAG$
PBSMFLAG                 $PBSMFLAG$
BASEFLOWFLAG             $BASEFLOWFLAG$
RUNMODE                  $RUNMODE$
BASINBALANCEOUTFLAG      $BASINBALANCEOUTFLAG$
BASINAVGWBFILEFLAG 	     $BASINAVGWBFILEFLAG$
BASINAVGEBFILEFLAG 	     $BASINAVGEBFILEFLAG$ 
DIAGNOSEMODE             $DIAGNOSEMODE$
PRINTSIMSTATUS           $PRINTSIMSTATUS$
OUTFILESFLAG             $OUTFILESFLAG$
AUTOCALIBRATIONFLAG    	 $AUTOCALIBRATIONFLAG$
METRICSSPINUP        	 $METRICSSPINUP$
##### Output Grid selection #####
----#
$NOGP$   #Maximum 5 points                               #17 Number of output grid points
---------#---------#---------#---------#---------#
$GRIDNUMBOUT$                                              #19 Grid number
$GRUOUT$                                              #20 GRU (if applicable)
$CLASSOUT$                                                #21 Output directory
##### Output Directory #####
---------#
$OUTPUTDIR$   												    #24 Output Directory for total-basin files
##### Simulation Run Times #####
---#---#---#---#
$STARTYEAR$   $STARTDAY$   $STARTHOUR$   $STARTMINUTE$          #27 Start year, day, hour, minute 2000 279
$STOPYEAR$   $STOPDAY$   $STOPHOUR$   $STOPMINUTE$                                       #28 Stop year, day, hour, minute  2000 288
'''
        return template
        
    def set_default_flags(self):
        '''create dictionairy with default flags'''
        default_flags = dict()
        default_flags['NOCF'] = '31'
        default_flags['SHDFILEFLAG'] = 'nc_subbasin'
        default_flags['STARTDATE'] = '20001001'
        default_flags['HF'] = 60
        default_flags['TIMESHIFT'] = 0
        default_flags['FNAME'] = 'MESH_input.nc'
        default_flags['BASINSHORTWAVEFLAG'] = 'FB'
        default_flags['BASINHUMIDITYFLAG'] = 'HU'
        default_flags['BASINRAINFLAG'] = 'PR'
        default_flags['BASINPRESFLAG'] = 'P0'
        default_flags['BASINLONGWAVEFLAG'] = 'FI'
        default_flags['BASINWINDFLAG'] = 'UV'
        default_flags['BASINTEMPERATUREFLAG'] = 'TT'
        default_flags['TIMESTEPFLAG'] = 30
        default_flags['INPUTPARAMSFORMFLAG'] = 'txt'
        default_flags['IDISP'] = 0
        default_flags['IZREF'] = 1
        default_flags['IPCP'] = 1
        default_flags['IWF'] = 1
        default_flags['FROZENSOILINFILFLAG'] = 1
        default_flags['SAVERESUMEFLAG'] = 0
        default_flags['RESUMEFLAG'] = 0
        default_flags['INTERPOLATIONFLAG'] = 1
        default_flags['SOILINIFLAG'] = 1
        default_flags['PBSMFLAG'] = 1
        default_flags['BASEFLOWFLAG'] = 'wf_lzs'
        default_flags['RUNMODE'] = 'runrte'
        default_flags['BASINBALANCEOUTFLAG'] = 'none'
        default_flags['BASINAVGWBFILEFLAG'] = 'daily'
        default_flags['BASINAVGEBFILEFLAG'] = 'daily'
        default_flags['DIAGNOSEMODE'] = 'on'
        default_flags['PRINTSIMSTATUS'] = 'date_monthly'
        default_flags['OUTFILESFLAG'] = 'on'
        default_flags['AUTOCALIBRATIONFLAG'] = 1
        default_flags['METRICSSPINUP'] = 366
        default_flags['NOGP'] = 0
        default_flags['GRIDNUMBOUT'] = 1936
        default_flags['GRUOUT'] = 1
        default_flags['CLASSOUT'] = 'CLASSOUT'
        default_flags['OUTPUTDIR'] = '.'
        default_flags['STARTYEAR'] = 2000
        default_flags['STARTDAY'] = 275
        default_flags['STARTHOUR'] = 0
        default_flags['STARTMINUTE'] = 0
        default_flags['STOPYEAR'] = 2018
        default_flags['STOPDAY'] = '001'
        default_flags['STOPHOUR'] = 0
        default_flags['STOPMINUTE'] = 0
        return default_flags

    def set_flags_from_ff(self,forcing_file):
        flags = self.flags
        # open forcing file
        ds = xr.open_dataset(forcing_file)
        # get start and end date time
        datetimestart = pd.Timestamp(ds.time.values[0])
        datetimeend = pd.Timestamp(ds.time.values[-1])
        timestep_ms = ds.time.values[1]-ds.time.values[0]
        timestep_minutes = timestep_ms.astype('timedelta64[m]').astype('int')

        # start stop flags
        flags['STARTDATE'] = datetimestart.strftime('%Y%m%d')
        flags['HF'] = timestep_minutes
        flags['STARTYEAR'] = datetimestart.year
        flags['STARTDAY'] = "{:02d}".format(datetimestart.day_of_year)
        flags['STARTHOUR'] = datetimestart.hour
        flags['STARTMINUTE'] = datetimestart.minute
        flags['STOPYEAR'] = datetimeend.year
        flags['STOPDAY'] = "{:02d}".format(datetimeend.day_of_year)
        flags['STOPHOUR'] = datetimeend.hour
        flags['STOPMINUTE'] = datetimeend.minute
        # default time step is 30 min, only adjust this when
        # forcing time step is smaller than 30 min
        if timestep_minutes < flags['TIMESTEPFLAG']:
            flags['TIMESTEPFLAG'] = timestep_minutes

        # name flag
        flags['FNAME'] = ntpath.basename(forcing_file)

        self.flags = flags

    def change_flag(self,flag,flag_value):
        '''replace value in ini file with given value'''
        flags = self.flags
        flags[flag] = flag_value
        self.write_ini_file()

    def parse_flag_values(self):
        '''replace all tags in template with flag values'''
        text = self.template
        for key, value in self.flags.items():
            text = text.replace('$'+str(key)+'$',str(value))
        return text

    def write_ini_file(self):
        '''parse flag values and write to file '''
        text = self.parse_flag_values()
        with open(self.inifilepath,'w') as setf:
            setf.write(text)