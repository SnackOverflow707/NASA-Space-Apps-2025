
class ValidCoords:
    
    MIN_LON = -130  # west
    MAX_LON = -60   # east
    MIN_LAT = 15    # south
    MAX_LAT = 60    # north

    def __init__(self, longitude, latitude):

        if not isinstance(longitude, (int, float)):
            raise TypeError("Longitude must be a number (int or float)")
        if not isinstance(latitude, (int, float)): 
            raise TypeError("Latitude must be a number (int or float)")

        self.validate_coords(longitude, latitude)
        
        self.lon = longitude
        self.lat = latitude

    def validate_coords(self, longitude, latitude): 

        if longitude < self.MIN_LON:
            raise ValueError(f"Longitude must be >= {self.MIN_LON} deg.")
        if longitude > self.MAX_LON:
            raise ValueError(f"Longitude must be <= {self.MAX_LON} deg.")
        if latitude < self.MIN_LAT:
            raise ValueError(f"Latitude must be >= {self.MIN_LAT} deg.")
        if latitude > self.MAX_LAT:
            raise ValueError(f"Latitude must be <= {self.MAX_LAT} deg.")
        
    def print_coords(self): 
        print(f"Latitude: {self.lat}; longitude: {self.lon}\n")
        


    

    
        