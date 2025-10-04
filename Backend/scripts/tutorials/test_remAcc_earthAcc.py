import earthaccess

BBOX = 0.1

lon = -122.2
lat = 49.2
min_lon = lon - BBOX
max_lon = lon + BBOX
min_lat = lat - BBOX
max_lat = lat + BBOX

bbox = (min_lon, min_lat, max_lon, max_lat)
print(bbox)

min_date = input("Enter start date (format yyyy-mm-dd): ") #Dates can be datetime objects or ISO 8601 formatted strings. 
max_date = input("Enter end date (format yyyy-mm-dd): ")

results = earthaccess.search_data(
    #short_name='TEMPO_NO2_L2_V03',
    short_name="TEMPO_NO2_L2", 
    version="V04",  
    #doi="10.5067/IS-40e/TEMPO/NO2_NRT_L2", 
    bounding_box=bbox,  
    temporal=(min_date, max_date),
    count=3
)
#Returns: a list of DataGranules that can be used to access the granule files by using download() or open()
print(results)





#granules = earthaccess.search_data(
#    short_name="ATL06",
#    bounding_box=(-46.5, 61.0, -42.5, 63.0),
#    count=2
#)

#print(granules)
