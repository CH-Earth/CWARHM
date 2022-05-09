
import netCDF4 as nc4
from pathlib import Path
import time, os
import math
import cdsapi    # copernicus connection
import calendar  # to find days per month
import os        # to check if file already exists
from pathlib import Path
from shutil import copyfile
from datetime import datetime
import multiprocessing

from cwarhm.util.util import run_in_parallel


def round_coords_to_ERA5(coords):
    """Round bounding box coordinates to ERA5 resolution

    Note
    ----
    from CWARHM by Wouter Knoben
    https://github.com/CH-Earth/CWARHM/blob/bdd5c388b7f307c6afe1228d4606c6a706fba9d7/3a_forcing/1a_download_forcing/download_ERA5_pressureLevel_annual.py#L29


    Parameters
    ----------
    coords : list
        Coordinates in the format [lat_max,lon_min,lat_min,lon_max]

    Returns
    -------
    dl_string : str
        rounded coordinates in format '{lat_min}/{lon_max}/{lat_max}/{lon_min}'
    rounded_lat : list
        [lat_max,lat_min]
    rounded_lon : list
        [lon_max,lon_min]
    
    """    
    # Extract values
    lon = [coords[1],coords[3]]
    lat = [coords[2],coords[0]]
    
    # Round to ERA5 0.25 degree resolution
    rounded_lon = [math.floor(lon[0]*4)/4, math.ceil(lon[1]*4)/4]
    rounded_lat = [math.floor(lat[0]*4)/4, math.ceil(lat[1]*4)/4]
    
    # Find if we are still in the representative area of a different ERA5 grid cell
    if lat[0] > rounded_lat[0]+0.125:
        rounded_lat[0] += 0.25
    if lon[0] > rounded_lon[0]+0.125:
        rounded_lon[0] += 0.25
    if lat[1] < rounded_lat[1]-0.125:
        rounded_lat[1] -= 0.25
    if lon[1] < rounded_lon[1]-0.125:
        rounded_lon[1] -= 0.25
    
    # Make a download string
    dl_string = '{}/{}/{}/{}'.format(rounded_lat[1],rounded_lon[0],rounded_lat[0],rounded_lon[1])
    
    return dl_string, rounded_lat, rounded_lon

