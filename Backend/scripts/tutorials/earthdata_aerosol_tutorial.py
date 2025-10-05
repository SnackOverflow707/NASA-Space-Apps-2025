import sys
from datetime import datetime, timedelta
import numpy as np
from shapely.geometry import Point, Polygon
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import netCDF4 as nc
import earthaccess
import copy 

def login():
    auth = earthaccess.login(strategy="netrc")
    return auth

def read_TEMPO_O3TOT_L2_UVAI(filename):
    """Read TEMPO UV Aerosol Index from a L2 granule"""
    arrays = {}
    fill_values = {}

    with nc.Dataset(filename) as ds:
        prod = ds.groups["product"]
        arrays["uvai"] = prod.variables["uv_aerosol_index"][:]
        fill_values["uvai"] = prod.variables["uv_aerosol_index"].getncattr("_FillValue")

        arrays["uvai_QF"] = prod.variables["quality_flag"][:]

        geo = ds.groups["geolocation"]
        arrays["lat"] = geo.variables["latitude"][:]
        arrays["lon"] = geo.variables["longitude"][:]
        arrays["time"] = geo.variables["time"][:]

        # Fix for known garbage geolocation values
        fill_values["geo"] = 9.969209968386869e36

    return arrays, fill_values

def TEMPO_L2_polygon(lat, lon, fv_geo):
    """Create polygon from TEMPO granule coordinates"""
    nx, ny = lon.shape
    dpos = np.empty([0, 2])
    x_ind, y_ind = np.indices((nx, ny))
    mask = (lon != fv_geo) & (lat != fv_geo)
    if len(lon[mask]) == 0:
        return dpos

    # Right boundary
    r_m = min(x_ind[mask].flatten())
    local_mask = mask[r_m, :]
    r_b = np.stack((lon[r_m, local_mask], lat[r_m, local_mask])).T

    # Left boundary
    l_m = max(x_ind[mask].flatten())
    local_mask = mask[l_m, :]
    l_b = np.stack((lon[l_m, local_mask], lat[l_m, local_mask])).T

    # Top and bottom boundaries
    t_b, b_b = np.empty([0, 2]), np.empty([0, 2])
    for ix in range(r_m + 1, l_m):
        local_mask = mask[ix, :]
        y_ind_top, y_ind_bottom = min(y_ind[ix, local_mask]), max(y_ind[ix, local_mask])
        t_b = np.append(t_b, [[lon[ix, y_ind_top], lat[ix, y_ind_top]]], axis=0)
        b_b = np.append(b_b, [[lon[ix, y_ind_bottom], lat[ix, y_ind_bottom]]], axis=0)

    # Combine boundaries counter-clockwise
    dpos = np.append(dpos, r_b[::-1, :], axis=0)
    dpos = np.append(dpos, t_b, axis=0)
    dpos = np.append(dpos, l_b, axis=0)
    dpos = np.append(dpos, b_b[::-1, :], axis=0)

    return dpos

def get_prod_loc(num_loc, lon_loc_array, lat_loc_array, values_loc, fill_value):
    """Interpolate or average values for a given point"""
    if num_loc < 1:
        return fill_value

    mask = np.ones(num_loc, dtype=bool)
    points = np.column_stack((lon_loc_array[mask], lat_loc_array[mask]))
    values = values_loc[mask]

    if len(values) == 0:
        return fill_value
    elif len(values) < 4:
        return np.mean(values)
    else:
        return griddata(points, values, POI_coordinate, method="linear", fill_value=fill_value)[0]
    

def read_aeronet_mw(
    filename: str, wavelengths: list, start_date: datetime.date, end_date: datetime.date
):
    sorted_wavelengths = np.array(copy.deepcopy(sorted(wavelengths)))

    with open(filename, "r") as aero_file:
        # Loop through and read lines until encountering the
        #   header line (identified by 'Date') or null.
        while True:
            line = aero_file.readline()
            if not line:
                break
            if "Date" in line:
                header = line.split(",")
                break

        # Find positions of necessary information in the header.
        # Date and time are always 1st and 2nd.
        date_pos = 0
        time_pos = 1
        aod_pos = [header.index(f"AOD_{wavelength:d}nm") for wavelength in wavelengths]
        name_pos = header.index("AERONET_Site_Name")
        lat_pos = header.index("Site_Latitude(Degrees)")
        lon_pos = header.index("Site_Longitude(Degrees)")

        # Read the 1st line of data to get name, lat, lon.
        values = aero_file.readline().split(",")
        AERONET_name = values[name_pos]
        lat = float(values[lat_pos])
        lon = float(values[lon_pos])

        # If AOD is valid, then append a new row to the aod and date_time arrays.
        aod = np.empty([0, len(wavelengths)])
        date_time = np.empty([0, 2])
        date_loc = values[date_pos]
        if start_date <= datetime.strptime(date_loc, "%d:%m:%Y").date() <= end_date:
            aod_values = np.array([float(values[position]) for position in aod_pos])
            aod = np.append(aod, [aod_values], axis=0)
            date_time = np.append(date_time, [[date_loc, values[time_pos]]], axis=0)

        # Read all other lines of data.
        #   For each AOD that is valid, append a new row to the aod and date_time arrays.
        while True:
            line = aero_file.readline()
            if not line:
                break
            values = line.split(",")

            date_loc = values[date_pos]
            date_stamp = datetime.strptime(date_loc, "%d:%m:%Y").date()
            if date_stamp < start_date or date_stamp > end_date:
                continue

            aod_values = np.array([float(values[position]) for position in aod_pos])
            aod = np.append(aod, [aod_values], axis=0)
            date_time = np.append(date_time, [[date_loc, values[time_pos]]], axis=0)

    return AERONET_name, lat, lon, sorted_wavelengths, date_time, aod


