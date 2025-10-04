
import './App.css';
import happyImg from "tamagachi guys/happy.png";
import sadImg from "tamagachi guys/sad.png";
import lpaImg from "tamagachi guys/lpa.png";
import reImg from "tamagachi guys/re.png";
import maskImg from "tamagachi guys/mask.png";

import React, { useState } from "react";

export default function AirTamagotchi() {
  //Variable declarations: will need to be API filled
  const maskNeeded = airQualityIndex > 100; 
  const lowExertion = airQualityIndex > 50;
  const reduceExposure = airQualityIndex > 75;
  const climateAreas = airQualityIndex > 150;

  var airQualityIndex = 75; // Filler value (will be replaced with API data)
  var happinessLevel = 50;

  //Get picture based on mood
  const getImage = () => {
    switch (mood) {
      case "happy":
        return happyImg;
      case "sad":
        return sadImg;
      case "mask":
        return maskImg;
      case "lpa":
        return lpaImg;
      case "re":
          return reImg;
      default:
        return happyImg;
    }
  };

  

}