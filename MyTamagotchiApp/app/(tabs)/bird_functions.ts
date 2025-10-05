   
  
  // --- Function to figure out which methods work--
export const getProtectionFlags = (aqi: number, susceptible = false) => {
  if (aqi >= 301) {
    return { mask: true, reducedActivity: false, stayIndoors: true };
  } else if (aqi >= 201) {
    return susceptible
      ? { mask: true, reducedActivity: false, stayIndoors: true }
      : { mask: true, reducedActivity: true, stayIndoors: false };
  } else if (aqi >= 151) {
    return { mask: true, reducedActivity: true, stayIndoors: false };
  } else if (aqi >= 101) {
    return { mask: susceptible, reducedActivity: susceptible, stayIndoors: false };
  } else if (aqi >= 51) {
    return { mask: false, reducedActivity: susceptible, stayIndoors: false };
  } else if (aqi >= 0) {
    return { mask: false, reducedActivity: false, stayIndoors: false };
  } else {
    return { mask: false, reducedActivity: false, stayIndoors: false };
  }
};

// --- Returns protection level of an image ---
export const getImageProtection = (imageName, susceptible = false) => {
  switch(imageName) {
    case "mask":
      return { mask: true, reducedActivity: false, stayIndoors: false, polluted: false };
    case "lpa": // e.g., "limited physical activity"
      return        { mask: false, reducedActivity: true, stayIndoors: false, polluted: false  };
    case "re": // e.g., "resting / indoors"
      return { mask: false, reducedActivity: false, stayIndoors: true, polluted: false  };
    case "happy": // normal state
    case "sad":
      return { mask: false, reducedActivity: false, stayIndoors: false, polluted: true  };
    default:
      return { mask: false, reducedActivity: false, stayIndoors: false };
  }
};

// --- Generate speech bubble text based on image, AQI, and susceptibility ---
export const getImageSpeech = (imageName, aqi, susceptible = false) => {
  if (aqi === null) return "Loading AQI...";

  const imageFlags = getImageProtection(imageName, susceptible);

  // Recommended protection based on AQI
  const aqiFlags = getProtectionFlags(aqi, susceptible);

  const parts = [];

  if (!aqiFlags.mask && imageFlags.mask) parts.push("A mask isn't nessary right now");
  if (!aqiFlags.reducedActivity && imageFlags.reducedActivity && aqiFlags.stayIndoors) parts.push("Even with reduced activity, I still feel the effects of air pollution");
  if (!aqiFlags.reducedActivity && imageFlags.reducedActivity && !aqiFlags.stayIndoors) parts.push("I don't need to reduce my activity right now");
  if (!aqiFlags.stayIndoors && imageFlags.stayIndoors &&(aqiFlags.mask || aqiFlags.reducedActivity)) parts.push("It is safe to leave the house, with proper precautions");
  if (!aqiFlags.stayIndoors && imageFlags.stayIndoors && !(aqiFlags.mask || aqiFlags.reducedActivity)) parts.push("It is safe to leave the house!");
  if (imageFlags.polluted )parts.push("The air pollution is affecting me");
  if (parts.length === 0) return "Thanks for taking care of me!";

  return parts.join(" | ");
};