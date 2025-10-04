#tutorial link https://nasa.github.io/ASDC_Data_and_User_Services/DSCOVR/how_to_compare_TEMPO_with_DSCOVR_and_AERONET_uvai.html#work-with-tempo-data 

import copy
import sys
from datetime import datetime, timedelta

import earthaccess  # needed to discover and download TEMPO data
import h5py  # needed to read DSCOVR_EPIC_L2_TO3 files
import matplotlib.pyplot as plt  # needed to plot the resulting time series
import netCDF4 as nc  # needed to read TEMPO data
import numpy as np
from shapely.geometry import Point, Polygon  # needed to search a point within a polygon
from scipy.interpolate import griddata  # needed to interpolate TEMPO data to the point of interest 

def login():
    auth = earthaccess.login(strategy="netrc")
    return auth

#function to read DSCOVR AER data files
def get_dataset_array_and_fill_value(file_object: h5py.File, dataset_path: str):
    h5_dataset = file_object[dataset_path]
    return np.array(h5_dataset[:]), h5_dataset.fillvalue


def read_epic_l2_AER(filename: str):
    aod_name = "/HDFEOS/SWATHS/Aerosol NearUV Swath/Data Fields/FinalAerosolOpticalDepth"
    uvai_name = "/HDFEOS/SWATHS/Aerosol NearUV Swath/Data Fields/UVAerosolIndex"
    lat_name = "/HDFEOS/SWATHS/Aerosol NearUV Swath/Geolocation Fields/Latitude"
    lon_name = "/HDFEOS/SWATHS/Aerosol NearUV Swath/Geolocation Fields/Longitude"
    wl_name = "/HDFEOS/SWATHS/Aerosol NearUV Swath/Data Fields/Wavelength"

    arrays = {}
    fill_values = {}

    with h5py.File(filename, "r") as f:
        arrays["aod3D"], fill_values["aod"] = get_dataset_array_and_fill_value(f, aod_name)
        arrays["uvai2D"], fill_values["uvai"] = get_dataset_array_and_fill_value(f, uvai_name)
        arrays["lat2D"], fill_values["lat"] = get_dataset_array_and_fill_value(f, lat_name)
        arrays["lon2D"], fill_values["lon"] = get_dataset_array_and_fill_value(f, lon_name)
        arrays["wl"], fill_values["wl"] = get_dataset_array_and_fill_value(f, wl_name)

    # Get time from the granule's filename.
    timestamp = datetime.strptime(filename.split("_")[-2], "%Y%m%d%H%M%S")

    return arrays, fill_values, timestamp

#function to read AERONET data files 

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


#functions to work with TEMPO
def read_TEMPO_O3TOT_L2_UVAI(filename):
    """Read the following product arrays from the TEMPO_O3TOT_L2_V03(2):
        - vertical_column
        - vertical_column_uncertainty

    and returns the respective fields along with coordinates of the pixels.
    """
    var_name = "uv_aerosol_index"
    var_QF_name = "quality_flag"

    arrays = {}
    fill_values = {}

    with nc.Dataset(filename) as ds:
        # Open the product group (/product), read the chosen UVAI variable and its quality flag.
        prod = ds.groups["product"]  # this opens group product, /product, as prod
        arrays["uvai"] = prod.variables[var_name][:]
        fill_values["uvai"] = prod.variables[var_name].getncattr("_FillValue")
        var_QF = prod.variables[var_QF_name]
        arrays["uvai_QF"] = var_QF[:]
        # Note: there is no fill value for the quality flag.
        # Once it is available in the next version of the product,
        # un-comment the line below and add fv_QF to the return line.
        #    fv_QF = var_QF.getncattr('_FillValue')

        # Open geolocation group (/geolocation), and
        #   read the latitude and longitude variables into a numpy array.
        geo = ds.groups["geolocation"]  # this opens group geolocation, /geolocation, as geo
        arrays["lat"] = geo.variables["latitude"][
            :
        ]  # this reads variable latitude from geo (geolocation group, /geolocation) into a numpy array
        arrays["lon"] = geo.variables["longitude"][
            :
        ]  # this reads variable longitude from geo (geolocation group, /geolocation) into a numpy array
        fill_values["geo"] = geo.variables["latitude"].getncattr("_FillValue")
        # Note: it appeared that garbage values of latitudes and longitudes in the L2 files
        # are 9.969209968386869E36 while fill value is -1.2676506E30
        # (after deeper search it was found that actual value in the file is -1.2676506002282294E30).
        # For this reason, fv_geo is set to 9.96921E36 to make the code working.
        # Once the problem is resolved and garbage values of latitudes and longitudes
        # equal to their fill value, the line below must be removed.
        fill_values["geo"] = 9.969209968386869e36

        arrays["time"] = geo.variables["time"][
            :
        ]  # this reads variable longitude from geo (geolocation group, /geolocation) into a numpy array

    return arrays, fill_values