def generate_download_requests(year,bbox,path_to_save_data,target_dataset):
    """Generate cdsapi requests for one year of ERA5 data in monthly chunks.

    The request list can be downloaded by using :func:wait_for_and_download_requests .
    The variables requested are the variables needed to run a land-surface scheme
    (e.g. SUMMA / CLASS / MESH).



    Note
    ----
    Using the download function requires acces to cdsapi:
    - Registration: https://cds.climate.copernicus.eu/user/register?destination=%2F%23!%2Fhome
    - Setup of the `cdsapi`: https://cds.climate.copernicus.eu/api-how-to

    Adapted from CWARHM by Wouter Knoben
    https://github.com/CH-Earth/CWARHM/blob/bdd5c388b7f307c6afe1228d4606c6a706fba9d7/3a_forcing/1a_download_forcing/download_ERA5_pressureLevel_annual.py#L29

    and example from ECMWF
    https://github.com/ecmwf/cdsapi/blob/master/examples/example-era5-update.py

    Requesting the parameters from the pressure_level takes a long time (days rather 
    than hours) because those parameters are stored on slow storage at ECMWF.

    Parameters
    ----------
    year : int
        year to download e.g. 2002
    bbox : list
        list of bounding box coordinates [lat_max,lon_min,lat_min,lon_max]
    path_to_save_data : str
        path to folder to save data in
    target_dataset : str
        either 'pressure_level' or 'surface_level'
    
    Returns
    -------
    request_list : list
        list with cdsapi requests
    download_list : list
        list of path destinations for downloads
    """   
    download_list = []
    request_list = []
    # Find the rounded bounding box
    coordinates,_,_ = round_coords_to_ERA5(bbox)
    # connect to Copernicus (requires .cdsapirc file in $HOME)
    c = cdsapi.Client(debug=True, wait_until_complete=False)
    # --- Start the month loop
    for month in range(1,13): # this loops through numbers 1 to 12
       
        # find the number of days in this month
        daysInMonth = calendar.monthrange(year,month) 
            
        # compile the date string in the required format. Append 0's to the month number if needed (zfill(2))
        date = str(year) + '-' + str(month).zfill(2) + '-01/' + \
            str(year) + '-' + str(month).zfill(2) + '-' + str(daysInMonth[1]).zfill(2) 
            
        # compile the file name string
        file_path = os.path.join(path_to_save_data,('ERA5_{}_'.format(target_dataset) + str(year) + str(month).zfill(2) + '.nc'))

        # track progress
        print('Trying to download ' + date + ' into ' + str(file_path))

        # if file doesn't yet exist, download the data
        if not os.path.isfile(file_path):

            # Make sure the connection is re-tried if it fails
            retries_max = 1
            retries_cur = 1
            while retries_cur <= retries_max:
                try:
                    # specify and request data
                    if target_dataset == 'pressure_level':
                        request_list.append(
                        c.retrieve('reanalysis-era5-complete', {    # do not change this!
                            'class': 'ea',
                            'expver': '1',
                            'stream': 'oper',
                            'type': 'an',
                            'levtype': 'ml',
                            'levelist': '137',
                            'param': '130/131/132/133',
                            'date': date,
                            'time': '00/to/23/by/1',
                            'area': coordinates,
                            'grid': '0.25/0.25', # Latitude/longitude grid: east-west (longitude) and north-south resolution (latitude).
                            'format'  : 'netcdf',
                        },)
                        )
                        download_list.append(file_path)

                    elif target_dataset == 'surface_level':
                        request_list.append(
                        c.retrieve('reanalysis-era5-single-levels',{
                                'product_type': 'reanalysis',
                                'format': 'netcdf',
                                'variable': [
                                    '10m_u_component_of_wind',
                                    '10m_v_component_of_wind',
                                    '2m_dewpoint_temperature',
                                    '2m_temperature',
                                    'mean_surface_downward_long_wave_radiation_flux',                
                                    'mean_surface_downward_short_wave_radiation_flux',
                                    'mean_total_precipitation_rate', 
                                    'surface_pressure',
                                ],
                                'date': date,
                                'time': '00/to/23/by/1',
                                'area': coordinates,	# North, West, South, East. Default: global
                                'grid': '0.25/0.25',    # Latitude/longitude grid: east-west (longitude) and north-south
                            },
                            ))
                        download_list.append(file_path) # file path and name
                    else:
                        print('No valid target. Target is either surface_level or pressure_level')
                

                except Exception as e:
                    print('Error creating request ' + str(file_path) + ' on try ' + str(retries_cur))
                    print(str(e))
                    retries_cur += 1
                    continue
                else:
                    break
    return request_list, download_list

def wait_for_and_download_requests(req_list,download_paths,sleep=30):
    """loop over cdsapi request list and download when ready

    Will end when all downloads are completed

    Parameters
    ----------
    req_list : list
        list of cdsapir requests (from :func:generate_download_requests)
    download_paths : list
        list of target file paths matching requests
    sleep : int, optional
        time to wait in seconds before checking, by default 30
    """
    # initialize all requests as queued
    conditions = ["queued"]*len(req_list)
    while any(element in ("queued", "running") for element in conditions):
        for i,r in enumerate(req_list):
            #sleep = 30
            r.update()
            reply = r.reply
            # this is logging
            r.info("Request ID: %s, state: %s" % (reply["request_id"], reply["state"]))
            # change state
            conditions[i]=reply["state"]

            if reply["state"] == "completed":
                print('start download {}'.format(download_paths[i]))
                r.download(download_paths[i])
                print('done downloading {}'.format(download_paths[i]))
                conditions[i]="downloaded"
            elif reply["state"] in ("queued", "running"):
                r.info("Request ID: %s, sleep: %s", reply["request_id"], sleep)
            elif reply["state"] in ("failed",):
                r.error("Message: %s", reply["error"].get("message"))
                r.error("Reason:  %s", reply["error"].get("reason"))
        time.sleep(sleep)
    # delete requests
    for i,r in enumerate(req_list):
        r.delete()        

