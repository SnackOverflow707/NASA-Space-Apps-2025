import { useState, useEffect } from "react";

export function useUserCoordinates() {
  const [coords, setCoords] = useState(null);

  useEffect(() => {
    const getCoordsFromCity = async (cityName) => {
      try {
        const response = await fetch(
          `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(cityName)}&count=1`
        );
        const data = await response.json();
        if (data.results && data.results.length > 0) {
          const { latitude, longitude } = data.results[0];
          setCoords({ latitude, longitude });
        } else {
          alert("City not found. Please try again.");
        }
      } catch (err) {
        console.error(err);
        alert("Failed to get coordinates for city.");
      }
    };

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setCoords({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          });
        },
        (error) => {
          console.warn("Geolocation failed:", error);
          const city = prompt("Enter your city:");
          if (city) getCoordsFromCity(city);
        }
      );
    } else {
      const city = prompt("Geolocation not supported. Enter your city:");
      if (city) getCoordsFromCity(city);
    }
  }, []);

  return coords; // null until coordinates are set

}

