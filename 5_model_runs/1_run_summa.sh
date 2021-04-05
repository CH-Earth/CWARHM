# Script to run SUMMA
# Reads all the required info from 'summaWorkflow_public/0_controlFiles/control_active.txt'

# --- Settings

# - Find the SUMMA install dir 
# ----------------------------
setting_line=$(grep -m 1 "install_path_summa" ../0_controlFiles/control_active.txt) # -m 1 ensures we only return the top-most result. This is needed because variable names are sometimes used in comments in later lines

# Extract the path
summa_path=$(echo ${setting_line##*|}) # remove the part that ends at "|"
summa_path=$(echo ${summa_path%% #*}) # remove the part starting at '#'; does nothing if no '#' is present

# Specify the default path if needed
if [ "$summa_path" = "default" ]; then
  
 # Get the root path
 root_line=$(grep -m 1 "root_path" ../0_controlFiles/control_active.txt)
 root_path=$(echo ${root_line##*|}) 
 root_path=$(echo ${root_path%% #*}) 
 summa_path="${root_path}/installs/summa/bin/"
fi
echo $summa_path


# - Find the SUMMA executable
# ---------------------------
setting_line=$(grep -m 1 "exe_name_summa" ../0_controlFiles/control_active.txt) 
summa_exe=$(echo ${setting_line##*|}) 
summa_exe=$(echo ${summa_exe%% #*}) 
echo $summa_exe

# - Find where the SUMMA settings are
# -----------------------------------
setting_line=$(grep -m 1 "settings_summa_path" ../0_controlFiles/control_active.txt) 
settings_path=$(echo ${setting_line##*|}) 
settings_path=$(echo ${settings_path%% #*}) 

# Specify the default path if needed
if [ "$settings_path" = "default" ]; then
  
 # Get the root path
 root_line=$(grep -m 1 "root_path" ../0_controlFiles/control_active.txt)
 root_path=$(echo ${root_line##*|}) 
 root_path=$(echo ${root_path%% #*}) 
 
 # Get the domain name
 domain_line=$(grep -m 1 "domain_name" ../0_controlFiles/control_active.txt)
 domain_name=$(echo ${root_line##*|}) 
 domain_name=$(echo ${domain_name%% #*})
 
 # Make the default path
 settings_path="${root_path}/domain_${domain_name}/settings/SUMMA/"
fi
echo $settings_path

# - Find the filemanager name
# ---------------------------
setting_line=$(grep -m 1 "settings_summa_filemanager" ../0_controlFiles/control_active.txt) 
filemanager=$(echo ${setting_line##*|}) 
filemanager=$(echo ${filemanager%% #*})
echo $filemanager

# - Find where the SUMMA logs need to go
# --------------------------------------
setting_line=$(grep -m 1 "experiment_log_summa" ../0_controlFiles/control_active.txt) 
summa_log_path=$(echo ${setting_line##*|}) 
summa_log_path=$(echo ${summa_log_path%% #*})

# Specify the default path if needed
if [ "$summa_log_path" = "default" ]; then
 
 # Get the root path
 root_line=$(grep -m 1 "root_path" ../0_controlFiles/control_active.txt)
 root_path=$(echo ${root_line##*|}) 
 root_path=$(echo ${root_path%% #*}) 
 
 # Get the domain name
 domain_line=$(grep -m 1 "domain_name" ../0_controlFiles/control_active.txt)
 domain_name=$(echo ${root_line##*|}) 
 domain_name=$(echo ${domain_name%% #*})
 
 # Get the experiment ID
 log_line=$(grep -m 1 "experiment_id" ../0_controlFiles/control_active.txt)
 log_name=$(echo ${exp_line##*|}) 
 log_name=$(echo ${log_name%% #*})
 
 # Make the default path
 summa_log_path="${root_path}/domain_${domain_name}/simulations/${exp_name}/SUMMA_logs/"
fi
echo $summa_log_path

# - Get the SUMMA output path (for code provenance and possibly settings backup)
# ------------------------------------------------------------------------------
summa_out_line=$(grep -m 1 "settings_summa_path" ../0_controlFiles/control_active.txt)
summa_out_path=$(echo ${summa_out_line##*|}) 
summa_out_path=$(echo ${summa_out_path%% #*})

# Specify the default path if needed
if [ "$summa_out_path" = "default" ]; then
 
 # Get the root path
 root_line=$(grep -m 1 "root_path" ../0_controlFiles/control_active.txt)
 root_path=$(echo ${root_line##*|}) 
 root_path=$(echo ${root_path%% #*}) 
 
 # Get the domain name
 domain_line=$(grep -m 1 "domain_name" ../0_controlFiles/control_active.txt)
 domain_name=$(echo ${root_line##*|}) 
 domain_name=$(echo ${domain_name%% #*})
 
 # Get the experiment ID
 exp_line=$(grep -m 1 "experiment_id" ../0_controlFiles/control_active.txt)
 exp_name=$(echo ${exp_line##*|}) 
 exp_name=$(echo ${exp_name%% #*})
 
 # Make the default path
 summa_out_path="${root_path}/domain_${domain_name}/simulations/${exp_name}/SUMMA/"
fi
echo $summa_out_path

# - Find if we need to backup the settings and find the path if so
# ----------------------------------------------------------------
setting_line=$(grep -m 1 "experiment_backup_settings" ../0_controlFiles/control_active.txt) 
do_backup=$(echo ${setting_line##*|}) 
do_backup=$(echo ${do_backup%% #*}) 

# Specify the path (inside the experiment output folder)
if [ "$do_backup" = "yes" ]; then
 # Make the setting backup path
 backup_path="${summa_out_path}/run_settings"
fi
echo $backup_path


# --- Run
# Do the settings backup if needed
if [ "$do_backup" = "yes" ]; then
 mkdir -p $backup_path
 copy_command="cp -R ${settings_path}/. ${backup_path}"
 echo $copy_command
fi

# Run SUMMA
mkdir -p $summa_log_path
summa_command="${summa_path}/${summa_exe} -m ${settings_path}/${filemanager}"
echo $summa_command > $summa_log_path/summa_log.txt



# --- Code provenance
# Generates a basic log file in the domain folder and copies the control file and itself there.
# Make a log directory if it doesn't exist
log_path="${summa_out_path}/_workflow_log"
mkdir -p $log_path

# Log filename
today=`date '+%F'`
log_file="${today}_clone_log.txt"

# Make the log
this_file='1_run_summa.sh'
echo "Log generated by ${this_file} on `date '+%F %H:%M:%S'`"  > $log_path/$log_file # 1st line, store in new file
echo 'Ran SUMMA.' >> $log_path/$log_file # 2nd line, append to existing file

# Copy this file to log directory
cp $this_file $log_path










