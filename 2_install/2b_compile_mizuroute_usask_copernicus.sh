# Compile mizuRoute on USASK's Copernicus
# export variables are used in the makefile. 

#---------------------------------
# Specify settings
#---------------------------------

# --- Location of source code
# Find the path to the source code in 'control_active.txt'
dest_line=$(grep -m 1 "install_path_mizuroute" ../0_controlFiles/control_active.txt)  # full settings line
mizu_path=$(echo ${dest_line##*|})   # removing the leading text up to '|' 
mizu_path=$(echo ${mizu_path%% #*})  # removing the trailing comments, if any are present

# Specify the default path if needed
if [ "$mizu_path" = "default" ]; then
  
 # Get the root path and append appropriate install directories
 root_line=$(grep -m 1 "root_path" ../0_controlFiles/control_active.txt)
 root_path=$(echo ${root_line##*|}) 
 root_path=$(echo ${root_path%% #*}) 
 mizu_path="${root_path}/installs/mizuRoute/route/" # note: NEEDS a trailing '/'

# With custom path, we still need to specify the /route directory for compilation
else 
 mizu_path="${mizu_path}/route/" # note: NEEDS a trailing '/'
fi

# Specify home directory of mizuroute/build
export F_MASTER=$mizu_path 


# --- Specify a name for the executable 
# Find the desired executable name in 'control_active.txt'
exe_line=$(grep -m 1 "exe_name_mizuroute" ../0_controlFiles/control_active.txt) 
mizu_exe=$(echo ${exe_line##*|}) 
mizu_exe=$(echo ${mizu_exe%% #*}) 
export EXE=$mizu_exe


# --- Compiler settings 
# Compiler (used in selection statements inside Makefile)
export FC=gfortran

# Compiler .exe
export FC_EXE='gfortran' # /cvmfs/soft.computecanada.ca/nix/var/nix/profiles/gcc-5.4.0/bin/gfortran


# --- Library settings
# Load the required libraries
module load gcc/7.3.0
module load netcdf-fortran/4.4.4

# Specify the necessary path for the compiler
export NCDF_PATH="$EBROOTNETCDFMINFORTRAN" #/cvmfs/soft.computecanada.ca/easybuild/software/2017/avx2/Compiler/gcc5.4/netcdf-fortran/4.4.4


# --- Define optional setting
# fast:      Enables optimizations
# debug:     Minimum debug options, still
# profile:   Enables profiling
#export MODE=debug 
                 
				 
#---------------------------------
# Print the settings
#---------------------------------
echo 'build directory: ' $F_MASTER
echo 'executable name: ' $EXE
echo 'compiler name:   ' $FC
echo 'compiler .exe:   ' $FC_EXE
echo 'netcdf path:     ' $NCDF_PATH
echo 'compile mode:    ' $MODE
echo # empty line				 


#---------------------------------
# Compile
#---------------------------------
# Copy the makefile and rename
cp Makefile_mizuroute_copernicus $F_MASTER/build/Makefile

# Compile
make -f ${F_MASTER}/build/Makefile