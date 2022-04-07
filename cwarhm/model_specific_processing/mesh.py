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
    lon = input_forcing.variables['longitude'].values
    lat = input_forcing.variables['latitude'].values
    # set lon lat as coordinates so that these are not in the data variables list
    # lon and lat are reindexed first separately
    input_forcing = input_forcing.set_coords(['latitude','longitude'])
    data_variables = list(input_forcing.keys())


    # %% extract indices of forcing ids based on the drainage database
    n = len(drainage_db.hruId)
    ind = []
    hruid =  drainage_db.variables['hruId']

    for i in range(n):
        fid = np.where(np.int32(input_basin['COMID'].values) == hruid[i].values)[0]
        ind = np.append(ind, fid)

    ind = np.int32(ind)

    # first reindex lat and lon coordinates
    lon_reind = lon[ind]
    lat_reind = lat[ind]

    # %% reorder input forcing
    # initialize with the first variable
    forc_vec = xr.Dataset(
        {
            data_variables[0]: (["subbasin", "time"], input_forcing[data_variables[0]].values[:,ind].transpose()),
        },
        coords={
            "time": input_forcing['time'].values.copy(),
            "lon": (["subbasin"], lon_reind),
            "lat": (["subbasin"], lat_reind),
        }
        )
    # then repeat for all other variables
    for n in data_variables[1::]:
        forc_vec[n] = (("subbasin", "time"), input_forcing[n].values[: , ind].transpose())
        forc_vec[n].coords["time"]          = input_forcing['time'].values.copy()
        forc_vec[n].coords["lon"]           = (["subbasin"], lon_reind)
        forc_vec[n].coords["lat"]           = (["subbasin"], lat_reind)
        forc_vec[n].attrs["units"]          = input_forcing[n].units
        forc_vec[n].attrs["grid_mapping"]   = 'crs'
        forc_vec[n].encoding['coordinates'] = 'time lon lat'

    # %% update meta data attributes
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
        """sets first three comment lines with header information

        :param title: title of the model run
        :type title: str
        :param name: name of the modeler
        :type name: str
        :param place: affiliation of modeler or modelling domain
        :type place: str
        """        
        
        line1 = "{:<70}".format(title)+'01 TITLE'
        line2 = "{:<70}".format(name)+'02 NAME'
        line3 = "{:<70}".format(place)+'03 PLACE'
        self.header = line1+'\n'+line2+'\n'+line3+'\n'

    def set_area_info(self,deglat=0.00,deglon=0.00,windspeed_ref_height=40.00,
                        temp_humid_ref_height=40.00, surface_roughness_height=50.00,
                        ground_cover_flag=-1, ILW=1, n_grid=0):
        """sets line 4 DEGLAT/DEGLON/ZRFM/ZRFH/ZBLD/GC/ILW/NL/NM

        :param deglat: Latitude of the sit or grid-cell in degrees, relevant
        for grid version of MESH or site-specific only, otherwise indicative defaults to 0.00
        :type deglat: float, optional
        :param deglon: Longitude of the sit or grid-cell in degrees, , relevant
        for grid version of MESH or site-specific only, otherwise indicativedefaults to 0.00
        :type deglon: float, optional
        :param windspeed_ref_height: Reference height (measurement height) for wind speed, defaults to 40.00
        :type windspeed_ref_height: float, optional
        :param temp_humid_ref_height: Reference height (measurement height) for temperature and humidity, defaults to 40.00
        :type temp_humid_ref_height: float, optional
        :param surface_roughness_height: Height into the atmosphere for aggregating surface roughness (usually in the order of 50-100 m), defaults to 50.00
        :type surface_roughness_height: float, optional
        :param ground_cover_flag: Ground cover flag; set to -1.0 if the GRUs in the file represent a "land surface", defaults to -1
        :type ground_cover_flag: int, optional
        :param ILW: Set to 1 (See the note on ILW below), defaults to 1
        :type ILW: int, optional
        :param n_grid: Number of grid-cells in the basin; this number must match the total number of grid-cells "TotalNumOfGrids" from the basin information file, defaults to 0
        :type n_grid: int, optional
        """                        
        n_GRU = self.n_gru
        line4 = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t'.format(
            deglat,deglon,windspeed_ref_height,temp_humid_ref_height,
            surface_roughness_height,ground_cover_flag,ILW,n_grid,n_GRU
        ).expandtabs(4)
        line4 = "{:<70}".format(line4)+'04 DEGLAT/DEGLON/ZRFM/ZRFH/ZBLD/GC/ILW/NL/NM'
        self.area_info = line4
    
    def GRU_part_template(self):
        """Template of the text related to a single GRU

        Template values can be replaced by replacing values encapsulated with "_"
        """        
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
        """Write dates to control CLASS point outputs and the start date

        :param pd_datetime_start: datetime of the first time value in forcing file
        :type pd_datetime_start: pandas.Timestamp
        """        
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
        """set_header, area_info and start_end_times with default values
        """        
        self.set_header(self.title,self.name,self.place)
        self.set_area_info()
        self.set_start_end_times(self.pd_datetime_start)

    
    def write_ini_file(self):
        """write ini text to file, with n_gru default GRUs
        """        
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
        """
        Parameters
        ----------
        inifilepath : str
            path to write file to
        forcing_file : str, optional
            path to forcing file. if set, flags are set to match , by default None
        """        
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
   $NOCF$                                                # Number of control flags 
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
    $NOGP$   #Maximum 5 points                            #17 Number of output grid points
