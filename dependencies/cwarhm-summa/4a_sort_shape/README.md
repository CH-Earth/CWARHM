# Sort catchment shape
SUMMA makes certain assumptions about GRU and HRU order in its input files:
1. It expects the gruId and hruId variables to have identical orders in the forcing, attributes, coldState and trialParameter `.nc` files. In cases where each GRU contains exactly one HRU, no action is needed beyond ensuring that these files use the same order of IDs. 
2. In cases where a GRU contains multiple HRUs, additional action is needed. In a multiple-HRU-per-GRU case, the catchment shapefile needs to be sorted by GRU ID first and HRU ID second, so that the order of HRUs in the shapefile matches SUMMA's expectations.

An example of correct and incorrect GRU & HRU sorting is provided below. 

## Example
Imagine a case where 2 GRUs are each divided into 2 HRUs. The GRU IDs are 1 and 2, and the HRU IDs are 1-4.

### Incorrect sorting
This example is sorted by HRU IDs first, and GRU IDs second. This does not match SUMMA's input requirements.

- GRU 1, HRU 1
- GRU 2, HRU 2
- GRU 1, HRU 3
- GRU 2, HRU 4

### Correct sorting
This example is sorted by GRU IDs first, and HRU IDs second. This matches SUMMA's input requirements.

- GRU 1, HRU 1
- GRU 1, HRU 3
- GRU 2, HRU 2
- GRU 2, HRU 4


## Explanation
SUMMA checks its input files for consistency when the model is first initialized. It first builds a data structure of GRU and HRU IDs as follows:
- GRU 1
	* HRU 1
	* HRU 3
- GRU 2
	* HRU 2
	* HRU 4
	
Next, SUMMA checks the order of HRU IDs in all other netcdf files, to ensure these orders are the same. Critically, it reads these IDs in a nested for-loop (pseudo code):

``` 
idx = 1
for gru in all_GRUs:
	for hru in HRUs_in_this_GRU:
		check if hruId_in_nc_file(idx) == hru
		idx += 1
	end
end
```

Therefore, it assumes the HRUs can be found at the following indices in each `.nc` file:
- GRU 1
	* HRU 1: expected at index 1
	* HRU 3: expected at index 2
- GRU 2
	* HRU 2: expected at index 3
	* HRU 4: expected at index 4
	
The sorting ensures that this expectation is met.

## Control file settings
This section lists all the settings in `control_active.txt` that the code in this folder uses.
- **catchment_shp_path, catchment_shp_name**: location of the catchment shapefile.
- **catchment_shp_gruid, catchment_shp_hruid**: names of the GRU and HRU ID columns in the shapefile
