# Control files
Control files are a basic way to interact with the code in the other parts of the repository. All scripts are set up to look for file_paths and certain other settings in the file `control_active.txt`. 

To define a new domain, start by copying and renaming the `control_template.txt` file and populating it with the desired paths and settings. Then specify the name of this control file in the notebook or Python script `make_folder_structure` that ca be found in folder `../1_folderPrep/`. This notebook/script will copy the contents of the new control file into `control_active.txt`, making sure that all settings are available for the scripts in the rest of the repository.

This setup allows a user to keep multiple control files in this directory, and switch between multiple experiments/domains by simply changing the contents of `control_active.txt`, without making changes to any other scripts in the repository.

## Note
The control files contain data/setting paths and several basic settings related to the temporal and spatial domain of experiments. This provides sufficient functionality to get an initial version of SUMMA and mizuRoute up and running for a given domain, using assumptions made by the authors for their large-domain work. The control files do not contain fields to adjust every single assumption made during model setup. User wishing to deviate from our assumptions need to make the required changes in the relevant scripts.
