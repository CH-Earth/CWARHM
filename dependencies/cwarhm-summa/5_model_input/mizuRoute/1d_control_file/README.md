# mizuRoute control file
Makes a `.control` file with the settings specified in the (workflow) control file. See: https://mizuroute.readthedocs.io/en/master/Control_file.html

#### route_opt
This setting determines whether mizuRoute performs routing with an Impulse Response Function (IRF; 1), Kinematic Wave Tracking (KWT; 2) or both (0). Note that if this variable is not specified in the control file, no outputs will be written to disk. The workflow code specifies this vale as `0` by default.

#### doesBasinRoute
In the default setup in this workflow, the SUMMA modeling decision `subRouting` is set to `timeDlay` which means that within-GRU routing is active inside SUMMA. This is functionally identical to mizuRoute's within-basin routing controlled by the option `doesBasinRoute` and these two should not be used at the same time. Therefore the workflow sets `doesBasinRoute` to `0` (inactive) by default when it generates the mizuRoute control file.

## Assumptions not specified in `control_active.txt`
- Many of the variable names used in mizuRoute's control file are hard-coded here, because they are hard-coded in the other mizuRoute setup files as well. This is a conscious decision to make the variable names used by the scripts in the workflow correspond closely to the names used in the mizuRoute online documentation.
- It is assumed that routing should be done for the entire provided river network. This can be changed by changing the value of variable `topolgy_outlet` to the segment ID that should be treated as the de facto outlet of the network.