# -------------------- Main Script --------------------
auth = login()

datestamp_initial = input("Enter start date (YYYYMMDD): ")
datestamp_final = input("Enter end date (YYYYMMDD): ")
assert datestamp_initial == '20230805', "Start date must be 20230805 for this tutorial"
assert datestamp_final == '20230805', "End date must be 20230805 for this tutorial"


datetime_initial = datetime.strptime(datestamp_initial + "00:00:00.000000", "%Y%m%d%H:%M:%S.%f")
datetime_final = datetime.strptime(datestamp_final + "23:59:59.999999", "%Y%m%d%H:%M:%S.%f")
date_start = datetime_initial.strftime("%Y-%m-%d %H:%M:%S")
date_end = datetime_final.strftime("%Y-%m-%d %H:%M:%S")

# Define point of interest

aeronet_filename = "/Users/annabel/nasaApps/NASA-Space-Apps-2025/Backend/scripts/tutorials/20010101_20251231_CCNY/20010101_20251231_CCNY.lev20"
wl = [500, 340, 380]
wl = [500, 340, 380]

#read aeronetdata and create timeseries of AODs: 
AERONET_name, lat, lon, wln, date_time, aod = read_aeronet_mw(
    aeronet_filename, wl, datetime_initial.date(), datetime_final.date()
)
POI_lat = lat
POI_lon = lon
POI_name = AERONET_name

num_datetimes = len(date_time)
print(f"name {AERONET_name}, latitude = {POI_lat}, longitude = {POI_lon}")

"""
POI_lat = float(input("Enter latitude of POI: "))
POI_lon = float(input("Enter longitude of POI: "))
POI_name = "POI"

POI_coordinate = np.array([POI_lon, POI_lat])
POI_point = Point(POI_coordinate)
"""

# Search TEMPO granules
short_name = "TEMPO_O3TOT_L2"
version = "V03"
bbox = (POI_lon - 0.5, POI_lat - 0.5, POI_lon + 0.5, POI_lat + 0.5)

POI_results = earthaccess.search_data(short_name=short_name, version=version, temporal=(date_start, date_end), bounding_box=bbox)
if len(POI_results) == 0:
    print("No TEMPO granules found. Exiting.")
    sys.exit()

# Download granules
downloaded_files = earthaccess.download(POI_results, local_path=".")

# Process granules
out_Q = "UVAI_TEMPO"
timeseries_TEMPO_UVAI = []

for result in POI_results:
    granule_link = result["umm"]["RelatedUrls"][0]["URL"]
    tempo_file_name = granule_link.split("/")[-1]
    try:
        tempo, tempo_fv = read_TEMPO_O3TOT_L2_UVAI(tempo_file_name)
    except Exception:
        print(f"Failed to read {tempo_file_name}")
        continue

    # Check if POI is in granule
    tempo_polygon = Polygon(TEMPO_L2_polygon(tempo["lat"], tempo["lon"], tempo_fv["geo"]))
    if not POI_point.within(tempo_polygon):
        continue

    # Loop over pixels to find POI
    found = False
    for ix in range(tempo["lon"].shape[0] - 1):
        for iy in range(tempo["lon"].shape[1] - 1):
            lat_loc = tempo["lat"][ix:ix+2, iy:iy+2].flatten()
            lon_loc = tempo["lon"][ix:ix+2, iy:iy+2].flatten()
            uvai_loc = tempo["uvai"][ix:ix+2, iy:iy+2].flatten()

            mask_noFV = uvai_loc != tempo_fv["uvai"]
            if np.any(mask_noFV):
                uvai_noFV = get_prod_loc(np.sum(mask_noFV), lon_loc[mask_noFV], lat_loc[mask_noFV], uvai_loc[mask_noFV], fill_value=-99.0)
                if uvai_noFV != -99.0:
                    delta_t = timedelta(seconds=(tempo["time"][ix+1] + tempo["time"][ix])*0.5 - tempo["time"][0])
                    mid_granule_datetime = datetime_initial + delta_t
                    dt_loc = (mid_granule_datetime - datetime_initial).total_seconds() / 86400
                    timeseries_TEMPO_UVAI.append([dt_loc, uvai_noFV])
                    found = True
                    break
        if found:
            break

# Convert to numpy array for plotting
timeseries_TEMPO_UVAI = np.array(timeseries_TEMPO_UVAI)

# Plot UVAI
plt.plot(timeseries_TEMPO_UVAI[:,0], timeseries_TEMPO_UVAI[:,1], 'mo', markersize=3)
plt.xlabel(f"Days from {datestamp_initial}")
plt.ylabel("UV Aerosol Index")
plt.title(f"TEMPO UVAI {datestamp_initial} to {datestamp_final} at {POI_name}")
plt.grid(True)
plt.show()