---------#---------#---------#---------#---------#
    $GRIDNUMBOUT$                                         #19 Grid number
    $GRUOUT$                                              #20 GRU (if applicable)
$CLASSOUT$                                                #21 Output directory
##### Output Directory #####
---------#
$OUTPUTDIR$   										      #24 Output Directory for total-basin files
##### Simulation Run Times #####
---#---#---#---#
$STARTYEAR$   $STARTDAY$   $STARTHOUR$   $STARTMINUTE$    #27 Start year, day, hour, minute 2000 279
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
        default_flags['FNAME'] = 'MESH_input'
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
        default_flags['OUTFILESFLAG'] = 'off'
        default_flags['AUTOCALIBRATIONFLAG'] = 1
        default_flags['METRICSSPINUP'] = 366
        default_flags['NOGP'] = 0
        default_flags['GRIDNUMBOUT'] = 1936
        default_flags['GRUOUT'] = 1
        default_flags['CLASSOUT'] = 'CLASSOUT'
        default_flags['OUTPUTDIR'] = 'output'
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
        print(timestep_minutes)

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

        # name flag from filename, without extension
        flags['FNAME'] = ntpath.basename(forcing_file).split('.')[0]

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

class MeshHydrologyIniFile():
    """_summary_
    """
    def __init__(self, inifilepath, n_gru, mesh_setting_flags=None,
                routing_parameters=None, gru_independent_parameters=None,
                 gru_hydrologic_parameters=None) -> None:
        self.inifilepath = inifilepath
        self.template = self.get_template()
        self.flags = self.set_default_flags()
        if mesh_setting_flags:
            print('NOT IMPLEMENTED YET Hydrology ini file parsed with settings')
        else:
            print('Hydrology ini is set as default')
        if routing_parameters:
            print('Set routing parameters from input')
            self.routing_parameters = routing_parameters
        else:
            self.routing_parameters = self.set_default_routing_parameters()
            print('Routing parameters set as default r2n, r1n, flz, pwr (5 identical classes)')
        if gru_independent_parameters:
            self.gru_independent_parameters = gru_independent_parameters
            print("set gru independent parameters from input")
        else:
            self.gru_independent_parameters = self.set_default_gru_independent_parameters()
        if gru_hydrologic_parameters:
            self.gru_hydrologic_parameters = gru_hydrologic_parameters
            print('set gru dependent parameters from input')
        else:
            self.gru_hydrologic_parameters = self.set_default_gru_dependent_parameters(n_gru)
            print('default hydrologic gru dependent parameters')

        self.write_ini_file()

    def get_template(self):
        template =  \
