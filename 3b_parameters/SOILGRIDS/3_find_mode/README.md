# Extract mode of 6 depth layers
We first find the mode of the soilclasses across depth, to find a single representative soilclass per SOILGRIDS pixel. We will later find the mode soilclass across space, if the modeling domain has model elements that cover multiple SOILGRIDS pixels. This approach mirrors that of Mizukami et al (2017).

## Inputs needed
Six `.tif` files (one for each depth) with pixels representing soil classes.

## Outputs generated
Single .tif file with the mode soilclass for the same domain as the input files covered.

## References
Mizukami, N., Clark, M. P., Newman, A. J., Wood, A. W., Gutmann, E. D., Nijssen, B., Rakovec, O., & Samaniego, L. (2017). Towards seamless large-domain parameter estimation for hydrologic models: LARGE-DOMAIN MODEL PARAMETERS. Water Resources Research, 53(9), 8020–8040. https://doi.org/10.1002/2017WR020401