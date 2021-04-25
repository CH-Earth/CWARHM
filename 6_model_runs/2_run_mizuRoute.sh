# Script to run mizuRoute
# Reads all the required info from 'summaWorkflow_public/0_control_files/control_active.txt'

# --- Settings

# - Find the mizuRoute install dir 
# --------------------------------
setting_line=$(grep -m 1 "install_path_mizuroute" ../0_control_files/control_active.txt) # -m 1 ensures we only return the top-most result. This is needed because variable names are sometimes used in comments in later lines

# Extract the path
mizu_path=$(echo ${setting_line##*|}) # remove the part that ends at "|"
mizu_path=$(echo ${mizu_path%%#*}) # remove the part starting at '#'; does nothing if no '#' is present

# Specify the default path if needed
if [ "$mizu_path" = "default" ]; then
  
 # Get the root path
 root_line=$(grep -m 1 "root_path" ../0_control_files/control_active.txt)
 root_path=$(echo ${root_line##*|}) 
 root_path=$(echo ${root_path%%#*}) 
 mizu_path="${root_path}/installs/mizuRoute/route/bin/"
fi
echo "install  = ${mizu_path}"


# - Find the mizuRoute executable
# -------------------------------
setting_line=$(grep -m 1 "exe_name_mizuroute" ../0_control_files/control_active.txt) 
mizu_exe=$(echo ${setting_line##*|}) 
mizu_exe=$(echo ${mizu_exe%%#*}) 
echo "exe      = ${mizu_exe}"


# - Find where the mizuRoute settings are
# ---------------------------------------
setting_line=$(grep -m 1 "settings_mizu_path" ../0_control_files/control_active.txt) 
settings_path=$(echo ${setting_line##*|}) 
settings_path=$(echo ${settings_path%%#*}) 

# Specify the default path if needed
if [ "$settings_path" = "default" ]; then
  
 # Get the root path
 root_line=$(grep -m 1 "root_path" ../0_control_files/control_active.txt)
 root_path=$(echo ${root_line##*|}) 
 root_path=$(echo ${root_path%%#*}) 
 
 # Get the domain name
 domain_line=$(grep -m 1 "domain_name" ../0_control_files/control_active.txt)
 domain_name=$(echo ${domain_line##*|}) 
 domain_name=$(echo ${domain_name%%#*})
 
 # Make the default path
 settings_path="${root_path}/domain_${domain_name}/settings/mizuRoute/"
fi
echo "Settings = ${settings_path}"


# - Find the .control filename
# ----------------------------
setting_line=$(grep -m 1 "settings_mizu_control_file" ../0_control_files/control_active.txt) 
control_file=$(echo ${setting_line##*|}) 
control_file=$(echo ${control_file%%#*})
echo "control  = ${control_file}"


# - Find where the mizuRoute logs need to go
# ------------------------------------------
setting_line=$(grep -m 1 "experiment_log_mizuroute" ../0_control_files/control_active.txt) 
mizu_log_path=$(echo ${setting_line##*|}) 
mizu_log_path=$(echo ${mizu_log_path%%#*})
mizu_log_name="mizuRoute_log.txt"

# Specify the default path if needed
if [ "$mizu_log_path" = "default" ]; then
 
 # Get the root path
 root_line=$(grep -m 1 "root_path" ../0_control_files/control_active.txt)
 root_path=$(echo ${root_line##*|}) 
 root_path=$(echo ${root_path%%#*}) 
 
 # Get the domain name
 domain_line=$(grep -m 1 "domain_name" ../0_control_files/control_active.txt)
 domain_name=$(echo ${domain_line##*|}) 
 domain_name=$(echo ${domain_name%%#*})
 
 # Get the experiment ID
 exp_line=$(grep -m 1 "experiment_id" ../0_control_files/control_active.txt)
 exp_name=$(echo ${exp_line##*|}) 
 exp_name=$(echo ${exp_name%%#*})
 
 # Make the default path
 mizu_log_path="${root_path}/domain_${domain_name}/simulations/${exp_name}/mizuRoute/mizuRoute_logs/"
fi
echo "log      = ${mizu_log_path}"
echo "file     = ${mizu_log_name}"


# - Get the mizuRoute output path (for code provenance and possibly settings backup)
# ----------------------------------------------------------------------------------
mizu_out_line=$(grep -m 1 "settings_mizu_path" ../0_control_files/control_active.txt)
mizu_out_path=$(echo ${mizu_out_line##*|}) 
mizu_out_path=$(echo ${mizu_out_path%%#*})

# Specify the default path if needed
if [ "$mizu_out_path" = "default" ]; then
 
 # Get the root path
 root_line=$(grep -m 1 "root_path" ../0_control_files/control_active.txt)
 root_path=$(echo ${root_line##*|}) 
 root_path=$(echo ${root_path%%#*}) 
 
 # Get the domain name
 domain_line=$(grep -m 1 "domain_name" ../0_control_files/control_active.txt)
 domain_name=$(echo ${domain_line##*|}) 
 domain_name=$(echo ${domain_name%%#*})
 
 # Get the experiment ID
 exp_line=$(grep -m 1 "experiment_id" ../0_control_files/control_active.txt)
 exp_name=$(echo ${exp_line##*|}) 
 exp_name=$(echo ${exp_name%%#*})
 
 # Make the default path
 mizu_out_path="${root_path}/domain_${domain_name}/simulations/${exp_name}/mizuRoute/"
fi
echo "mizu out = ${mizu_out_path}"


# - Find if we need to backup the settings and find the path if so
# ----------------------------------------------------------------
setting_line=$(grep -m 1 "experiment_backup_settings" ../0_control_files/control_active.txt) 
do_backup=$(echo ${setting_line##*|}) 
do_backup=$(echo ${do_backup%%#*}) 

# Specify the path (inside the experiment output folder)
if [ "$do_backup" = "yes" ]; then
 # Make the setting backup path
 backup_path="${mizu_out_path}run_settings"
fi
echo "backup   = ${backup_path}"


# --- Run
# Do the settings backup if needed
if [ "$do_backup" = "yes" ]; then
 mkdir -p $backup_path
 copy_command="cp -R ${settings_path}. ${backup_path}"
 $copy_command
fi

# Run SUMMA
mkdir -p $mizu_log_path
mizu_command="${mizu_path}${mizu_exe} ${settings_path}${control_file}"
$mizu_command > $mizu_log_path$mizu_log_name


# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.
# Make a log directory if it doesn't exist
log_path="${mizu_out_path}/_workflow_log"
mkdir -p $log_path

# Log filename
today=`date '+%F'`
log_file="${today}_mizuRoute_run_log.txt"

# Make the log
this_file='2_run_mizuRoute.sh'
echo "Log generated by ${this_file} on `date '+%F %H:%M:%S'`"  > $log_path/$log_file # 1st line, store in new file
echo 'Ran mizuRoute.' >> $log_path/$log_file # 2nd line, append to existing file

# Copy this file to log directory
cp $this_file $log_path