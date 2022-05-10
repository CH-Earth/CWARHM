from pathlib import Path
import numpy as np
import requests
import shutil
import os
from osgeo import gdal
import glob
import tarfile

def all_merit_variables():
    """Returns a list of all MERIT variables

    :return: List of all MERIT variables available for download
    :rtype: List
    """
    return ['dir','elv','upa','upg','wth','hnd']

def download_merit(target_folder,credentials: dict,variables=['elv'],bbox: list=None,retries_max=10,
                    merit_url='http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_Hydro/distribute/v1.0.1/'):
    """Downloads MERIT data from source. Adapted from CWARHM (Knoben et Al., 2022).

    :param target_folder: root of target folder to save dowloaded MERIT data
    :type target_folder: string
    :param credentials: credentials to download MERIT data of the form dict(user='user',pass='pass') 
    :type credentials: dict
    :param variables: List of variables to download, defaults to ['elv']
    :type variables: list, optional
    :param bbox: bounding box in lat,lon to download subsection of spatial extent [xmin,ymin,xmax,ymax], defaults to None
    :type bbox: list, optional
    :param retries_max: number of retries for downloading a file, defaults to 10
    :type retries_max: int, optional
    :param merit_url: base url of download source, defaults to 'http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_Hydro/distribute/v1.0.1/'
    :type merit_url: str, optional
    """

    # define all possible variables
    if variables=='all':
        variables=all_merit_variables()

    # Define the edges of the download areas
    lon_right_edge  = np.array([-150,-120, -90,-60,-30,  0,30,60,90,120,150,180])
    lon_left_edge   = np.array([-180,-150,-120,-90,-60,-30, 0,30,60, 90,120,150])
    lat_bottom_edge = np.array([-60,-30,0, 30,60]) # NOTE: latitudes -90 to -60 are NOT part of the MERIT domain
    lat_top_edge    = np.array([-30,  0,30,60,90])
    # list all the tile combinations
    dl_lon_all = np.array(['w180','w150','w120','w090','w060','w030','e000','e030','e060','e090','e120','e150'])
    dl_lat_all = np.array(['s60','s30','n00','n30','n60'])

    if bbox:
        domain_min_lon = np.array(float(bbox[0])) #xmin
        domain_min_lat = np.array(float(bbox[1])) #ymin
        domain_max_lon = np.array(float(bbox[2])) #xmax
        domain_max_lat = np.array(float(bbox[3])) #ymax

        # Find the lower-left corners of each download square
        dl_lons = dl_lon_all[(domain_min_lon < lon_right_edge) & (domain_max_lon > lon_left_edge)]
        dl_lats = dl_lat_all[(domain_min_lat < lat_top_edge) & (domain_max_lat > lat_bottom_edge)]
        
    else:
        dl_lons = dl_lon_all
        dl_lats = dl_lat_all
    print('dl_lons: {} | dl_lats: {}'.format(dl_lons,dl_lats) )
    # Loop over the download files
    for variable in variables:
        print('downloading variable {}'.format(variable))
        for dl_lon in dl_lons:
            print('for tile lon {}'.format(dl_lon))
            for dl_lat in dl_lats:
                print('and tile lat {}'.format(dl_lat))
                # Skip those combinations for which no MERIT data exists
                if (dl_lat == 'n00' and dl_lon == 'w150') or \
                (dl_lat == 's60' and dl_lon == 'w150') or \
                (dl_lat == 's60' and dl_lon == 'w120'):
                    continue

                # Make the download URL
                file_url = (merit_url + '{}_{}{}.tar').format(variable,dl_lat,dl_lon)
        
                # Extract the filename from the URL
                file_name = file_url.split('/')[-1].strip() # Get the last part of the url, strip whitespace and characters
                # set full download file target path
                target_dir = Path(target_folder+'/{}/'.format(variable))
                target_dir.mkdir(parents=True,exist_ok=True)
                target_path = Path(target_folder+'/{}/'.format(variable)+file_name)
                # If file already exists in destination, move to next file
                if os.path.isfile(target_path):
                    print('{} already exist, skipping download'.format(target_path))
                    continue
                # Make sure the connection is re-tried if it fails
                retries_cur = 1
                while retries_cur <= retries_max:
                    try: 

                        # Send a HTTP request to the server and save the HTTP response in a response object called resp
                        # 'stream = True' ensures that only response headers are downloaded initially (and not all file contents too, which are 2GB+)
                        with requests.get(file_url.strip(), auth=(credentials['user'],credentials['pass']), stream=True) as response:
            
                            # Decode the response
                            response.raw.decode_content = True
                            content = response.raw
            
                            # Write to file
                            with open(target_path, 'wb') as data:
                                shutil.copyfileobj(content, data)

                            # print a completion message
                            print('Successfully downloaded {}'.format(target_path))
                            break
                    except Exception as e:
                        print('Error downloading ' + file_url + ' on try ' + str(retries_cur) + ' with error: ' + str(e))
                        retries_cur += 1
                        continue
                    else:
                        break

