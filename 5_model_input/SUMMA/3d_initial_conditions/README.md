# Initial conditions file
Makes an initial conditions file with basic assumptions. The initial conditions or state file contains a number of modeling options. The state file is an `.nc` file with dimensions `nSoil`, `nSnow`, `midSoil`, `midToto`, `ifcToto` and `scalarv`. See: https://summa.readthedocs.io/en/latest/input_output/SUMMA_input/#initial-conditions-restart-or-state-file

State parameters are set at hard-coded values as follows:

| Parameter            | Value                                        | Units  | Description |
|----------------------|----------------------------------------------|--------|-------------|
| dt_init              | taken from control file                      | s      | Time step size of forcing data |
| nSoil                | 8                                            | -      | Number of soil layers |
| nSnow                | 0                                            | -      | Number of currently active snow layers |
| iLayerHeight         | [0, 0.025, 0.1, 0.25, 0.5, 1, 1.5, 2.5, 4]   | m      | Location of layer boundaries. 0 at the soil surface with positive numbers indicating deeper layers |
| mLayerHeight         | [0.025, 0.075, 0.15, 0.25, 0.5, 0.5, 1, 1.5] | m      | Mid-point of each active layer. 0 at the soil surface with positive numbers indicating deeper layers |
| scalarCanopyIce      | 0                                            | kg m-2 | Current ice storage in the canopy |
| scalarCanopyLiq      | 0                                            | kg m-2 | Current liquid water storage in the canopy |
| scalarSnowDepth      | 0                                            | m      | Current snow depth |
| scalarSWE            | 0                                            | kg m-2 | Current snow water equivalent |
| scalarSfcMeltPond    | 0                                            | kg m-2 | Current ponded melt water |
| scalarAquiferStorage | 1.0                                          | m      | Current aquifer storage |
| scalarSnowAlbedo     | 0                                            | -      | Current snow albedo |
| scalarCanairTemp     | 283.16                                       | K      | Current temperature in the canopy airspace |
| scalarCanopyTemp     | 283.16                                       | K      | Current temperature of the canopy |
| mLayerTemp           | 283.16                                       | K      | Current temperature of each layer; assumed that all layers are identical |
| mLayerVolFracIce     | 0                                            | -      | Current ice storage in each layer; assumed that all layers are identical |
| mLayerVolFracLiq     | 0.2                                          | -      | Current liquid water storage in each layer; assumed that all layers are identical |
| mLayerMatricHead     | -1.0                                         | m      | Current matric head in each layer; assumed that all layers are identical |

SUMMA has built-in capability to save the model states at a given time step. This behaviour is controlled by runtime argument `-r` (for "restart") and parameter `year`, `month`, `day` or `end`. Runs can be restarted from such a file by changing the name of the `initConditionFile` entry in `fileManager.txt`. Such files can also form the basis for a more appropriate initial conditions file when they result from long runs. This initial long run can be treated as a model warm-up period and the restart file can be used as an approximation of the slowly changing model states. The folder `0_tools` that is part of this repository contains a script that can be used to strip the snow layers from a restart file if desired.