def download_one_era5_year(year,bbox,path_to_save_data,target_dataset):
    """Download one year of ERA5 data in monthly chunks.

    Note
    ----
    Adapted from CWARHM by Wouter Knoben
    https://github.com/CH-Earth/CWARHM/blob/bdd5c388b7f307c6afe1228d4606c6a706fba9d7/3a_forcing/1a_download_forcing/download_ERA5_pressureLevel_annual.py#L29

    Parameters
    ----------
    year : int
        year to download e.g. 2002
    bbox : list
        list of bounding box coordinates [lat_max,lon_min,lat_min,lon_max]
    path_to_save_data : str
        path to folder to save data in
    target_dataset : str
        either 'pressure_level' or 'surface_level'
    """   
    # Find the rounded bounding box
    coordinates,_,_ = round_coords_to_ERA5(bbox)
    # --- Start the month loop
    for month in range (1,13): # this loops through numbers 1 to 12
       
        # find the number of days in this month
        daysInMonth = calendar.monthrange(year,month) 
            
        # compile the date string in the required format. Append 0's to the month number if needed (zfill(2))
        date = str(year) + '-' + str(month).zfill(2) + '-01/' + \
            str(year) + '-' + str(month).zfill(2) + '-' + str(daysInMonth[1]).zfill(2) 
            
        # compile the file name string
        file_path = os.path.join(path_to_save_data,('ERA5_{}_'.format(target_dataset) + str(year) + str(month).zfill(2) + '.nc'))

        # track progress
        print('Trying to download ' + date + ' into ' + str(file_path))

        # if file doesn't yet exist, download the data
        if not os.path.isfile(file_path):

            # Make sure the connection is re-tried if it fails
            retries_max = 1
            retries_cur = 1
            while retries_cur <= retries_max:
                try:

                    # connect to Copernicus (requires .cdsapirc file in $HOME)
                    c = cdsapi.Client()

                    # specify and retrieve data
                    if target_dataset == 'pressure_level':
                        c.retrieve('reanalysis-era5-complete', {    # do not change this!
                            'class': 'ea',
                            'expver': '1',
                            'stream': 'oper',
                            'type': 'an',
                            'levtype': 'ml',
                            'levelist': '137',
                            'param': '130/131/132/133',
                            'date': date,
                            'time': '00/to/23/by/1',
                            'area': coordinates,
                            'grid': '0.25/0.25', # Latitude/longitude grid: east-west (longitude) and north-south resolution (latitude).
                            'format'  : 'netcdf',
                        }, file_path)

                    elif target_dataset == 'surface_level':
                        c.retrieve('reanalysis-era5-single-levels',{
                                'product_type': 'reanalysis',
                                'format': 'netcdf',
                                'variable': [
                                    'mean_surface_downward_long_wave_radiation_flux',                
                                    'mean_surface_downward_short_wave_radiation_flux',
                                    'mean_total_precipitation_rate', 
                                    'surface_pressure',
                                ],
                                'date': date,
                                'time': '00/to/23/by/1',
                                'area': coordinates,	# North, West, South, East. Default: global
                                'grid': '0.25/0.25',    # Latitude/longitude grid: east-west (longitude) and north-south
                            },
                            file_path) # file path and name
                    else:
                        print('No valid target. Target is either surface_level or pressure_level')
                
                    # track progress
                    print('Successfully downloaded ' + str(file_path))

                except Exception as e:
                    print('Error downloading ' + str(file_path) + ' on try ' + str(retries_cur))
                    print(str(e))
                    retries_cur += 1
                    continue
                else:
                    break

