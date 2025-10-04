
class ValidCoords:
    
    MIN_LON = -130  # west
    MAX_LON = -60   # east
    MIN_LAT = 15    # south
    MAX_LAT = 60    # north

    def __init__(self, longitude, latitude):
        if longitude < self.MIN_LON:
            raise ValueError(f"Longitude must be >= {self.MIN_LON} deg.")
        if longitude > self.MAX_LON:
            raise ValueError(f"Longitude must be <= {self.MAX_LON} deg.")
        if latitude < self.MIN_LAT:
            raise ValueError(f"Latitude must be >= {self.MIN_LAT} deg.")
        if latitude > self.MAX_LAT:
            raise ValueError(f"Latitude must be <= {self.MAX_LAT} deg.")

        self.lon = longitude
        self.lat = latitude

        


    

    
        