#function creating TEMPO O3 granule polygon

def TEMPO_L2_polygon(lat, lon, fv_geo):
    nx = lon.shape[0]
    ny = lon.shape[1]
    print("granule has %3d scanlines by %4d pixels" % (nx, ny))

    dpos = np.empty([0, 2])

    x_ind = np.empty([nx, ny], dtype=int)  # creating array in x indices
    for ix in range(nx):
        x_ind[ix, :] = ix  # populating array in x indices
    y_ind = np.empty([nx, ny], dtype=int)
    for iy in range(ny):
        y_ind[:, iy] = iy  # populating array in x indices

    mask = (lon[ix, iy] != fv_geo) & (lat[ix, iy] != fv_geo)
    if len(lon[mask]) == 0:
        print("the granule is empty - no meaningful positions")
        return dpos

    # right boundary
    r_m = min(x_ind[mask].flatten())
    local_mask = (lon[r_m, :] != fv_geo) & (lat[r_m, :] != fv_geo)
    r_b = np.stack((lon[r_m, local_mask], lat[r_m, local_mask])).T

    # left boundary
    l_m = max(x_ind[mask].flatten())
    local_mask = (lon[l_m, :] != fv_geo) & (lat[l_m, :] != fv_geo)
    l_b = np.stack((lon[l_m, local_mask], lat[l_m, local_mask])).T

    # top and bottom boundaries
    t_b = np.empty([0, 2])
    b_b = np.empty([0, 2])
    for ix in range(r_m + 1, l_m):
        local_mask = (lon[ix, :] != fv_geo) & (lat[ix, :] != fv_geo)
        local_y_ind = y_ind[ix, local_mask]
        y_ind_top = min(local_y_ind)
        y_ind_bottom = max(local_y_ind)
        t_b = np.append(t_b, [[lon[ix, y_ind_top], lat[ix, y_ind_top]]], axis=0)
        b_b = np.append(b_b, [[lon[ix, y_ind_bottom], lat[ix, y_ind_bottom]]], axis=0)

    # combining right, top, left, and bottom boundaries together, going along the combined boundary counterclockwise
    dpos = np.append(dpos, r_b[::-1, :], axis=0)  # this adds right boundary, counterclockwise
    dpos = np.append(dpos, t_b, axis=0)  # this adds top boundary, counterclockwise
    dpos = np.append(dpos, l_b, axis=0)  # this adds left boundary, counterclockwise
    dpos = np.append(dpos, b_b[::-1, :], axis=0)  # this adds bottom boundary, counterclockwise

    print("polygon shape: ", dpos.shape)

    return dpos



#main code starts here! 
auth = login(); 
print("enter period of interest, start and end dates, in the form YYYYMMDD")
datestamp_initial = input("enter start date of interest ")
datestamp_final = input("enter end date of interest ")

#For the tutorial demonstration, 20230805 was used for both the start and end date.
datetime_initial = datetime.strptime(datestamp_initial + "00:00:00.000000", "%Y%m%d%H:%M:%S.%f")
date_start = datetime_initial.strftime("%Y-%m-%d %H:%M:%S")

datetime_final = datetime.strptime(datestamp_final + "23:59:59.999999", "%Y%m%d%H:%M:%S.%f")
date_end = datetime_final.strftime("%Y-%m-%d %H:%M:%S")

print(date_start, date_end)

"""As of now, April 24, 2024, AERONET data cannot be downloaded programmatically. User must upload an 
AERONET data file using AERONET download tool here https://aeronet.gsfc.nasa.gov/new_web/webtool_aod_v3.html. 
The first line below is the name of the AERONET file used in this example."""

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

