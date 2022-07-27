# Goal: project shapefiles (catchments and rivers) into a Winkel Tripel CRS.

# Modules
import os
import shapely
from shapely.geometry import shape, LineString, MultiLineString
import geopandas as gpd

# Specify desired projections
dest_proj = 'ESRI:54030' # See: https://epsg.io/54030
proj_name = 'robinson'
#dest_proj = '+proj=wintri'
#proj_name = 'world_winkel_tripel'

# Specify file locations
root_path = "/gpfs/tp/gwf/gwf_cmt/wknoben/CWARHM_data/domain_"
domains = ["Africa","Europe","NorthAmerica","NorthAsia","Oceania","SouthAmerica","SouthAsia"]
dest_path = '/gpfs/tp/gwf/gwf_cmt/wknoben/CWARHM_data/domain_global/shapefiles'

# Check output location
if not os.path.exists(dest_path):
    os.makedirs(dest_path)

# ---------------------------------------
# FUNCTIONS

def split_geometry_along_vertical_splitter(row,splitter):
    
    '''Treats a specific edge case that shapely.ops.splitter() does not handle: 
       splits a LineString that partly overlaps with a vertical splitter LineString.
       
       In:
       row      - shapefile row containing a "geometry" field. Geometry is assumed to be a LineString
       splitter - shapely LineString containing a vertical line defined by two points
       
       Out:
       new_geom - shapely GeometryCollection containing two LineStrings, split along the splitter line'''
    
    # Assumption 1: we're dealing with LineString geometries
    assert type(row['geometry']) == LineString, "Edge case splitter: input geometry must be Linestring." 
    assert type(splitter) == LineString, "Edge case splitter: splitter geometry must be Linestring." 

    # Get actual coordinates
    line_coords = list(row['geometry'].coords)
    splt_coords = list(splitter.coords)

    # Assumption 2: the splitter is a vertical line
    assert len(splt_coords) == 2, "Edge case splitter: splitter geometry must have 2 coordinates only." 
    assert splt_coords[0][0] == splt_coords[1][0], "Edge case splitter: splitter geometry must be vertical line."

    # Loop over the original coordinates until we find the straight vertical section
    splt_here = splt_coords[0][0] # longitude on which to split
    splt_indx = []
    for ix,(lon,lat) in enumerate(line_coords):
        if lon == splt_here:
            splt_indx.append(ix)

    # Assumption 3: there's only a single straight section
    assert (splt_indx[-1] - splt_indx[0]) == (len(splt_indx) - 1), "Edge case splitter: coordinate indices of straight section are not consecutive."

    # Split the line into two based on the indices we found
    line1 = line_coords[:splt_indx[0]+1]
    line2 = line_coords[splt_indx[-1]:]

    # Store as a geometry so that it can nicely feed into the rest of the code
    new_geom = shape({'type': 'GeometryCollection',
                      'geometries' : [{'type': 'LineString', 'coordinates': line1},
                                      {'type': 'LineString', 'coordinates': line2}]})
    
    return new_geom
    
def remove_split_coordinates_from_geometries(geoms,remove_this_coord):
    
    '''Removes coordinates from split geometries that are exactly on the line used for splitting.
    
       In:
       geoms             - Shapely GeometryCollection containing multiple LineStrings
       remove_this_coord - Coordinate to be removed. Currently does not distinguish between latitude and longitude
       
       Out:
       fixed_geom        - Shapely GeometryCollection containing original LineStrings with identified coordinates removed'''
    
    fixed_geoms = []
    # Look at the geometries we created through splitting the original and remove any antimeridian coordinates
    for geom in geoms:
        
        # Assumption 1: working with LineStrings
        assert type(geom) == LineString, "remove_split_coordinates_from_geometries: input geometries must be Linestring." 

        # Prep coordinate lists
        old_coords = list(geom.coords) # Coordinate tuples that make up this geometry
        new_coords = [] # New list that we will populate with the coordinate tuples we want to keep

        # Copy over the coordinates that we do not want to remove
        for jj, xy in enumerate(old_coords):
            if remove_this_coord not in xy:
                new_coords.append(xy)

        # Convert the coordinate list back into a LineString
        fixed_geoms.append(LineString(new_coords))
    
    return fixed_geoms
    
