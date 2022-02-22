# Soil download through Hydroshare
A global map of USGS soil classes has been prepared and is available on Hydroshare. This avoids lengthy preprocessing and provides a consistent download location for this data set.

Hydroshare resource: https://www.hydroshare.org/resource/1361509511e44adfba814f6950c6e742/

## Download registration
Hydroshare downloads require registration through the Hydroshare website. See: https://www.hydroshare.org/sign-up/?next=

Hydroshare downloads use the Python package `hs_restclient`. Downloads require authentication through the client. Store  user details (username and password) in a new file `$HOME/.hydroshare` (Unix/Linux) or `C:\Users\[user]\.hydroshare` (Windows) as follows (replace `[name]` and `[pass]` with your own credentials):

```
name: [name]
pass: [pass]

```

**_Note: given that these passwords are stored as plain text, it is strongly recommended to use a unique password that is different from any other passwords you currently have in use._**

## Download run instructions
Execute the download script and keep the terminal or notebook open until the downloads fully complete. No manual interaction with the https://www.hydroshare.org/ website is required.