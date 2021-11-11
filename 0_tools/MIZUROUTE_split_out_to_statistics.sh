#!/bin/bash

# Assumes yearly mizuRoute outputs. 
# Keeps the mean value over time of two routing variables and also keeps the segment ID variable.
module load StdEnv/2020 intel/2020.1.217 openmpi/4.0.3 cdo/1.9.8

path_src='/scratch/wknoben/summaWorkflow_data/domain_NorthAmerica/simulations/run1/mizuRoute'
path_des='/scratch/wknoben/summaWorkflow_data/domain_NorthAmerica/simulations/run1/statistics'
mkdir -p $path_des

# individual yearly outputs to mean values of variables of interest
for year in {1979..2019}; do
 in="run1.mizuRoute.h.${year}-01-01-00000.nc"
 out="run1_mizuRoute_mean_KWT_IRF_${year}.nc"
 cdo timmean -select,name=KWTroutedRunoff,IRFroutedRunoff,reachID ${path_src}/${in} ${path_des}/${out}
done

# merge separate files into one
cdo timmean -mergetime ${path_des}/run1_mizuRoute_mean_KWT_IRF_*.nc ${path_des}/run1_mizuRoute_mean_KWT_IRF.nc

# remove the individual files for cleanliness
rm ${path_des}/run1_mizuRoute_mean_KWT_IRF_*.nc