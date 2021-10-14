# Make input file list
Finds names of the SUMMA output files and stores these in the experiment's settings folder. Useful in cases where SUMMA outputs are large and divided into multiple files to keep the size of each individual file manageable. 

## Note on SUMMA output versus mizuRoute input 
Note that SUMMA's parallel implementation actived through the `-g` option results in output files that are split across **space** (i.e. each SUMMA output file contains the full timeseries for a subset of GRUs). mizuRoute can only deal with domains that are split in **time** (i.e. each mizuRoute input file must contain a part of the timeseries for all GRUs). The repository folder `0_tools` contains a script that can convert SUMMA split outputs into mizuRoute split inputs.