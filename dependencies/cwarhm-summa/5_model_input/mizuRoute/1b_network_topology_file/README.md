# Network topology
The network topology contains information about the stream network and the routing basins the network is in. These include:
1. Unique indices of the stream segment;
2. Unique indices of the routing basins (HRUs; equivalent to SUMMA GRUs in this setup);
3. ID of the stream segment each individual segment connects to (should be 0 or negative number to indicate that segment is an outlet);
4. ID of the stream segment a basin drains into;
5. Basin area;
6. Segment slope;
7. Segment length.

Values for these settings are taken from the user's shapefiles. See: https://mizuroute.readthedocs.io/en/master/Input_data.html