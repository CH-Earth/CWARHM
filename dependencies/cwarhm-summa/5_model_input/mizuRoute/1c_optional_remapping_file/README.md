# SUMMA to mizuRoute remapping
Note that this file is **_only_** needed if the defined SUMMA GRUs **_do not_** map 1:1 onto the routing basins as defined for mizuRoute. It is typically easiest to ensure this direct mapping. In cases where the routing basins are different from the GRUs used by SUMMA, this script generates the required mizuRoute input file to do so.

The optional remap file contains information about how the model elements of the Hydrologic Model (HM; i.e. SUMMA in this setup) map onto the routing basins used by the Routing Model (RM; i.e. mizuRoute). This information includes:
1. Unique RM HRU IDs of the routing basins;
2. Unique HM HRU IDs of the modeled basins (note that in this case what mizuRoute calls a "HM HRU" is equivalent to what SUMMA calls a GRU);
3. The number of HM HRUs each RM HRU is overlapped by;
4. The weights (relative area) each HM HRU contributes to each RM HRU.

IDs are taken from the user's shapefiles whereas overlap and weight are calculated based on an intersection of both shapefiles. See: https://mizuroute.readthedocs.io/en/master/Input_data.html