'''2.0: MESH Hydrology Parameters (v2.0)
!> Lines that begin with '!' are skipped as comments.
!> All variable lines have the same free-format space delimited structure:
!> [Variable name] [Value]
##### Option Flags #####
----#
    $NOCF$ # Number of option flags.
####### Channel routing parameters #####
-------#
    $NOCRPS$ # Number of channel routing parameters.
$$$CHANNEL_ROUTING_PART$$$
##### GRU class independent hydrologic parameters #####
-------#
    $NOGRUIPS$ # Number of GRU independent hydrologic parameters
$$$GRU_INDEPENDENT_PART$$$
##### GRU class dependent hydrologic parameters #####
-------#
    $NOGRUHPS$ # Number of GRU dependent hydrologic parameters.
$$$GRU_DEPENDENT_PART$$$
'''
        return template

    def set_default_flags(self):
        '''create dictionairy with default flags'''
        default_flags = dict()
        default_flags['NOCF'] = 0
        default_flags['NOCRPS'] = 4
        default_flags['NOGRUIPS'] = 5
        default_flags['NOGRUHPS'] = 13
        return default_flags

    def set_default_routing_parameters(self):
        default_routing_parameters = pd.DataFrame(
        data = np.array(
            [[0.035, 0.10, 1.0E-04, 2.00] for i in range(5)]
        ).transpose(),
        index=['r2n','r1n','flz','pwr'],
        columns=[str(n+1) for n in range(5)]
        )
        return default_routing_parameters

    def parse_routing_parameters(self):
        routing_parameters_text = self.routing_parameters.__repr__()
        # make the header line a comment
        all_lines = routing_parameters_text.split('\n')
        line1 = all_lines[0]
        line1_com = '!>\t'.expandtabs()+line1.lstrip()
        all_lines[0] = line1_com
        text_routing_parameters = '\n'.join(all_lines)
        return text_routing_parameters

    def set_default_gru_independent_parameters(self):
        dgip = dict()
        dgip['SOIL_POR_MAX'] = 0.8
        dgip['SOIL_DEPTH'] = 4.1
        dgip['S0'] = 1.0
        dgip['T_ICE_LENS'] = -10.0
        dgip['T0_ACC'] = [0]*30
        return dgip

    def parse_gru_independent_parameters(self):
        dgip = self.gru_independent_parameters
        lines = []
        for key,value in dgip.items():
            if key != 'T0_ACC':
                lines.append(key+'\t'+str(value))
            else:
                T0_ACC_header = '!> YEAR\t'+'\t'.join([str(i+1) for i in range(len(value))])+'\n'
                T0_ACC_values = 't0_ACC\t'+'\t'.join([str(a) for a in dgip['T0_ACC']])
                T0_ACC_part = T0_ACC_header+T0_ACC_values
        # join all parts and ensure T0_ACC part is last
        text = '\n'.join(lines)
        text = text+'\n'+T0_ACC_part
        return text

    def set_default_gru_dependent_parameters(self,n_gru):
        default_grudep = pd.DataFrame(
        data = np.array(
            [[0,0.1,0.1,0.1,300.0,6.0,1.0,0.5,0.0,2.1,0.0,0.0,0.0] for i in range(n_gru)]
        ).transpose(),
        index=['IWF','ZSNL','ZPLS','ZPLG','fetch','Ht','N_S','A_S',
                'Distrib','FRZC','FREZTH','SWELIM','SNDENLIM'],
        columns=[str(n+1) for n in range(n_gru)]
        )
        return default_grudep

    def parse_parameter_dataframe(self,dataframe,header=''):
        text = dataframe.to_string()
        # make the header line a comment
        all_lines = text.split('\n')
        line1 = all_lines[0]
        line1_com = '!>{}\t'.format(header).expandtabs(12)+line1.lstrip()
        #line1_com = '!>\t'.expandtabs()+line1.lstrip()
        all_lines[0] = line1_com
        all_lines_expanded = [line.expandtabs(12) for line in all_lines]
        text_parameters = '\n'.join(all_lines_expanded)
        return text_parameters

    def parse_setup(self):
        '''replace all tags in template with flag values'''
        text = self.template
        # first replace all flags
        for key, value in self.flags.items():
            text = text.replace('$'+str(key)+'$',str(value))
        # then set the $$$ text blogs
        #text = text.replace('$$$CHANNEL_ROUTING_PART$$$',self.parse_routing_parameters()+'\n')
        text = text.replace('$$$CHANNEL_ROUTING_PART$$$',self.parse_parameter_dataframe(self.routing_parameters,'NRVR')+'\n')
        text = text.replace('$$$GRU_INDEPENDENT_PART$$$',self.parse_gru_independent_parameters()+'\n')
        text = text.replace('$$$GRU_DEPENDENT_PART$$$',self.parse_parameter_dataframe(self.gru_hydrologic_parameters,'GRU')+'\n')
        return text

    def write_ini_file(self):
        text = self.parse_setup()
        with open(self.inifilepath,'w') as setf:
            setf.write(text)

class MeshReservoirTxtFile():
    '''This file contains information about the controlled and natural reservoirs 
    or lakes in the basin. 

    Two types of reservoirs are supported in Standalone MESH. The first is the 
    controlled reservoir, which replaces modelled streamflow with values from 
    this file. The second is the natural reservoir, or lake, which allows a
    power curve to regulate release from an outlet location. A third option,
    a polynomial release curve, is implemented in test versions of the model.

    This file is required by Standalone MESH, even if the watershed contains no 
    reservoirs. If reservoirs are not required, a dummy file with fictitious data 
    on the first line must exist, which follows the appropriate formatting rules. 
    The following line can be used to create the dummy file. The first number is 
    the number of reservoirs, and should be set to zero.

    TODO: currently only gives the dummy file
    '''
    def __init__(self,inifilepath) -> None:
        self.inifilepath = inifilepath
        self.template = self.get_template()
        self.write_ini_file()

    def get_template(self):
        template = '''0    0    0'''
        return template

    def parse_setup(self):
        '''replace all tags in template with flag values'''
        text = self.template
        return text

    def write_ini_file(self):
        text = self.parse_setup()
        with open(self.inifilepath,'w') as setf:
            setf.write(text)
    
class MeshSoilLevelTxtFile():
    '''MESH_input_soil_levels.txt describes the depth in meters of connected 
    soil layers in the soil profile.
    
    It is similar to the Soil_3lev file used by the CLASS 
    Stand-Alone Driver. The first layer is the surface layer, which can be no 
    less than 10 cm in depth. A minimum of three soil layers are required 
    in the file.
    '''
    def __init__(self,inifilepath,soil_layers=None) -> None:
        self.inifilepath = inifilepath
        self.template = self.get_template()
        self.flags = self.set_default_flags()
        if soil_layers:
            self.soil_layers = soil_layers
            print("setting soil layers from soil layers input")
        else:
            self.soil_layers = self.set_default_soil_layers()
            print("setting three default soil layers")
        self.write_ini_file()

    def get_template(self):
        template = ''''''
        return template

    def set_default_flags(self):
        self.flags = None

    def set_default_soil_layers(self):
        default_soil_layers = pd.DataFrame(
        data = np.array(
            [[0.10, 0.25, 3.75],[0.10, 0.35, 4.10]]
        ).transpose(),
        columns=['DELZ','ZBOT']
        )
        return default_soil_layers


    def parse_setup(self):
        '''replace all tags in template with flag values'''
        text = self.template # template is empty here
        lines = self.soil_layers.to_string(header=False,index=False,col_space=8).split('\n')
        formatted_lines = ['{}\t#DELZ/ZBOT'.format(line) for line in lines]
        text = '\n'.join(formatted_lines)
        return text

    def write_ini_file(self):
        text = self.parse_setup()
        with open(self.inifilepath,'w') as setf:
            setf.write(text)

