# MERIT-Hydro 
Note that the MERIT DEM (http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_DEM/) has been superceded by MERIT Hydro DEM (http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_Hydro/).

## Description
Adjusted elevation is reprepared in 4-byte float (float32). The elevations are adjusted to satisfy the condition 'downstream is not higher than its upstream' while minimizing the required modifications from the original DEM. The elevation above EGM96 geoid is represented in meter, and the vertical increment is set to 10cm. The undefined pixels (oceans) are represented by the value -9999 (MERIT webpage, accessed 2020-07-05).

Using gdalinfo on one of the source files shows:
```
[wknoben@gra-login1 ~]$ gdalinfo /project/6008034/Model_Output/ClimateForcingData/MERIT_Hydro_adjusted_elevation/elv_n00e000/n00e005_elv.tif
Driver: GTiff/GeoTIFF
Files: /project/6008034/Model_Output/ClimateForcingData/MERIT_Hydro_adjusted_elevation/elv_n00e000/n00e005_elv.tif
Size is 6000, 6000
Coordinate System is:
GEOGCS["WGS 84",
    DATUM["WGS_1984",
        SPHEROID["WGS 84",6378137,298.257223563,
            AUTHORITY["EPSG","7030"]],
        AUTHORITY["EPSG","6326"]],
    PRIMEM["Greenwich",0],
    UNIT["degree",0.0174532925199433],
    AUTHORITY["EPSG","4326"]]
Origin = (4.999583333333334,4.999583333333334)
Pixel Size = (0.000833333333333,-0.000833333333333)
Metadata:
  AREA_OR_POINT=Area
Image Structure Metadata:
  COMPRESSION=DEFLATE
  INTERLEAVE=BAND
Corner Coordinates:
Upper Left  (   4.9995833,   4.9995833) (  4d59'58.50"E,  4d59'58.50"N)
Lower Left  (   4.9995833,  -0.0004167) (  4d59'58.50"E,  0d 0' 1.50"S)
Upper Right (   9.9995833,   4.9995833) (  9d59'58.50"E,  4d59'58.50"N)
Lower Right (   9.9995833,  -0.0004167) (  9d59'58.50"E,  0d 0' 1.50"S)
Center      (   7.4995833,   2.4995833) (  7d29'58.50"E,  2d29'58.50"N)
Band 1 Block=6000x1 Type=Float32, ColorInterp=Gray
  NoData Value=-9999
```

Summary
- Data is in [m] above EGM96 spheroid
- Ocean tiles are -9999
- Data is stored in band 1 in each .tif
- Data is in regular lat/long (EPSG:4326)

## Download registration
MERIT Hydro downloads require registration through a Google webform. See: http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_Hydro/

Store the obtained user details (username and password) in a new file `$HOME/.merit` (Unix/Linux) or `C:\Users\[user]\.merit` (Windows) as follows (replace `[name]` and `[pass]` with your own credentials):

```
name: [name]
pass: [pass]

```

## Source
http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_Hydro/

## Suggested citation
Yamazaki D., D. Ikeshima, J. Sosa, P.D. Bates, G.H. Allen, T.M. Pavelsky. MERIT Hydro: A high-resolution global hydrography map based on latest topography datasets. Water Resources Research, vol.55, pp.5053-5073, 2019, doi: 10.1029/2019WR024873