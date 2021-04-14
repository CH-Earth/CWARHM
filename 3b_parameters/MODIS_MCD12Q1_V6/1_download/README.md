# MODIS download 
MODIS downloads are performed directly through the URLs provided in the file `daac_mcd12q1_data_links.txt`.

The downloads require registration through NASA's EarthData website. See: https://urs.earthdata.nasa.gov/

Authentication is handled through Python's `requests` package. Store  user details (username and password) in a new file `$HOME/.netrc` (Unix/Linux) or `C:\Users\[user]\.netrc` (Windows) as follows (replace `[name]` and `[pass]` with your own credentials):

```
name: [name]
pass: [pass]

```

**_Note: given that these passwords are stored as plain text, it is strongly recommended to use a unique password that is different from any other passwords you currently have in use._**
