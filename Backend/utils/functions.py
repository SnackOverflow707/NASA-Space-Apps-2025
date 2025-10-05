import xarray as xr
import earthaccess
import pyrsig
import pandas as pd
import os
from datetime import datetime, timedelta
import gzip 

def login():
    auth = earthaccess.login(strategy="netrc")
    return auth

"""This requires users to create an netrc file with ~/.netrc and adding the following: 
machine urs.earthdata.nasa.gov
login YOUR_USERNAME
password YOUR_PASSWORD

I've found this is better than setting an environment variable, because I can't get that version to work. 
"""

def get_data(auth):
    session = auth.get_fsspec_session()
    # Example: download a file
    # session.get("https://example.earthdata.nasa.gov/file.nc", "file.nc")
    return "data downloaded"

def get_opendap_url(granule):
    related_urls = granule['umm']['RelatedUrls']
    print(related_urls)
    for url_info in related_urls:
        if url_info.get("Subtype") == "OPENDAP DATA":
            return url_info["URL"]
    return None  # if no OPeNDAP found



def get_no2(dataset: str): 

    if dataset[-3:] != ".nc":
        raise ValueError(f".nc file expected. Instead got filetype: {dataset[dataset.find(".") + 1:]}\n")
    # Load the file
    #ds = xr.open_dataset(dataset)
    ds = xr.open_dataset(dataset, engine="netcdf4")

    # Access the tropospheric NO2 column
    no2 = ds['NO2_VERTICAL_CO']
    print(no2[:10])


