#!/bin/bash
module load StdEnv/2020 intel/2020.1.217 openmpi/4.0.3 cdo/1.9.8 nco/4.9.5

path_src='/scratch/wknoben/summaWorkflow_data/domain_NorthAmerica/simulations/run1/SUMMA'
path_tmp='/scratch/wknoben/summaWorkflow_data/domain_NorthAmerica/simulations/run1/tmp'
path_des='/scratch/wknoben/summaWorkflow_data/domain_NorthAmerica/simulations/run1/intermediate'
year=$1 # accepts year as input argument; disable this and enable FOR loop below to run everything sequentially

# loop over all years and months
#for year in {1979..2019}; do
 for month in {01..12}; do
  
  # progress
  echo ${year}-${month}
  
  # make the year/month tmp dir
  path_tym=${path_tmp}${year}${month}
  mkdir -p ${path_tym}
   
  # get the number of days in this month
  nDays=$(cal $month $year | awk 'NF {DAYS = $NF}; END {print DAYS}')
  
  # extract from each file the period of interest and save in the temporary dir
  for file in ${path_src}/run1_G*_timestep.nc; do
   
   # extract the filename
   filename=$(basename -- $file)
  
   # extract the month into new file
   cdo --silent seldate,${year}-${month}-01,${year}-${month}-${nDays} ${file} ${path_tym}/tmp.nc 
   
   # keep only our variable of interest
   cdo --silent select,name=averageRoutedRunoff,gruId ${path_tym}/tmp.nc ${path_tym}/${filename} 
   
   # re-order the dimensions to make gru the unlimited dimensions
   ncpdq -O -a gru,time ${path_tym}/${filename} ${path_tym}/${filename}
   
   # remove the tmp file
   rm -r ${path_tym}/tmp.nc
	
  done
  
  # merge everything in the temporary dir into a single file
  ncrcat -O ${path_tym}/*.nc ${path_des}/run1_${year}${month}.nc
  
  # swap the dimensions again
  ncpdq -O -L 1 -a time,gru ${path_des}/run1_${year}${month}.nc ${path_des}/run1_${year}${month}.nc
  
  # clean the temporary dir
  rm -r ${path_tym}
  
 done
#done