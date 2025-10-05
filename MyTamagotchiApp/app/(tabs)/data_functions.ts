  // --- Function to send coordinates to backend ---
export const sendCoordsToBackend = async (coords: any) => {
  const response = await fetch('http://localhost:5001/get_data', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      latitude: coords.latitude,
      longitude: coords.longitude,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return {
    aqi: data.aqi,
    weather: data.current_weather,  // Extract weather data
    pollutants: data.pollutants
  };
  
  // Return the data so it can be used
};

//function to select aqi widget background
export const getAqiBackgroundImage = (aqiValue: number | null, aqiverygood, aqigood, aqifair, aqipoor, aqiverypoor, aqihazardous) => {
    
    if (aqiValue === null) return null;    
    if (aqiValue <= 33) return aqiverygood;           // Good
    if (aqiValue <= 67) return aqigood;      // Moderate
    if (aqiValue <= 100) return aqifair;     // Unhealthy for Sensitive Groups
    if (aqiValue <= 150) return aqipoor; // Unhealthy
    if (aqiValue <= 200) return aqiverypoor;
    return aqihazardous;                           // Very Unhealthy/Hazardous
  };