class MeshInputStreamflowTxtFile():
    '''This file contains measured streamflow values for gauged locations

    It can also be used to specify locations where streamflow values will 
    be output even if no gauge actually exists at that location.


    At a minimum, every configuration of Standalone MESH must contain at least one
    streamflow gauge location. Even if the watershed does not contain an actual 
    streamflow gauge, one must still be included in the streamflow file. It is also
    important that at least one gauge in the file has a measured value greater than 
    zero during the first time step. This value is used to initialize the flow in 
    the stream network. This value must be greater than zero and must be included 
    even if the watershed contains no actual gauges with measured data.

    For more information see https://wiki.usask.ca/display/MESH/MESH_input_streamflow.txt
    '''
    def __init__(self,inifilepath,streamflow=None,forcing_file=None) -> None:
        self.inifilepath = inifilepath
        self.template = self.get_template()
        self.flags = self.set_default_flags()
        if streamflow:
            self.streamflow = streamflow
            print("setting streamflow from streamflow input")
            self.set_flags_from_streamflow()
            print("setting header flags from streamflow input")
        else:
            if forcing_file:
                self.streamflow = self.match_streamflow_with_forcing(forcing_file)
                self.set_flags_from_streamflow()
                print("setting default dummy streamflow that matches forcing length")
            else:
                self.streamflow = self.set_default_streamflow()
                self.set_flags_from_streamflow() # to make sure compatibality
                print("no input, default streamflow set - manual intervention needed")

        self.write_ini_file()

    def get_template(self):
        '''The first line of the file is a comment line. Immediately following 
        this line, in the second line in the file, is the header information. 
        The header contains the number of streamflow gauge locations, the 
        starting date of the record (for all gauges), and the uniform 
        time-stepping of the records. It should also contain the number of 
        records in the file, but this value is not used. The simulation will run 
        until it reaches the user-specified stopping date, runs out of 
        meteorological input data, or runs out of streamflow records to 
        read from this file.'''
        template = \
'''# MESH streamflow record input file 01
$WF_NO$    $WF_NL$    $WF_MHRD$   $WF_KT$ $WF_START_YEAR$  $WF_START_DAY$    $WF_START_HOUR$ 02 WF_NO/WF_NL/WF_MHRD/WF_KT/WF_START_YEAR/WF_START_DAY/WF_START_HOUR'''
        return template

    def set_default_flags(self):
        default_flag = dict()
        default_flag['WF_NO'] = 1
        default_flag['WF_NL'] = 0 #obsolete
        default_flag['WF_MHRD'] = 0 #obsolete
        default_flag['WF_KT'] = 24
        default_flag['WF_START_YEAR'] = 2000
        default_flag['WF_START_DAY'] = 1
        default_flag['WF_START_HOUR'] = 1
        return default_flag

    def set_default_streamflow(self):
        streamflow_xr = xr.Dataset(
        {
            'streamflow': (["gauge","time"],np.array([[10]*10]))
        },
        coords={
            "time":pd.date_range(start='2000-01-01',periods=10,freq='D'),
            "id":  (["gauge"], ['default_gauge']),
            "lon": (["gauge"], [0.00]),
            "lat": (["gauge"], [0.00]),
        },
        )
        # update metadata
        streamflow_xr.attrs['Conventions'] = 'CF-1.6'
        streamflow_xr.attrs['history'] = 'Example default input for MeshStreamflowTxt()'
        streamflow_xr.attrs['featureType'] = 'timeSeries'
        return streamflow_xr

    def set_flags_from_streamflow(self):
        flags = self.flags
        sf = self.streamflow

        # calculate timestep
        datetimestart = pd.Timestamp(sf.time.values[0])
        timestep_ms = sf.time.values[1]-sf.time.values[0]
        timestep_hr = timestep_ms.astype('timedelta64[h]').astype('int')
        # set flags
        flags['WF_NO'] = sf.dims['gauge']
        flags['WF_KT'] = timestep_hr
        flags['WF_START_YEAR'] = datetimestart.year
        flags['WF_START_DAY'] = datetimestart.day_of_year
        flags['WF_START_HOUR'] = datetimestart.hour
        self.flags = flags

    def match_streamflow_with_forcing(self,forcing_dataset):
        fds = forcing_dataset
        empty_streamflow_array = np.array([[-1]*len(fds.time)])
        empty_streamflow_array[0,0] = 10
        streamflow_xr = xr.Dataset(
        {
            'streamflow': (["gauge","time"],empty_streamflow_array)
        },
        coords={
            "time": fds.time,
            "id":  (["gauge"], ['default_gauge']),
            "lon": (["gauge"], [0.00]),
            "lat": (["gauge"], [0.00]),
        },
        )
        # update metadata
        streamflow_xr.attrs['Conventions'] = 'CF-1.6'
        streamflow_xr.attrs['history'] = 'Example default input for MeshStreamflowTxt()'
        streamflow_xr.attrs['featureType'] = 'timeSeries'
        return streamflow_xr


    def parse_setup(self):
        '''replace all tags in template with flag values'''
        text_header = self.template # this is a header only
        # first set header flags
        for key, value in self.flags.items():
            text_header = text_header.replace('$'+str(key)+'$',str(value))
        # next write gauge header lines from streamflow info
        gauge_headers = []
        for g in range(self.streamflow.dims['gauge']):
            gauge_info = self.streamflow.isel(gauge=g)
            wf_iy = str(gauge_info.lat.values)
            wf_jx = str(gauge_info.lon.values)
            wf_gage = str(gauge_info.id.values)
            line = "{}\t{}\t{:<12}".format(wf_iy,wf_jx,wf_gage[:12])
            gauge_headers.append(line)
        gauge_header = '\n'.join(gauge_headers)
        # last parse streamflow data
        streamflow_values = []
        for g in range(self.streamflow.dims['gauge']):
            gauge_info = self.streamflow.isel(gauge=g)
            streamflow_values.append(gauge_info.streamflow.values)
        dfs = pd.DataFrame(np.array(streamflow_values).transpose())
        stream_values_text = dfs.to_string(header=False,index=False)

        text = '\n'.join([text_header,gauge_header,stream_values_text])
        return text

    def write_ini_file(self):
        text = self.parse_setup()
        with open(self.inifilepath,'w') as setf:
            setf.write(text)

