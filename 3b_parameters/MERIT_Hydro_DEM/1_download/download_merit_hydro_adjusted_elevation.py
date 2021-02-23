# Script to download the MERIT DEM data
# Source: http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_DEM/index.html
#
# Note: this requires the user to be registered, which can be done through the website

# modules
import requests
import os  

# login details
user = 'hydrography'
login = 'rivernetwork'

# Locations
loc_src = 'http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_Hydro/distribute/v1.0/'
loc_des = '/project/6008034/Model_Output/ClimateForcingData/MERIT_Hydro_adjusted_elevation_raw/'

# Check if the destination directory exists and create it if not
if not os.path.exists(loc_des):
    os.makedirs(loc_des)

# specify a list of files to download
file_list = ['elv_n60w180.tar',
             'elv_n60w150.tar',
             'elv_n60w120.tar',
             'elv_n60w090.tar',
             'elv_n60w060.tar',
             'elv_n60w030.tar',
             'elv_n60e000.tar',
             'elv_n60e030.tar',
             'elv_n60e060.tar',
             'elv_n60e090.tar',
             'elv_n60e120.tar',
             'elv_n60e150.tar',
             'elv_n30w180.tar',
             'elv_n30w150.tar',
             'elv_n30w120.tar',
             'elv_n30w090.tar',
             'elv_n30w060.tar',
             'elv_n30w030.tar',
             'elv_n30e000.tar',
             'elv_n30e030.tar',
             'elv_n30e060.tar',
             'elv_n30e090.tar',
             'elv_n30e120.tar',
             'elv_n30e150.tar',
             'elv_n00w180.tar',
             'elv_n00w120.tar',
             'elv_n00w090.tar',
             'elv_n00w060.tar',
             'elv_n00w030.tar',
             'elv_n00e000.tar',
             'elv_n00e030.tar',
             'elv_n00e060.tar',
             'elv_n00e090.tar',
             'elv_n00e120.tar',
             'elv_n00e150.tar',
             'elv_s30w180.tar',
             'elv_s30w150.tar',
             'elv_s30w120.tar',
             'elv_s30w090.tar',
             'elv_s30w060.tar',
             'elv_s30w030.tar',
             'elv_s30e000.tar',
             'elv_s30e030.tar',
             'elv_s30e060.tar',
             'elv_s30e090.tar',
             'elv_s30e120.tar',
             'elv_s30e150.tar',
             'elv_s60w180.tar',
             'elv_s60w090.tar',
             'elv_s60w060.tar',
             'elv_s60w030.tar',
             'elv_s60e000.tar',
             'elv_s60e030.tar',
             'elv_s60e060.tar',
             'elv_s60e090.tar',
             'elv_s60e120.tar',
             'elv_s60e150.tar']

# loop over the list and download each item
for item in file_list:

    # if file already exists in destination, move to next file
    if os.path.isfile(loc_des + item):
        continue

    # specify the url to get
    file_url = loc_src + item

    # Make sure the connection is re-tried if it fails
    retries_max = 1
    retries_cur = 1
    while retries_cur <= retries_max:
        try: 

            # Send a HTTP request to the server and save the HTTP response in a response object called resp
            # 'stream = True' ensures that only response headers are downloaded initially (and not all file contents too, which are 2GB+)
            resp = requests.get(file_url, auth=(user, login), stream=True)  

            # When fully downloaded, write to file
            if resp.status_code == 200:

                # write the contents of the response (r.content) to file ...
                with open(loc_des + item,"wb") as f:
                    f.write(resp.raw.read())

            # print a completion message
            print('Successfully downloaded ' + file_url)

        except:
            print('Error downloading ' + file_url + ' on try ' + str(retries_cur))
            retries_cur += 1
            continue
        else:
            break

