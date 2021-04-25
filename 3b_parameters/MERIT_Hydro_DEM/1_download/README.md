# MERIT-Hydro adjusted elevation download
Downloads MERIT-Hydro adjusted elevation data. Data is available in blocks of 30x30 degrees in a regular lat/lon projection. The download code downloads the blocks required to cover the domain. Subsetting to the exact domain happens in follow-up steps.

## Download setup instructions
MERIT Hydro downloads require registration through a Google webform. See: http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_Hydro/

Store the obtained user details (username and password) in a new file `$HOME/.merit` (Unix/Linux) or `C:\Users\[user]\.merit` (Windows) as follows (replace `[name]` and `[pass]` with your own credentials):

```
name: [name]
pass: [pass]

```