print(f"name {AERONET_name}, latitude {lat:>9.4f}, longitude {lon:>10.4f}")

nwl = len(wln)
for iwl in range(nwl):
    print(f"wavelength: {wln[iwl]}, length:{len(aod[aod[:, iwl] > 0, iwl])}")

out_Q_AERONET = "AOD_AERONET"
with open(
    f"{out_Q_AERONET}_{datestamp_initial}_{datestamp_final}_"
    f"{POI_name}_{POI_lat:>08.4f}N_{-POI_lon:>08.4f}W.txt",
    "w",
) as fout:
    fout.write(
        f"timeseries of {out_Q_AERONET} at {POI_name} {POI_lat:>08.4f}N {-POI_lon:>08.4f}W\n"
    )
    fout.write("yyyy mm dd hh mn ss time,days wl,nm    AOD wl,nm    AOD wl,nm    AOD\n")

    for i, datetime_row in enumerate(date_time):
        dt_AERONET = datetime.strptime(datetime_row[0] + datetime_row[1], "%d:%m:%Y%H:%M:%S")
        dt_loc = (dt_AERONET - datetime_initial).total_seconds() / 86400
        time_str = (
            f"{dt_AERONET.year} {dt_AERONET.month:>02} {dt_AERONET.day:>02} "
            f"{dt_AERONET.hour:>02} {dt_AERONET.minute:>02} {dt_AERONET.second:>02} "
            f"{dt_loc:>9.6f}"
        )
        fout.write(time_str)
        for wl, tau in zip(wln, aod[i]):
            fout.write(f" {wl:>5.0f} {max(tau, -1.0):>6.3f}")
        fout.write("\n")
        print(datetime_row, time_str, aod[i])

#work with DSCOVR data: 
short_name = "DSCOVR_EPIC_L2_AER"  # collection name to search for in the EarthData

bbox = (POI_lon - 0.5, POI_lat - 0.5, POI_lon + 0.5, POI_lat + 0.5)

POI_results_EPIC = earthaccess.search_data(
    short_name=short_name, temporal=(date_start, date_end), bounding_box=bbox
)

print(
    f"total number of DSCOVR EPIC L2_AER granules found for POI {POI_name}\n",
    f"within period of interest between {date_start} and {date_end} is {len(POI_results_EPIC)}",
)

#ensure all granules have download links: 
def get_url_value_from_result(earthaccess_result):
    """Return a tuple of the result itself and the data URL, only if the URL field is accessible."""
    try:
        return earthaccess_result, earthaccess_result["umm"]["RelatedUrls"][0]["URL"]
    except Exception:
        return None


# Populate the list of results that have links.
good_EPIC_result_links = [
    get_url_value_from_result(result)
    for result in POI_results_EPIC
    if get_url_value_from_result(result) is not None
]

# Show the result links
for r in sorted(good_EPIC_result_links, key=lambda x: x[1]):
    print(r[1])

#read DSCOVR EPIC granules and compile timeseries of AODs and UVAI 
# parameter geo_deviation defines maximum difference between lats and lons of EPIC pixels and that of AERONET
geo_deviation = 0.075
POI_coordinate = np.array([POI_lon, POI_lat])

out_Q_EPIC = "AOD_UVAI_EPIC"


def get_prod_loc(num_loc: int, lon_loc_array, lat_loc_array, values_loc, fill_value: float):
    if num_loc < 1:
        prod_loc = fill_value
    else:
        points = np.empty([0, 2])
        ff = np.empty(0)

        for i in range(num_loc):
            points = np.append(points, [[lon_loc_array[i], lat_loc_array[i]]], axis=0)
            ff = np.append(ff, values_loc[i])

        try:
            [prod_loc] = griddata(
                points, ff, POI_coordinate, method="linear", fill_value=fill_value, rescale=False
            )
        except Exception:
            try:
                prod_loc = np.mean(ff)
            except Exception:
                prod_loc = fill_value

    return prod_loc


