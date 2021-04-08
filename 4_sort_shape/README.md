# Sort catchment shape
SUMMA makes certain assumptions about GRU and HRU order in its input files. It expects the gruId and hruId variables to have identical orders in the forcing, attributes, coldState and trialParameter `.nc` files. In cases where each GRU contains exactly one HRU, no action is needed beyond ensuring that these files use the same order of IDs. In cases where a GRU contains multiple HRUs, additional action is needed. An example of SUMMA's internal reasoning is shown below.

## Example
Imagine a case where 2 GRUs are each divided into 2 HRUs. For some reason, the IDs are as follows:
- GRU 1, HRU 1
- GRU 2, HRU 2
- GRU 1, HRU 3
- GRU 2, HRU 4

From this, SUMMA creates a data structure that looks as follows:
- GRU 1
	* HRU 1
	* HRU 3
- GRU 2
	* HRU 2
	* HRU 4
	
Next, SUMMA checks the order of HRU IDs in all other netcdf files, to ensure these orders are the same. Critically, it reads these IDs in a nested for-loop (pseudo code):

``` 
idx = 1
for gru in GRUs:
	for hru in HRUs:
		check if hruId_in_nc_file(idx) == hru
		idx += 1
	end
end
```

Thus, it expects the HRUs in all other netcdf files to occur in this order at a given index (expectation > actual order in file):
- index 1, HRU 1 > HRU 1 (match)
- index 2, HRU 3 > HRU 2 (error)
- index 3, HRU 2 > HRU 3 (error)
- index 4, HRU 4 > HRU 4 (match)

Therefore, even if HRUs are in identical order in the separate `.nc` files, SUMMA might exit with a warning that HRU orders do not match due to the implicit assumption that all HRUs in a given GRU are at subsequent indices. 

## Solution
In a multiple-HRU-per-GRU case, the catchment shapefile thus needs to be sorted by GRU ID first and HRU ID second, so that the order of HRUs in the shapefile matches SUMMA's expectations.