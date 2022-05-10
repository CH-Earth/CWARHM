# MERIT-Hydro adjusted elevation download
Downloads MERIT-Hydro adjusted elevation data. Data is available in blocks of 30x30 degrees in a regular lat/lon projection. The download code downloads the blocks required to cover the domain. Subsetting to the exact domain happens in follow-up steps.

## Download setup instructions
MERIT Hydro downloads require registration through a Google webform. See: http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_Hydro/

Store the obtained user details (username and password) in a new file `$HOME/.merit` (Unix/Linux) or `C:\Users\[user]\.merit` (Windows) as follows (replace `[user]` and `[pass]` with your own credentials):

```
user: [user]
pass: [pass]

```

## Download run instructions
Execute the download script and keep the terminal or notebook open until the downloads fully complete. No manual interaction with the http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_Hydro/ website is required.