with open(
    f"{out_Q_EPIC}_{datestamp_initial}_{datestamp_final}_{POI_name}_"
    f"{POI_lat:>08.4f}N_{-POI_lon:>08.4f}W.txt",
    "w",
) as fout:
    fout.write(f"timeseries of {out_Q_EPIC} at {POI_name} {POI_lat:>08.4f}N {-POI_lon:>08.4f}W\n")
    fout.write("yyyy mm dd hh mn ss time,days wl,nm    AOD wl,nm    AOD wl,nm    AOD UVAI\n")

    for _, granule_link in sorted(good_EPIC_result_links, key=lambda x: x[1]):
        EPIC_fname = granule_link.split("/")[-1]
        print(EPIC_fname)

        try:
            dscovr_arrays, dscovr_fill_values, dscovr_timestamp = read_epic_l2_AER(EPIC_fname)
        except Exception:
            print("Unable to find or read hdf5 input granule file ", EPIC_fname)
            continue

        dt_loc = (dscovr_timestamp - datetime_initial).total_seconds() / 86400
        time_str = (
            f"{dscovr_timestamp.year} {dscovr_timestamp.month:>02} {dscovr_timestamp.day:>02} "
            f"{dscovr_timestamp.hour:>02} {dscovr_timestamp.minute:>02} {dscovr_timestamp.second:>02} "
            f"{dt_loc:>9.6f}"
        )
        print(time_str)
        fout.write(time_str)

        # Check whether POI is in the granule. If not - move to the next granule.
        mask_geo = (
            (dscovr_arrays["lat2D"] < POI_lat + geo_deviation)
            & (dscovr_arrays["lat2D"] > POI_lat - geo_deviation)
            & (dscovr_arrays["lon2D"] < POI_lon + geo_deviation)
            & (dscovr_arrays["lon2D"] > POI_lon - geo_deviation)
        )

        for iwl in range(len(dscovr_arrays["wl"])):
            mask = mask_geo & (dscovr_arrays["aod3D"][:, :, iwl] > 0.0)
            lat_loc = dscovr_arrays["lat2D"][mask]
            lon_loc = dscovr_arrays["lon2D"][mask]
            aod_loc = dscovr_arrays["aod3D"][mask, iwl]

            prod_loc = get_prod_loc(len(aod_loc), lon_loc, lat_loc, aod_loc, fill_value=-0.999)

            fout.write(f" {dscovr_arrays['wl'][iwl]:>5.0f} {prod_loc:>6.3f}")
            print(dscovr_arrays["wl"][iwl], prod_loc)

        mask = mask_geo & (dscovr_arrays["uvai2D"] != dscovr_fill_values["uvai"])
        lat_loc = dscovr_arrays["lat2D"][mask]
        lon_loc = dscovr_arrays["lon2D"][mask]
        uvai_loc = dscovr_arrays["uvai2D"][mask]

        prod_loc = get_prod_loc(len(aod_loc), lon_loc, lat_loc, uvai_loc, fill_value=-99.0)

        fout.write(f" {prod_loc:>6.2f}\n")
        print("UVAI", prod_loc)


# Setting TEMPO name constants
short_name = "TEMPO_O3TOT_L2"  # collection name to search for in the EarthData
out_Q = "UVAI_TEMPO"  # name of the output quantity with unit
version = "V03"

# Searching TEMPO data files within 0.5 degree range around the POI
bbox = (POI_lon - 0.5, POI_lat - 0.5, POI_lon + 0.5, POI_lat + 0.5)

POI_results = earthaccess.search_data(
    short_name=short_name, version=version, temporal=(date_start, date_end), bounding_box=bbox
)
n_gr = len(POI_results)
print(
    f"Total number of TEMPO version {version} granules found for POI {POI_name}\n",
    f"within period of interest between {date_start} and {date_end} is {n_gr}.",
)

if n_gr == 0:
    print("program terminated")
    sys.exit()

# Print links to the granules.
tempo_granule_links = []
for result in POI_results:
    tempo_granule_links.append(result["umm"]["RelatedUrls"][0]["URL"])
for granule_link in tempo_granule_links:
    print(granule_link)

# Downloading TEMPO data files
# check whether all downloads were successful, try to download failed granules yet another time. 
# if second attempt fails, remove those granules from the list.
downloaded_files = earthaccess.download(POI_results, local_path=".")