def run_era5_download_in_parallel(years,bbox,path_to_save_data,target_dataset):
    """Run download_one_era5_year in parallel

    Parameters
    ----------
    years : list
        years to download e.g. [2002,2003,2004]
    bbox : list
        list of bounding box coordinates [lat_max,lon_min,lat_min,lon_max]
    path_to_save_data : str
        path to folder to save data in
    target_dataset : str
        either 'pressure_level' or 'surface_level'
    """    
    pool = multiprocessing.Pool()
    outputs = [pool.apply_async(download_one_era5_year, args=(year, bbox, path_to_save_data, target_dataset)) for year in years]
    print(outputs)
    pool.close()

def merge_era5_surface_and_pressure_level_downloads(forcingPath, mergePath, years_str):
    """Combine separate surface and pressure level downloads
    Creates a single monthly `.nc` file with SUMMA-ready variables for further processing. # Combines ERA5's `u` and
    `v` wind components into a single directionless wind vector.

    Note
    ----
    This function is no longer needed as merging is more effective using xarray

    :param forcingPath: path to raw ERA5 surface and pressure level data
    :param mergePath: path to save merged ERA5 data
    :param year_str: start,end year string from control file (e.g., "2008,2013")
    """

    # processing
    years = [int(s) for s in years_str.split(',')]
    forcingPath = Path(forcingPath)
    mergePath = Path(mergePath)
    os.makedirs(mergePath, exist_ok=True)

    # --- Merge the files
    # Loop through all years and months
    for year in range(years[0] ,years[1 ] +1):
        for month in range (1 ,13):

            # Define file names
            data_pres = 'ERA5_pressureLevel137_' + str(year) + str(month).zfill(2) + '.nc'
            data_surf = 'ERA5_surface_' + str(year) + str(month).zfill(2) + '.nc'
            data_dest = 'ERA5_merged_' + str(year) + str(month).zfill(2) + '.nc'

            # Step 1: convert lat/lon in the pressure level file to range [-180,180], [-90,90]
            # Extract the variables we need for the similarity check in a way that closes the files implicitly
            with nc4.Dataset(forcingPath / data_pres) as src1, nc4.Dataset(forcingPath / data_surf) as src2:
                pres_lat = src1.variables['latitude'][:]
                pres_lon = src1.variables['longitude'][:]
                pres_time = src1.variables['time'][:]
                surf_lat = src2.variables['latitude'][:]
                surf_lon = src2.variables['longitude'][:]
                surf_time = src2.variables['time'][:]

            # Update the pressure level coordinates
            pres_lat[pres_lat > 90] = pres_lat[pres_lat > 90] - 180
            pres_lon[pres_lon > 180] = pres_lon[pres_lon > 180] - 360

            # Step 2: check that coordinates and time are the same between the both files
            # Compare dimensions (lat, long, time)
            flag_loc_and_time_same = [all(pres_lat == surf_lat), all(pres_lon == surf_lon), all(pres_time == surf_time)]

            # Check that they are all the same
            if not all(flag_loc_and_time_same):
                err_txt = 'Dimension mismatch while merging ' + data_pres + ' and ' + data_surf + '. Check latitude, longitude and time dimensions in both files. Continuing with next files.'
                print(err_txt)
                continue

            # Step 3: combine everything into a single .nc file
            # Order of writing things:
            # - Meta attributes from both source files
            # - Dimensions (lat, lon, time)
            # - Variables: long, lat and time
            # - Variables: forcing at surface
            # - Variables: forcing at pressure level 137

            # Define the variables we want to transfer
            variables_surf_transfer = ['longitude' ,'latitude' ,'time']
            variables_surf_convert = ['sp' ,'mtpr' ,'msdwswrf' ,'msdwlwrf']
            variables_pres_convert = ['t' ,'q']
            attr_names_expected = ['scale_factor' ,'add_offset' ,'_FillValue' ,'missing_value' ,'units' ,'long_name'
                                   ,'standard_name'] # these are the attributes we think each .nc variable has
            loop_attr_copy_these = ['units' ,'long_name'
                                    ,'standard_name'] # we will define new values for _FillValue and missing_value when writing the .nc variables' attributes

            # Open the destination file and transfer information
            with nc4.Dataset(forcingPath / data_pres) as src1, nc4.Dataset(forcingPath / data_surf) as src2, nc4.Dataset \
                    (mergePath / data_dest, "w") as dest:

                # === Some general attributes
                dest.setncattr('History' ,'Created ' + time.ctime(time.time()))
                dest.setncattr('Language' ,'Written using Python')
                dest.setncattr('Reason'
                               ,'(1) ERA5 surface and pressure files need to be combined into a single file (2) Wind speed U and V components need to be combined into a single vector (3) Forcing variables need to be given to SUMMA without scale and offset')

                # === Meta attributes from both sources
                for name in src1.ncattrs():
                    dest.setncattr(name + ' (pressure level (10m) data)', src1.getncattr(name))
                for name in src2.ncattrs():
                    dest.setncattr(name + ' (surface level data)', src1.getncattr(name))

                # === Dimensions: latitude, longitude, time
                # NOTE: we can use the lat/lon from the surface file (src2), because those are already in proper units. If there is a mismatch between surface and pressure we shouldn't have reached this point at all due to the check above
                for name, dimension in src2.dimensions.items():
                    if dimension.isunlimited():
                        dest.createDimension( name, None)
                    else:
                        dest.createDimension( name, len(dimension))

                # === Get the surface level generic variables (lat, lon, time)
                for name, variable in src2.variables.items():

                    # Transfer lat, long and time variables because these don't have scaling factors
                    if name in variables_surf_transfer:
                        dest.createVariable(name, variable.datatype, variable.dimensions, fill_value = -999)
                        dest[name].setncatts(src1[name].__dict__)
                        dest.variables[name][:] = src2.variables[name][:]

                # === For the forcing variables, we need to:
                # 1. Extract them (this automatically applies scaling and offset with nc4) and apply non-negativity constraints
                # 2. Create a .nc variable with the right SUMMA name and file type
                # 3. Put all data into the new .nc file

                # ===  Transfer the surface level data first, for no particular reason
                # This should contain surface pressure (sp), downward longwave (msdwlwrf), downward shortwave (msdwswrf) and precipitation (mtpr)
                for name, variable in src2.variables.items():

                    # Check that we are only using the names we expect, and thus the names for which we have the required code ready
                    if name in variables_surf_convert:

                        # 0. Reset the dictionary that we keep attribute values in
                        loop_attr_source_values = {name: 'n/a' for name in attr_names_expected}

                        # 1a. Get the values of this variable from the source (this automatically applies scaling and offset)
                        loop_val = variable[:]

                        # 1b. Apply non-negativity constraint. This is intended to remove very small negative data values that sometimes occur
                        loop_val[loop_val < 0] = 0

                        # 1c. Get the attributes for this variable from source
                        for attrname in variable.ncattrs():
                            loop_attr_source_values[attrname] = variable.getncattr(attrname)

                        # 2a. Find what this ERA5 variable should be called in SUMMA
                        if name == 'sp':
                            name_summa = 'airpres'
                        elif name == 'msdwlwrf':
                            name_summa = 'LWRadAtm'
                        elif name == 'msdwswrf':
                            name_summa = 'SWRadAtm'
                        elif name == 'mtpr':
                            name_summa = 'pptrate'
                        else:
                            name_summa = 'n/a/' # no name so we don't start overwriting data if a new name is not defined for some reason

                        # 2b. Create the .nc variable with the proper SUMMA name
                        # Inputs: variable name as needed by SUMMA; data type: 'float'; dimensions; no need for fill value, because thevariable gets populated in this same script
                        dest.createVariable(name_summa, 'f4', ('time' ,'latitude' ,'longitude'), fill_value = False)

                        # 3a. Select the attributes we want to copy for this variable, based on the dictionary defined before the loop starts
                        loop_attr_copy_values = {use_this: loop_attr_source_values[use_this] for use_this in loop_attr_copy_these}

                        # 3b. Copy the attributes FIRST, so we don't run into any scaling/offset issues
                        dest[name_summa].setncattr('missing_value' ,-999)
                        dest[name_summa].setncatts(loop_attr_copy_values)

                        # 3c. Copy the data SECOND
                        dest[name_summa][:] = loop_val

                # === Transfer the pressure level variables next, using the same procedure as above
                for name, variable in src1.variables.items():
                    if name in variables_pres_convert:

                        # 0. Reset the dictionary that we keep attribute values in
                        loop_attr_source_values = {name: 'n/a' for name in attr_names_expected}

                        # 1a. Get the values of this variable from the source (this automatically applies scaling and offset)
                        loop_val = variable[:]

                        # 1b. Get the attributes for this variable from source
                        for attrname in variable.ncattrs():
                            loop_attr_source_values[attrname] = variable.getncattr(attrname)

                        # 2a. Find what this ERA5 variable should be called in SUMMA
                        if name == 't':
                            name_summa = 'airtemp'
                        elif name == 'q':
                            name_summa = 'spechum'
                        elif name == 'u':
                            name_summa = 'n/a/' # we shouldn't reach this part of the code, because 'u' is not specified in 'variables_pres_convert'
                        elif name == 'v':
                            name_summa = 'n/a' # as with 'u', because both are needed to calculate total wind speed first
                        else:
                            name_summa = 'n/a/' # no name so we don't start overwriting data if a new name is not defined for some reason

                        # 2b. Create the .nc variable with the proper SUMMA name
                        # Inputs: variable name as needed by SUMMA; data type: 'float'; dimensions; no need for fill value, because thevariable gets populated in this same script
                        dest.createVariable(name_summa, 'f4', ('time' ,'latitude' ,'longitude'), fill_value = False)

                        # 3a. Select the attributes we want to copy for this variable, based on the dictionary defined before the loop starts
                        loop_attr_copy_values = {use_this: loop_attr_source_values[use_this] for use_this in loop_attr_copy_these}

                        # 3b. Copy the attributes FIRST, so we don't run into any scaling/offset issues
                        dest[name_summa].setncattr('missing_value' ,-999)
                        dest[name_summa].setncatts(loop_attr_copy_values)

                        # 3c. Copy the data SECOND
                        dest[name_summa][:] = loop_val

                # === Calculate combined wind speed and store
                # 1a. Get the values of this variable from the source (this automatically applies scaling and offset)
                pres_u = src1.variables['u'][:]
                pres_v = src1.variables['v'][:]

                # 1b. Create the variable attribute 'units' from the source data. This lets us check if the source units match (they should match)
                unit_u = src1.variables['u'].getncattr('units')
                unit_v = src1.variables['v'].getncattr('units')
                unit_w = '(({})**2 + ({})**2)**0.5'.format(unit_u ,unit_v)

                # 2a. Set the summa_name
                name_summa = 'windspd'

                # 2b. Create the .nc variable with the proper SUMMA name
                # Inputs: variable name as needed by SUMMA; data type: 'float'; dimensions; no need for fill value, because thevariable gets populated in this same script
                dest.createVariable(name_summa ,'f4' ,('time' ,'latitude' ,'longitude') ,fill_value = False)

                # 3a. Set the attributes FIRST, so we don't run into any scaling/offset issues
                dest[name_summa].setncattr('missing_value' ,-999)
                dest[name_summa].setncattr('units' ,unit_w)
                dest[name_summa].setncattr('long_name'
                                           ,'wind speed at the measurement height, computed from ERA5 U and V-components')
                dest[name_summa].setncattr('standard_name' ,'wind_speed')

                # 3b. Copy the data SECOND
                # Creating a new variable first and writing to .nc later seems faster than directly writing to .nc
                pres_w = ((pres_u**2)+(pres_v**2))**0.5
                dest[name_summa][:] = pres_w

            print('Finished merging {} and {} into {}'.format(data_surf ,data_pres ,data_dest))