def fix_northAsia_rivers(shp, 
                         splitter = LineString([(180,25), (180,90)]), # antimeridian
                         remove_this_coord = 180):  # degrees longitude
    
    '''We first split the river on the antimeridian, but this gives us two river segments that end/start on the antimeridian:
       [somewhere,180] & [180,somewhere]. These river segments are stored as LineStrings, which consist of multiple tuples 
       (lon,lat) that describe where the river is. The second setting is used to remove any line-segment coordinates that 
       have (in this case) 180 in them, effectively cutting out the part of the river that crosses the antimeridian. Once that
       is done the rivers can be safely reprojected.'''
    
    # Prep output
    new_shp = shp.copy()
    
    # From a shapefile row, takes the geometry field and attempts to split this by a Shapely geometry
    for ii, row in shp.iterrows():
        
        # Attempt to split the geometry. If it can't be split, we simply get the original geometry back
        # Ingoing data type:  shapely.geometry.linestring.LineString
        # Outgoing data type: shapely.geometry.collection.GeometryCollection[LineString,..]. Could contain multiple lines
        try:
            new_geom = shapely.ops.split(row['geometry'],splitter)
        except ValueError as e: # Above breaks in certain edge cases
            if len(e.args) > 0 and e.args[0] == 'Input geometry segment overlaps with the splitter.':
                new_geom = split_geometry_along_vertical_splitter(row,splitter) # Specific edge case we can now deal with
            else:
                raise e # Original error
        
        # Proceed based on previous outcome
        if len(new_geom) == 1:
            print('Row {}. No split performed. Keeping original entry.'.format(ii))
        elif len(new_geom) > 1:
            print('Row {}. Split performed. Proceeding to remove coordinates directly on the splitting line.'.format(ii))

            # Further processing
            fixed_geoms = remove_split_coordinates_from_geometries(new_geom,remove_this_coord)
            new_geom = MultiLineString(fixed_geoms) # Convert to MultiLineString

            # Replace geometry in row
            row['geometry'] = new_geom
            new_shp.loc[ii] = row
            
    return new_shp    

# ---------------------------------------


# Loop over all domains and reproject
for domain in domains:
    
    # Construct the file names
    if domain == 'NorthAmerica':
        src_basin_shp = root_path + domain + '/shapefiles/catchment/merit_hydro_basins_and_coastal_hillslopes_merged_NA.shp'
        src_river_shp = root_path + domain + '/shapefiles/river_network/merit_river_na_full.shp'
    else:
        src_basin_shp = root_path + domain + '/shapefiles/catchment/' + domain + '_gruhru.shp'
        src_river_shp = root_path + domain + '/shapefiles/river_network/' + domain + '_river_rawMERIT.shp'
    des_basin_shp = dest_path + '/basins_' + domain + '_' + proj_name + '.shp'
    des_river_shp = dest_path + '/rivers_' + domain + '_' + proj_name + '.shp'
    
    # Progress check
    if os.path.exists(des_basin_shp) and os.path.exists(des_river_shp):
        print('Reprojected files already exist for ' + domain + '. Skipping.')
        continue
    else:
        print('Reprojecting shapefiles for ' + domain)
    
    # Load the shapes
    basins = gpd.read_file(src_basin_shp)
    rivers = gpd.read_file(src_river_shp)
    
    # Ensure the CRS is set to EPSG:4326
    if basins.crs != 'EPSG:4326':
        basins.set_crs('EPSG:4326')
    if rivers.crs != 'EPSG:4326':
        rivers.set_crs('EPSG:4326')    
    
    # Ensure we don't end up with criss-crossing nonsense across the antimeridian
    if domain == 'NorthAsia':
        rivers = fix_northAsia_rivers(rivers)        
    
    # Reproject
    basins_proj = basins.to_crs(dest_proj)
    rivers_proj = rivers.to_crs(dest_proj)
    
    # Save in new location
    basins_proj.to_file(des_basin_shp)
    rivers_proj.to_file(des_river_shp)