with open(
    f"{out_Q}_{datestamp_initial}_{datestamp_final}_{POI_name}_"
    f"{POI_lat:>08.4f}N_{-POI_lon:>08.4f}W.txt",
    "w",
) as fout:
    fout.write(f"timeseries of {out_Q} at {POI_name} {POI_lat:>08.4f}N {-POI_lon:>08.4f}W\n'")
    fout.write("yyyy mm dd hh mn ss time,days   UVAI\n")
    print("Writing results to file.\n")

    POI_coordinate = np.array([POI_lon, POI_lat])
    POI_point = Point(POI_coordinate)

    for granule_link in sorted(tempo_granule_links):
        last_slash_ind = granule_link.rfind("/")
        tempo_file_name = granule_link[last_slash_ind + 1 :]
        print(f"\ngranule {tempo_file_name}")

        try:
            tempo, tempo_fv = read_TEMPO_O3TOT_L2_UVAI(tempo_file_name)
        except Exception:
            print(f"TEMPO UVAI cannot be read in file {tempo_file_name}")
            continue

        # Get time from the granule filename.
        # This time corresponds to the 1st element of array time above; that is GPS time in seconds.
        T_index = tempo_file_name.rfind("T")
        tempo_file_datetime = datetime.strptime(
            tempo_file_name[T_index - 8 : T_index + 7], "%Y%m%dT%H%M%S"
        )

        # Check whether POI is in the granule. If not - move to the next granule.
        tempo_polygon = Polygon(
            list(TEMPO_L2_polygon(tempo["lat"], tempo["lon"], tempo_fv["geo"]))
        )  # create granule polygon
        if not POI_point.within(tempo_polygon):
            continue
        print(f"point {POI_point} is in granule polygon.")

        POI_found = False
        for ix in range(tempo["lon"].shape[0] - 1):
            for iy in range(tempo["lon"].shape[1] - 1):

                def subarray(X_array):
                    return np.array(
                        [
                            X_array[ix, iy],
                            X_array[ix, iy + 1],
                            X_array[ix + 1, iy + 1],
                            X_array[ix + 1, iy],
                        ]
                    )

                lat_loc = subarray(tempo["lat"])
                lon_loc = subarray(tempo["lon"])

                coords_poly_loc = [
                    [lon_loc[0], lat_loc[0]],
                    [lon_loc[1], lat_loc[1]],
                    [lon_loc[2], lat_loc[2]],
                    [lon_loc[3], lat_loc[3]],
                ]
                if np.any(coords_poly_loc == tempo_fv["geo"]):
                    continue

                if POI_point.within(Polygon(coords_poly_loc)):
                    # Print the polygon coordinates within which this point has been found.
                    POI_found = True
                    print("scanl pixel latitude longitude UVAI UVAI_QF")
                    for scl in range(ix, ix + 2):
                        for pix in range(iy, iy + 2):
                            print(
                                "  %3d %4d %9.6f %10.6f %5.1f %6i"
                                % (
                                    scl,
                                    pix,
                                    tempo["lat"][scl, pix],
                                    tempo["lon"][scl, pix],
                                    tempo["uvai"][scl, pix],
                                    tempo["uvai_QF"][scl, pix],
                                )
                            )
                    print(f"POI {POI_name} at {POI_lat}N {POI_lon}E found")

                    # Get the values for this polygon.
                    uvai_loc = subarray(tempo["uvai"])
                    mask_noFV = uvai_loc != tempo_fv["uvai"]
                    points_noFV = np.column_stack((lon_loc[mask_noFV], lat_loc[mask_noFV]))
                    ff_noFV = uvai_loc[mask_noFV]

                    points = np.empty([0, 2])
                    ff = np.empty(0)

                    if ff_noFV.shape[0] == 0:
                        continue
                    elif ff_noFV.shape[0] < 4:
                        uvai_noFV = np.mean(ff_noFV)
                    elif ff_noFV.shape[0] == 4:
                        uvai_noFV = griddata(
                            points_noFV,
                            ff_noFV,
                            POI_coordinate,
                            method="linear",
                            fill_value=-99.0,
                            rescale=False,
                        )[0]
                    if uvai_noFV == -99.0:
                        continue

                    # Get the scanline time average, as the TEMPO time of observation in seconds since first scanline.
                    delta_t = timedelta(
                        seconds=(tempo["time"][ix + 1] + tempo["time"][ix]) * 0.5 - tempo["time"][0]
                    )
                    # Convert that delta of seconds into UTC timestamp, by adding those seconds to the filename's UTC timestamp.
                    mid_granule_datetime = tempo_file_datetime + delta_t

                    dt_loc = (mid_granule_datetime - datetime_initial).total_seconds() / 86400
                    time_and_uvai_str = (
                        f"{mid_granule_datetime.year} {mid_granule_datetime.month:>02} {mid_granule_datetime.day:>02} "
                        f"{mid_granule_datetime.hour:>02} {mid_granule_datetime.minute:>02} {mid_granule_datetime.second:>02} "
                        f"{dt_loc:>9.6f} {uvai_noFV:>10.3e}"
                    )
                    print(time_and_uvai_str)
                    fout.write(time_and_uvai_str)
                    fout.write(
                        f"{tempo['lat'][ix, iy]:>9.4f}N {-tempo['lon'][ix, iy]:>9.4f}W {tempo['uvai'][ix, iy]:>10.3e} "
                    )
                    fout.write(
                        f"{tempo['lat'][ix, iy + 1]:>9.4f}N {-tempo['lon'][ix, iy + 1]:>9.4f}W {tempo['uvai'][ix, iy + 1]:>10.3e} "
                    )
                    fout.write(
                        f"{tempo['lat'][ix + 1, iy + 1]:>9.4f}N {-tempo['lon'][ix + 1, iy + 1]:>9.4f}W {tempo['uvai'][ix + 1, iy + 1]:>10.3e} "
                    )
                    fout.write(
                        f"{tempo['lat'][ix + 1, iy]:>9.4f}N {-tempo['lon'][ix + 1, iy]:>9.4f}W {tempo['uvai'][ix + 1, iy]:>10.3e} "
                    )

                    break

            if POI_found:
                break

