import pyproj
import xarray as xr
import pyrsig
import pandas as pd
import pycno
import matplotlib.pyplot as plt
import os 

tempokey = "tempo.l2.no2.vertical_column_troposphere"
locname = "nyc"
bbox = (-74.8, 40.32, -71.43, 41.4)
bdate = "2023-12-18"

output_dir = "test_plots"
os.makedirs(output_dir, exist_ok=True)

"""Step 2: Exploring Data
Import libraries
Prepare a pyrsig object"""

api = pyrsig.RsigApi(bdate=bdate, bbox=bbox, workdir=locname, gridfit=True)
# api_key = getpass.getpass('Enter TEMPO key (anonymous if unknown):')
api_key = "anonymous"  # using public, so using anonymous
api.tempo_kw["api_key"] = api_key

descdf = api.descriptions()
print(descdf[:10])

df = api.to_dataframe(tempokey, backend="xdr")
print(df[:10])

# Do it again, but cleanup the keys and add time object
# Notice that the file is reused
df = api.to_dataframe(tempokey, unit_keys=False, parse_dates=True, backend="xdr")
print(df[:10])

"""Step 3: Compare to observations
Make an hourly average product.
Make a simple time-series plot
Do the same with airnow to compare"""
# Make an hourly average
hdf = df.groupby(pd.Grouper(key="time", freq="1h")).mean(numeric_only=True)
print(hdf)

# Plot a data column selected from the names above
tempocol = "no2_vertical_column_troposphere"
ax = hdf[tempocol].plot(ylim=(0, None), ylabel="NO2 [molec/cm2]")

airnowkey = "airnow.no2"
adf = api.to_dataframe(airnowkey, unit_keys=False, parse_dates=True)
print(adf[:10])

airnowno2 = adf["no2"].groupby(adf["time"]).median()
ax = hdf[tempocol].plot(ylabel="TEMPO NO2 [molec/cm2]", color="r", marker="+", ylim=(0, 9e15))
airnowno2.plot(ax=ax.twinx(), color="k", marker="o", ylim=(0, 7), ylabel="AirNow NO2 [ppb]")
plt.savefig(os.path.join(output_dir, "timeseries_no2.png"), dpi=300)
plt.close() 


"""Step 4: Create a TEMPO custom map
Here we will request similar data, but pregridded.
This is a custom L3 file on a CMAQ 12km grid."""

api.grid_kw
# Now retrieve a NetCDF file with IOAPI coordinates (like CMAQ)
ds = api.to_ioapi(tempokey)
# Choose a column from above, notice that names are truncated, so they can be weird
tempoikey = "NO2_VERTICAL_CO"
# Now plot a map
cno = pycno.cno(ds.crs_proj4)
fig = plt.figure(figsize=(10, 6))  # optionally specify size
qm = ds[tempoikey].where(lambda x: x > 0).mean(("TSTEP", "LAY")).plot()
cno.drawstates(resnum=1)
# Save the figure
fig.savefig(os.path.join(output_dir, "tempo_custom_map.png"), dpi=300)
plt.close(fig)


"""Step 5: Make a surface NO2 map"""

# Get a column and surface estimate form CMAQ
cmaqcolkey = "cmaq.equates.conus.integrated.NO2_COLUMN"
qids = api.to_ioapi(cmaqcolkey, bdate="2018-12-21")
cmaqsfckey = "cmaq.equates.conus.aconc.NO2"
qsds = api.to_ioapi(cmaqsfckey, bdate="2018-12-21")

"""Align Grids
To align the grids, we have to convert between lambert projections. This is a little complicated, but pyrsig gives you all the tools you need.

get 2d x/y for TEMPO L3 cell centroids
get 2d x/y for TEMPO L3 cell centroids on CMAQ grid
store for later use
pretend the EQUATES data is 2023"""
# 1. get 2d x/y for TEMPO L3 cell centroids
y, x = xr.broadcast(ds.ROW, ds.COL)
# 2. get 2d x/y for TEMPO L3 cell centroids on CMAQ grid
dstproj = pyproj.Proj(ds.crs_proj4)
srcproj = pyproj.Proj(qids.crs_proj4)
X, Y = srcproj(*dstproj(x.values, y.values, inverse=True))
# 3. store the result for later use
ds["CMAQX"] = ("COL",), X.mean(0)
ds["CMAQY"] = ("ROW",), Y.mean(1)
# 4. here we pretend that the CMAQ times align with the TEMPO times
ds["CMAQT"] = ("TSTEP",), qsds.TSTEP.values


"""Extract CMAQ to TEMPO custom L3
We'll extract data using the CMAQ coordinates
And, add the data to the TEMPO dataset"""

# Now we extract the CMAQ at the TEMPO locations
# all extractions will output time, y, x data
dims = ("TSTEP", "ROW", "COL")
# all extractions use the same coordinates
selopts = dict(TSTEP=ds["CMAQT"], COL=ds["CMAQX"], ROW=ds["CMAQY"], method="nearest")
# 1 atm is the surface
selopts["LAY"] = 1
# Get CMAQ surface NO2 (NO2), and tropospheric column (NO2_COLUMN)
ds["CMAQ_NO2_SFC"] = dims, qsds["NO2"].sel(**selopts).data, {"units": "ppb"}
ds["CMAQ_NO2_COL"] = dims, qids["NO2_COLUMN"].sel(**selopts).data * 1e15, {"units": "molec/cm**2"}
     

# Calculate the transfer function
ds["CMAQ_SFC2COL"] = ds["CMAQ_NO2_SFC"] / ds["CMAQ_NO2_COL"]
ds["CMAQ_SFC2COL"].attrs.update(units="1")
# Calculate the estimate surface NO2
ds["TEMPO_SFC"] = ds["NO2_VERTICAL_CO"] * ds["CMAQ_SFC2COL"]
ds["TEMPO_SFC"].attrs.update(units="ppb")


# Now plot the time average
pds = ds.where(ds["NO2_VERTICAL_CO"] > 0).mean(("TSTEP", "LAY"), keep_attrs=True)

# Controlling figure canvas use
gskw = dict(left=0.05, right=0.95, bottom=0.05, top=0.95)
fig, axx = plt.subplots(2, 3, figsize=(18, 8), gridspec_kw=gskw)

"""Now Plot TEMPO-based Surface NO2"""
# Put CMAQ on top row : columns 0, 1, and 2
qmsfc = pds["CMAQ_NO2_SFC"].plot(ax=axx[0, 0], cmap="viridis")
qmcol = pds["CMAQ_NO2_COL"].plot(ax=axx[0, 1], cmap="cividis")
pds["CMAQ_SFC2COL"].plot(ax=axx[0, 2], cmap="Reds")
# Put TEMPO on bottom row and use the same colorscales as CMAQ
pds["TEMPO_SFC"].plot(ax=axx[1, 0], norm=qmsfc.norm, cmap=qmsfc.cmap)
pds["NO2_VERTICAL_CO"].plot(ax=axx[1, 1], norm=qmcol.norm, cmap=qmcol.cmap)
# add state overlays (alternatively)
cno.drawstates(ax=axx, resnum=1)
# hide the unused axes
axx[1, 2].set(visible=False)
# add a reminder
_ = fig.text(0.7, 0.25, "Don't look too close.\nRemember, CMAQ is from 2018 and TEMPO is from 2023")

fig.savefig(os.path.join(output_dir, "surface_no2_plot.png"), dpi=300)
plt.close(fig)