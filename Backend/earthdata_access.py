# earthdata_access.py
import earthaccess
import os

def login():
    auth = earthaccess.login(strategy="environment")
    return auth

def get_data(auth):
    session = auth.get_fsspec_session()
    # Example: download a file
    # session.get("https://example.earthdata.nasa.gov/file.nc", "file.nc")
    return "data downloaded"