#plot results: 
print("reading from files for results...\n")
with open(
    f"{out_Q}_{datestamp_initial}_{datestamp_final}_{POI_name}_"
    f"{POI_lat:>08.4f}N_{-POI_lon:>08.4f}W.txt",
    "r",
) as fin:
    data_lines = fin.readlines()

timeseries_TEMPO_UVAI = np.empty([0, 2])
for data_line in data_lines[2:]:
    split = data_line.split()
    tt = float(split[6])
    TEMPO_UVAI = float(split[7])
    if TEMPO_UVAI > -99.0:
        timeseries_TEMPO_UVAI = np.append(timeseries_TEMPO_UVAI, [[tt, TEMPO_UVAI]], axis=0)

#plot UV aerosol index: 
print("Working on plotting results...")
plot_title = f"UVAI_{datestamp_initial}_{datestamp_final}\n{POI_name}"
img_name = f"UVAI_{datestamp_initial}_{datestamp_final}_{POI_name}.jpg"

plt.plot(
    timeseries_EPIC_UVAI[:, 0],
    timeseries_EPIC_UVAI[:, 1],
    label="UVAI EPIC",
    linestyle="None",
    markersize=2,
    marker="o",
    markerfacecolor="c",
    markeredgecolor="c",
)
plt.plot(
    timeseries_TEMPO_UVAI[:, 0],
    timeseries_TEMPO_UVAI[:, 1],
    label="UVAI TEMPO",
    linestyle="None",
    markersize=2,
    marker="o",
    markerfacecolor="m",
    markeredgecolor="m",
)

# Set the range of x-axis
l_lim = 0.0
u_lim = ((datetime_final - datetime_initial).total_seconds() + 1.0) / 86400.0
plt.xlim(l_lim, u_lim)

# Set the range of y-axis
l_lim = -3.0
u_lim = 3.0
plt.ylim(l_lim, u_lim)

plt.xlabel(r"GMT, day from beginning of " + datestamp_initial, fontsize=12)
plt.ylabel(r"UV Aerosol Index", fontsize=12)

plt.legend(loc="lower left")

plt.title(plot_title + str(", %08.4fN %08.4fW" % (POI_lat, -POI_lon)))
plt.savefig(img_name, format="jpg", dpi=300)

plt.close()