# QGIS analysis
This part of the workflow requires functions from the QGIS library. At the time of writing, there are multiple ways to achieve this:
1. Install the `qgis` package available on conda-forge and import QGIS functionality in a Python script as you would any other package. The Jupyter notebooks in this folder use this approach. Conda-forge: https://anaconda.org/conda-forge/qgis
2. Install a stand-alone QGIS application on the system and interact with it through a Python script. The Python scripts in this folder use a version of this approach, modified to work in an HPC environment. See: https://docs.qgis.org/3.16/en/docs/pyqgis_developer_cookbook/intro.html


## Differences
Key differences between both approaches are as follows:
1. When QGIS is installed as a (Conda) package, all imports can occur at the top of the script. If Python interacts with a standalone QGIS install, importing the `processing` tools needs to happen after the QGIS path is initialized (see scripts `2` and `3`).
2. When QGIS is installed as a (Conda) package, there is no need to specify the plugin path where `processing` can be found. If Python interacts with a standalone QGIS install, it may be/is necessary to specify the path to the plugin folder. See e.g.: https://gis.stackexchange.com/questions/279874/using-qgis3-processing-algorithms-from-standalone-pyqgis-scripts-outside-of-gui


## Code development
The notebooks were developed on a local machine with the QGIS package installed via Conda. The scripts were developed in an HPC environment were QGIS is available as a module (Copernicus cluster, Global Water Futures, Universisty of Saskatchewan, Canada). Below is an example of how this works:


```
# Load the required HPC modules
module load gcc qgis 

# Run DEM intersection (does not need `processing` tools)
python 1_find_HRU_elevation.py

# Set the path to the QGIS plugin folder
export PYTHONPATH="$EBROOTQGIS/share/qgis/python/plugins:$PYTHONPATH"

# Run the soil and land intersection
python 2_find_HRU_soil_classes.py
python 3_find_HRU_land_classes.py
```

The scripts can easily be adapted to interact with a local QGIS install by specifying the plugin path before the `import processing` line (as shown in the link above). 