def extract_merit_tars(data_path,extracted_path,variables=['']):
    """Extract MERIT zipped data downloaded by download_merit

    :param data_path: root path to MERIT data
    :type data_path: string
    :param extracted_path: root path to extracted MERIT data to
    :type extracted_path: string
    :param variables: List of variables to extract. 'all' will generate a list of all the MERIT variables, defaults to ['']
    :type variables: list, optional
    """
    # define all possible variables
    if variables=='all':
        variables=all_merit_variables()
    print('variables to extract are {}'.format(variables))
    # loop over variables
    for variable in variables:
        print('extracting variable {}'.format(variable))
        # set variable as folder for extracted files
        extracted_path_variable = Path(extracted_path+'/'+variable)
        # make folder if does not exist
        extracted_path_variable.mkdir(parents=True,exist_ok=True)
        # list all tarfiles
        tarfiles = glob.glob(data_path+'/{}*/'.format(variable)+'/*.tar')
        print(tarfiles)
        # loop over all tarfiles and extract
        for tar_file in tarfiles:
            with tarfile.open(tar_file) as my_tar:
                my_tar.extractall(extracted_path_variable)

def build_merit_vrt(data_path_in, vrt_out_dir, variables=[''], **build_options):
    """Build gdal virtual data set (vrt) from extracted MERIT variables.

    :param data_path_in: Root path of extracted MERIT data
    :type data_path_in: string
    :param vrt_out_dir: Root path to save vrts to
    :type vrt_out_dir: string
    :param variables: List of MERIT variables to build vrt for, defaults to ['']. 'all' generates a list of all MERIT variables
    :type variables: list, optional
    """
    # define all possible variables
    if variables=='all':
        variables=all_merit_variables()
    print('variables to process vrt: {}'.format(variables))
    for variable in variables:

        # set list of files to make into vrt
        tifslist = glob.glob(data_path_in+'/{}*/'.format(variable)+'/*/'+'*.tif')
        print(tifslist)
        # construct vrt out path
        vrt_out = vrt_out_dir+'/{}/'.format(variable)+'/{}.vrt'.format(variable)
        # Make folder structure for vrt_out
        vrt_dir= Path(os.path.dirname(vrt_out))
        vrt_dir.mkdir(parents=True,exist_ok=True)
        print('result saved as {}'.format(vrt_out))
        # execute gdal build to make vrt
        vrt_options = gdal.BuildVRTOptions(**build_options) 
        my_vrt = gdal.BuildVRT(vrt_out, tifslist, options=vrt_options)
        my_vrt.FlushCache()



credentials = dict(user='hydrography',password='rivernetwork') 

#test bow at banff download_merit('/Users/ayx374/data/merit_hydro',credentials,bbox=[-116.55,50.95,-115.52,51.74])
#download_merit('/home/ayx374/projects/rpp-kshook/CompHydCore/merit_hydro/raw_data',credentials,variables='all')
#extract_merit_tars('/home/ayx374/projects/rpp-kshook/CompHydCore/merit_hydro/raw_data','/home/ayx374/projects/rpp-kshook/CompHydCore/merit_hydro/extracted',variables='all')
#build_merit_vrt('/home/ayx374/projects/rpp-kshook/CompHydCore/merit_hydro/extracted','/home/ayx374/projects/rpp-kshook/CompHydCore/merit_hydro/vrts',variables='all',resolution='highest')