class MeshMinMaxParameterTxtFile():
    '''This file is recently included to check if parameter values lie within specified ranges 
    so as to avoid model crash problems that will be caused by unrealistic parameter values.

    This file is currently static
    '''
    def __init__(self,inifilepath) -> None:
        """Initialize file

        Parameters
        ----------
        inifilepath : str
            path to file to write
        """        
        self.inifilepath = inifilepath
        self.template = self.get_template()
        self.write_ini_file()
    
    def get_template(self):
        template = \
'''Reserved 1 - THEXTRA                               !ROW 1
0.0000                                             !min
0.0001                                             !max
Reserved 2 - ICE_INDEX                             !ROW 2
0.0000                                             !min
0.0001                                             !max
Reserved 3 - GWSCALE                               !ROW 3
0.0000                                             !min
0.0001                                             !max
River roughness factor (WF_R2) (5 classes maximum) !ROW 4
0.0200                                             !min
2.0000                                             !max
WF_R2 - CLASS 2                                    !ROW 5
0.0200                                             !min
2.0000                                             !max
WF_R2 - CLASS 3                                    !ROW 6
0.0200                                             !min
2.0000                                             !max
WF_R2 - CLASS 4                                    !ROW 7
0.0200                                             !min
2.0000                                             !max
WF_R2 - CLASS 5                                    !ROW 8
0.0200                                             !min
2.0000                                             !max
maximum soil porosity                              !ROW 9
0.0000                                             !min
1.0000                                             !max
depth from surface to bottom of rooting zone for maximum water holding capacity, m !ROW 10
0.0000                                             !min
4.1000                                             !max
Surface saturations [0.75 - 1.0]                   !ROW 11
0.0000                                             !min
1.0000                                             !max
Overnight minimum to cause ice lens after major melt -[50 - 0.0 �C] !ROW 12
-50.00                                             !min
0.0000                                             !max
DRNROW - DRAINAGE INDEX, CALCULATED DRAINAGE IS MULTIPLIED BY THIS VALUE                      !ROW 13
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min DRNROW
1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000   !max
SDEPROW - THE PERMEABLE DEPTH OF THE SOIL COLUMN                                              !ROW 14
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min SDEPROW
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
FAREROW - WHEN RUNNING A MOSAIC, THE FRACTIONAL AREA THAT THIS TILE REPRESENTS IN A GRID CELL !ROW 15
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min FAREROW
5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000   !max
DDENROW - THE DRAINAGE DENSITY OF THE GRU IN m/m2                                             !ROW 16
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min DDENROW
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
XSLPROW - AVERAGE OVERLAND SLOPE OF A GIVEN GRU                                               !ROW 17
0.0001 0.0001 0.0001 0.0001 0.0001 0.0001 0.0001 0.0001 0.0001 0.0001 0.0001 0.0001 0.0001 0.0001 0.0001 0.0001 0.0001 0.0001 0.0001 0.0001 0.0001 0.0001   !min XSLPROW
1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000   !max
XDNROW - HORIZONTAL CONDUCTIVITY AT A DEPTH OF h0 DIVIDED BY HORIZONTAL CONDUCTIVITY AT SURFACE !ROW 18
0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010   !min XDNROW
1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000   !max
MANNROW - MANNING ROUGHNESS COEFFICIENT                                                       !ROW 19
0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010 0.0010   !min MANNROW
2.0000 2.0000 2.0000 2.0000 2.0000 2.0000 2.0000 2.0000 2.0000 2.0000 2.0000 2.0000 2.0000 2.0000 2.0000 2.0000 2.0000 2.0000 2.0000 2.0000 2.0000 2.0000   !max
KSROW - HORIZONTAL CONDUCTIVITY AT SURFACE                                                    !ROW 20
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min KSROW
1.0200 1.0200 1.0200 1.0200 1.0200 1.0200 1.0200 1.0200 1.0200 1.0200 1.0200 1.0200 1.0200 1.0200 1.0200 1.0200 1.0200 1.0200 1.0200 1.0200 1.0200 1.0200   !max
SANDROW - PERCENTAGES OF SAND CONTENT OF SOIL LAYER 1                                         !ROW 21
-5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000   !min % OF SAND not organic in soil layer 1
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
CLAYROW - PERCENTAGES OF CLAY CONTENT OF SOIL LAYER 1                                         !ROW 22
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min % OF CLAY not organic or sand in soil layer 1
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
ORGMROW - PERCENTAGES OF ORGANIC MATTER OF SOIL LAYER 1                                       !ROW 23
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min % OF ORGANIC in soil layer 1
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
SANDROW - PERCENTAGES OF SAND CONTENT OF SOIL LAYER 2                                         !ROW 24
-5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000   !min % OF SAND not organic in soil layer 2
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
CLAYROW - PERCENTAGES OF CLAY CONTENT OF SOIL LAYER 2                                         !ROW 25
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min % OF CLAY not organic or sand in soil layer 2
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
ORGMROW - PERCENTAGES OF ORGANIC MATTER OF SOIL LAYER 2                                       !ROW 26
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min % OF ORGANIC in soil layer 2
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
SANDROW - PERCENTAGES OF SAND CONTENT OF SOIL LAYER 3                                         !ROW 27
-5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000 -5.000   !min % OF SAND not organic in soil layer 3
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
CLAYROW - PERCENTAGES OF CLAY CONTENT OF SOIL LAYER 3                                         !ROW 28
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min % OF CLAY not organic or sand in soil layer 3
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
ORGMROW - PERCENTAGES OF ORGANIC MATTER OF SOIL LAYER 3                                       !ROW 29
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min % OF ORGANIC in soil layer 3
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
ZSNLROW - LIMITING SNOW DEPTH BELOW WHICH COVERAGE IS < 100%                                  !ROW 30
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min ZSNLROW    **From MESH_parameters_hydrology.ini
5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000 5.0000   !max
ZPLSROW - MAXIMUM WATER PONDING DEPTH FOR SNOW-COVERED AREAS                                  !ROW 31
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min ZPLSROW
1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000   !max
ZPLGROW - MAXIMUM WATER PONDING DEPTH FOR SNOW-FREE AREAS                                     !ROW 32
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min ZPLGROW
1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000   !max
FZRCROW - COEFFICIENT FOR THE FROZEN SOIL INFILTRATION PARAMETERIC EQUATION                   !ROW 33
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min FZRCROW
3.0000 3.0000 3.0000 3.0000 3.0000 3.0000 3.0000 3.0000 3.0000 3.0000 3.0000 3.0000 3.0000 3.0000 3.0000 3.0000 3.0000 3.0000 3.0000 3.0000 3.0000 3.0000   !max
LNZ0ROW - NATURAL LOGARITHM OF THE ROUGHNESS LENGTH FOR LAND COVER CATEGORY 1                 !ROW 34
-20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00   !min LNZ0ROW1   Column 1 **Atmospheric parameters from MESH_parameters_CLASS.INI
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
ALVCROW - VISIBLE ALBEDO FOR LAND COVER CATEGORY 1                                            !ROW 35
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min ALVCROW1
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
ALICROW - NEAR INFRARED ALBEDO FOR LAND COVER CATEGORY 1                                      !ROW 36
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min ALICROW1
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
RSMNROW - MINIMUM STOMATAL RESISTANCE FOR THE VEGETATION TYPE 1                               !ROW 37
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min RSMNROW1
1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0   !max
VPDAROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO VAPOR PRESSURE DEFICIT - COMMON VALUE 0.5 !ROW 38
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min VPDAROW1
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
PSGAROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO SOIL WATER SUCTION -OMMON VALUE 100 !ROW 39
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min PSGAROW1
1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0   !max
LNZ0ROW - NATURAL LOGARITHM OF THE ROUGHNESS LENGTH FOR LAND COVER CATEGORY 2                 !ROW 40
-20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00   !min LNZ0ROW2   Column 2 **Atmospheric parameters from MESH_parameters_CLASS.INI
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
ALVCROW - VISIBLE ALBEDO FOR LAND COVER CATEGORY 2                                            !ROW 41
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min ALVCROW2
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
ALICROW - NEAR INFRARED ALBEDO FOR LAND COVER CATEGORY 2                                      !ROW 42
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min ALICROW2
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
RSMNROW - MINIMUM STOMATAL RESISTANCE FOR THE VEGETATION TYPE 2                               !ROW 43
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min RSMNROW2
1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0   !max
VPDAROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO VAPOR PRESSURE DEFICIT - COMMON VALUE 0.5 !ROW 44
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min VPDAROW2
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
PSGAROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO SOIL WATER SUCTION -OMMON VALUE 100 !ROW 45
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min PSGAROW2
1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0   !max
LNZ0ROW - NATURAL LOGARITHM OF THE ROUGHNESS LENGTH FOR LAND COVER CATEGORY 3                 !ROW 46
-20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00   !min LNZ0ROW3   Column 3 **Atmospheric parameters from MESH_parameters_CLASS.INI
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
ALVCROW - VISIBLE ALBEDO FOR LAND COVER CATEGORY 3                                            !ROW 47
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min ALVCROW3
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
ALICROW - NEAR INFRARED ALBEDO FOR LAND COVER CATEGORY 3                                      !ROW 48
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min ALICROW3
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
RSMNROW - MINIMUM STOMATAL RESISTANCE FOR THE VEGETATION TYPE 3                               !ROW 49
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min RSMNROW3
1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0   !max
VPDAROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO VAPOR PRESSURE DEFICIT - COMMON VALUE 0.5 !ROW 50
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min VPDAROW3
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
PSGAROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO SOIL WATER SUCTION -OMMON VALUE 100 !ROW 51
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min PSGAROW3
1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0   !max
LNZ0ROW - NATURAL LOGARITHM OF THE ROUGHNESS LENGTH FOR LAND COVER CATEGORY 4                 !ROW 52
-20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00   !min LNZ0ROW4   Column 4 **Atmospheric parameters from MESH_parameters_CLASS.INI
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
ALVCROW - VISIBLE ALBEDO FOR LAND COVER CATEGORY 4                                            !ROW 53
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min ALVCROW4
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
ALICROW - NEAR INFRARED ALBEDO FOR LAND COVER CATEGORY 4                                      !ROW 54
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min ALICROW4
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
RSMNROW - MINIMUM STOMATAL RESISTANCE FOR THE VEGETATION TYPE 4                               !ROW 55
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min RSMNROW4
1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0   !max
VPDAROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO VAPOR PRESSURE DEFICIT - COMMON VALUE 0.5 !ROW 56
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min VPDAROW4
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
PSGAROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO SOIL WATER SUCTION -OMMON VALUE 100 !ROW 57
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min PSGAROW4
1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0   !max
LNZ0ROW - NATURAL LOGARITHM OF THE ROUGHNESS LENGTH FOR LAND COVER CATEGORY 5                 !ROW 58
-20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00 -20.00   !min LNZ0ROW5   Column 5 **Atmospheric parameters from MESH_parameters_CLASS.INI
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
ALVCROW - VISIBLE ALBEDO FOR LAND COVER CATEGORY 5                                            !ROW 59
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min ALVCROW5
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
ALICROW - NEAR INFRARED ALBEDO FOR LAND COVER CATEGORY 5                                      !ROW 60
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min ALICROW5
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
LAMXROW - MAXIMUM LEAF AREA INDEX FOR THE VEGETATION TYPE 1                                   !ROW 61
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min LAMXROW1   Column 6
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
LAMNROW - MINIMUM LEAF AREA INDEX FOR THE VEGETATION TYPE 1                                   !ROW 62
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min LAMNROW1
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
CMASROW - ANNUAL MAXIMUM CANOPY MASS FOR VEGETATION TYPE 1 [kg m-2]                           !ROW 63
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min CMASROW1
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
ROOTROW - ROOTING DEPTH FOR VEGETATION TYPE 1                                                 !ROW 64
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min ROOTROW1
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
QA50ROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO LIGHT, COMMON VALUES - 30 TO 50 W/M2 !ROW 65
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min QA50ROW1
1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0   !max
VPDBROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO VAPOR PRESSURE DEFICIT, COMMON VALUES - 1.0 !ROW 66
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min VPDBROW1
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
PSGBROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO SOIL WATER SUCTION, COMMON VALUES - 5       !ROW 67
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min PSGBROW1
1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0   !max
LAMXROW - MAXIMUM LEAF AREA INDEX FOR THE VEGETATION TYPE 2                                   !ROW 68
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min LAMXROW2   Column 7
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
LAMNROW - MINIMUM LEAF AREA INDEX FOR THE VEGETATION TYPE 2                                   !ROW 69
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min LAMNROW2
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
CMASROW - ANNUAL MAXIMUM CANOPY MASS FOR VEGETATION TYPE 2 [kg m-2]                           !ROW 70
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min CMASROW2
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
ROOTROW - ROOTING DEPTH FOR VEGETATION TYPE 2                                                 !ROW 71
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min ROOTROW2
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
QA50ROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO LIGHT, COMMON VALUES - 30 TO 50 W/M2 !ROW 72
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min QA50ROW2
1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0   !max
VPDBROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO VAPOR PRESSURE DEFICIT, COMMON VALUES - 1.0 !ROW 73
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min VPDBROW2
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
PSGBROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO SOIL WATER SUCTION, COMMON VALUES - 5 !ROW 74
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min PSGBROW2
1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0   !max
LAMXROW - MAXIMUM LEAF AREA INDEX FOR THE VEGETATION TYPE 3                                   !ROW 75
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min LAMXROW3   Column 8
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
LAMNROW - MINIMUM LEAF AREA INDEX FOR THE VEGETATION TYPE 3                                   !ROW 76
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min LAMNROW3
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
CMASROW - ANNUAL MAXIMUM CANOPY MASS FOR VEGETATION TYPE 3 [kg m-2]                           !ROW 77
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min CMASROW3
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
ROOTROW - ROOTING DEPTH FOR VEGETATION TYPE 3                                                 !ROW 78
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min ROOTROW3
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
QA50ROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO LIGHT, COMMON VALUES - 30 TO 50 W/M2 !ROW 79
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min QA50ROW3
1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0   !max
VPDBROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO VAPOR PRESSURE DEFICIT, COMMON VALUES - 1.0 !ROW 80
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min VPDBROW3
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
PSGBROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO SOIL WATER SUCTION, COMMON VALUES - 5 !ROW 81
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min PSGBROW3
1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0   !max
LAMXROW - MAXIMUM LEAF AREA INDEX FOR THE VEGETATION TYPE 4                                   !ROW 82
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min LAMXROW4   Column 9
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
LAMNROW - MINIMUM LEAF AREA INDEX FOR THE VEGETATION TYPE 4                                   !ROW 83
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min LAMNROW4
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
CMASROW - ANNUAL MAXIMUM CANOPY MASS FOR VEGETATION TYPE 4 [kg m-2]                           !ROW 84
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min CMASROW4
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
ROOTROW - ROOTING DEPTH FOR VEGETATION TYPE 4                                                 !ROW 85
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min ROOTROW4
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
QA50ROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO LIGHT, COMMON VALUES - 30 TO 50 W/M2 !ROW 86
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min QA50ROW4
1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0   !max
VPDBROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO VAPOR PRESSURE DEFICIT, COMMON VALUES - 1.0 !ROW 87
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min VPDBROW4
100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00 100.00   !max
PSGBROW - COEFFICIENT GOVERNING THE RESPONSE OF STOMATES TO SOIL WATER SUCTION, COMMON VALUES - 5       !ROW 88
0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000   !min PSGBROW4
1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0 1000.0   !max
'''
        return template

    def parse_setup(self):
        return self.template

    def write_ini_file(self):
        text = self.parse_setup()
        with open(self.inifilepath,'w') as setf:
            setf.write(text)

