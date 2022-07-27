#!/bin/bash
module load StdEnv/2020 intel/2020.1.217 openmpi/4.0.3 cdo/1.9.8

# Define the simulation paths
root_path="/gpfs/tp/gwf/gwf_cmt/wknoben/CWARHM_data/domain_"
declare -a domain_name=("Africa" "Europe" "NorthAmerica" "NorthAsia" "Oceania" "SouthAmerica" "SouthAsia")
declare -a sim_folders=("simulations/run1" "simulations/run1" "simulations/run3" "simulations/run1" "simulations/run1" "simulations/run1" "simulations/run1")
declare -a summa_files=("SUMMA/run1_day.nc" "SUMMA/run1_day.nc" "SUMMA/run3_day.nc" "SUMMA/run1_day.nc" "SUMMA/run1_day.nc" "SUMMA/run1_day.nc" "SUMMA/run1_day.nc")
declare -a mizur_files=("mizuRoute/run1.h.1979-01-01-00000.nc" "mizuRoute/run1.h.1979-01-01-00000.nc" "mizuRoute/run3.h.1979-01-01-00000.nc" "mizuRoute/run1.h.1979-01-01-00000.nc" "mizuRoute/run1.h.1979-01-01-00000.nc" "mizuRoute/run1.h.1979-01-01-00000.nc" "mizuRoute/run1.h.1979-01-01-00000.nc")
arraylength=${#domain_name[@]} 

# Define a location where we can temporarily store the simulation files so we don't need to swap back and forth
dest_path="/gpfs/tp/gwf/gwf_cmt/wknoben/CWARHM_data/domain_global/simulation_stats"
mkdir -p $dest_path

# Loop over all simulations and find the mean values we're after
for (( i=0; i<${arraylength}; i++ ));
do
  summa_in="$root_path${domain_name[$i]}/${sim_folders[$i]}/${summa_files[$i]}"
  mizur_in="$root_path${domain_name[$i]}/${sim_folders[$i]}/${mizur_files[$i]}"
  summa_out="${dest_path}/SUMMA_stat_197901_${domain_name[$i]}.nc"
  mizur_out="${dest_path}/mizuRoute_stat_197901_${domain_name[$i]}.nc"
  
  #echo "index: $i, SUMMA in : $summa_in"
  #echo "index: $i, SUMMA out: $summa_out"
  #echo "index: $i, mizuR in : $mizur_in"
  #echo "index: $i, SUMMA out: $mizur_out"
  
  echo "Working on ${domain_name[$i]}"
  cdo timmean -select,name=scalarTotalET,scalarTotalRunoff,gruId,hruId ${summa_in} ${summa_out}
  cdo timmean -select,name=IRFroutedRunoff,reachID ${mizur_in} ${mizur_out}
done
