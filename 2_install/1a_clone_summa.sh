# Script to clone SUMMA
# Reads GitHub location of the fork and desired install location from 'summaWorkflow_public/0_controlFiles/control_active.txt'

# --- Settings
# Find the line with the GitHub url
setting_line=$(grep -m 1 "github_summa" ../0_controlFiles/control_active.txt) # -m 1 ensures we only return the top-most result. This is needed because variable names are sometimes used in comments in later lines

# Extract the url
github_url=$(echo ${setting_line##*|}) # remove the part that ends at "|"
github_url=$(echo ${github_url%% #*}) # remove the part starting at '#'; does nothing if no '#' is present

# Find the line with the destination path
dest_line=$(grep -m 1 "install_path_summa" ../0_controlFiles/control_active.txt) 

# Extract the path
summa_path=$(echo ${dest_line##*|}) 
summa_path=$(echo ${summa_path%% #*}) 


# Specify the default path if needed
if [ "$summa_path" = "default" ]; then
  
 # Get the root path
 root_line=$(grep -m 1 "root_path" ../0_controlFiles/control_active.txt)
 root_path=$(echo ${root_line##*|}) 
 root_path=$(echo ${root_path%% #*}) 
 summa_path="${root_path}/installs/summa/"
fi

# --- Clone
# Clone the 'develop' branch of the specified SUMMA repository
echo 'cloning ' $github_url ' into ' $summa_path
git clone --single-branch --branch develop "$github_url" "$summa_path"

# Navigate into the new 'summa' dir
cd "$summa_path"

# Set the upstream repo
git remote add upstream https://github.com/ncar/summa.git

# Fetch latest updates
git pull upstream develop