class MeshParameterTxtFile():
    '''MESH_parameters.txt is an optional input file, which can be used 
    to replace the traditional INI format parameter files, and allows 
    specifying additional parameters, variables, and options not 
    supported by the legacy file formats. The file uses free-formatting, 
    allows block and in-line comments, and uses a generalized structure 
    for greater flexibility, which includes the use of names to identify 
    parameters, variables, and options.

    The structure of MESH_parameters.txt is free-format and does not contain 
    identified sections. Parameters, variables, and options are listed by line, 
    with corresponding values and settings listed in the same line as the 
    parameter, variable, or option name key.
    '''
    def __init__(self,inifilepath,parameter_values=None) -> None:
        """Initialize file

        Parameters
        ----------
        inifilepath : str
            path to file to write
        parameter_values: pandas.core.frame.DataFrame
            parameter values. First column VARIABLE NAMES, second column (or more) VARIABLE values
            comments can be added by adding '!>' as Variable name. 
            No values should be '' and example is:
            pardf = pd.DataFrame(
                    np.array([['!>','PARA','PARB','!>','PARC'],
                    ['test comment',32,0.45,'comment two','txt'],
                    ['','','0.8','','']]).transpose()
                    )
        """        
        self.inifilepath = inifilepath
        if isinstance(parameter_values,pd.core.frame.DataFrame):
            self.flags = parameter_values
            print('Parameter values read from input')
        else:
            self.flags = self.set_dummy_content()
            print('No parameter values read - create dummy file')

        self.write_ini_file()

    def set_dummy_content(self):
        pardf = pd.DataFrame(np.array(
            [['!>','!>'],
            ['No parameters given','Dummy file generated']]).transpose()
                )
        return pardf
    
    def parse_setup_dict(self):
        # start with header
        comment_parameter_lines = ['!> TXT (free-format) MESH configuration file.']
        for parameter, valcom in self.flags.items():
            # check if comment is included
            if isinstance(valcom,tuple):
                # change type to list, to have uniform behavior 
                # for single values and lists
                value = list(valcom[0])
                # next try for comment
                comment = valcom[1]
                comment_line = '!>\t{}'.format(comment)
                comment_parameter_lines.append(comment_line)
            else:
                value = list(valcom)
            value_line = '{}\t{}'.format(parameter,'\t'.join([str(v) for v in value]))
            comment_parameter_lines.append(value_line)
        text = '\n'.join(comment_parameter_lines)

        return text

    def parse_setup_df(self):
        text_header = '!> TXT (free-format) MESH configuration file.\n'
        par_text = self.flags.to_string(header=False,index=False,justify='left')
        return text_header + par_text

    def write_ini_file(self):
        text = self.parse_setup_df()
        with open(self.inifilepath,'w') as setf:
            setf.write(text)


class MeshOutputTxtFile():
    pass