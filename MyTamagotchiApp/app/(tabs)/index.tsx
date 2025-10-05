import { Image } from 'expo-image';
import { Modal, Platform, StyleSheet, TouchableOpacity, Text, View, SwitchProps, Easing } from 'react-native';
import ParallaxScrollView from '@/components/parallax-scroll-view';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { IconSymbol } from '@/components/ui/icon-symbol';
import { Fonts } from '@/constants/theme';
import { Ionicons } from '@expo/vector-icons';
import React, { useState, useEffect } from 'react';
import happyImg from '../../assets/images/tamagachi-guys/regular.png';
import sadImg from '../../assets/images/tamagachi-guys/pollutants.png';
import lpaImg from '../../assets/images/tamagachi-guys/couch.png';
import reImg from '../../assets/images/tamagachi-guys/house.png';
import maskImg from '../../assets/images/tamagachi-guys/mask.png'; 
import button0icon from '../../assets/images/refresh.png';
import button1icon from '../../assets/images/mask-icon.png'
import button2icon from '../../assets/images/reduce-exposure.png';
import button3icon from '../../assets/images/couch.png';
import aqiverygood from '../../assets/images/widgets/verygood.jpg';
import aqigood from '../../assets/images/widgets/good.jpg';
import aqifair from '../../assets/images/widgets/fair.jpg';
import aqipoor from '../../assets/images/widgets/poor.jpg';
import aqiverypoor from '../../assets/images/widgets/verypoor.jpg';
import aqihazardous from '../../assets/images/widgets/hazardous.jpg';
import surpriseButton from '../../assets/images/surprise.jpg'; 
import cloudImg from '../../assets/images/cloudicon.png';
import { useUserCoordinates } from '../../components/get_usr_loc'; 
import { ImageBackground } from 'react-native';
import { getProtectionFlags, getImageProtection, getImageSpeech } from "./bird_functions";
import { sendCoordsToBackend, getAqiBackgroundImage } from "./data_functions"
import { LoadingMessage, AqiCardPopup, ImageWithLoadingBackground } from "./widget_functions"


type ImageName = 'happy' | 'sad' | 'lpa' | 're' | 'mask';

export default function TabTwoScreen() {
  // --- State for the Tamagotchi image ---
  const [currentImage, setCurrentImage] = useState(happyImg);

  // --- State for the pop-up window ---
  const [modalVisible, setModalVisible] = useState(false);

  //Variable for if user is susceptible to pollution
  const [susceptible, setSusceptible] = useState(false);

  const coords = useUserCoordinates(); 
  const [aqi, setAqi] = useState<number | null>(null);
  const [weather, setWeather] = useState<any>(null); 
  const [pollutants, setPollutants] = useState<any>(null); 
  const [error, setError] = useState<string | null>(null);
  const [speechText, setSpeechText] = useState("Hello! I'm a bird!");
  const [surpriseData, setSurpriseData] = useState(null);

  // Fetch backend data when coordinates change
  useEffect(() => {
    const fetchData = async () => {
      if (coords?.latitude && coords?.longitude) {
        try {
          const data = await sendCoordsToBackend(coords);
          // Assuming sendCoordsToBackend returns the response data
          if (data.aqi !== undefined) {
            setAqi(data.aqi);
            setError(null);
          
            // Set weather data
          if (data.weather) {
            setWeather(data.weather);
            console.log('Weather data:', data.weather);
          }

          if (data.pollutants) {
            setPollutants(data.pollutants)
            console.log('Pollutant data: ', data.pollutants)
          }
        }
        } catch (err) {
          console.error('Failed to fetch data:', err);
          setError('Failed to fetch AQI data');
        }
      }
    };

    fetchData();
  }, [coords?.latitude, coords?.longitude]);

    // Update speech text when AQI or susceptibility changes
  useEffect(() => {
    if (aqi !== null) {
      // Update speech for current image based on new AQI
      const currentImageName = getCurrentImageName();
      setSpeechText(getImageSpeech(currentImageName, aqi, susceptible));
    }
  }, [aqi, susceptible]);

    // Helper function to get current image name
  const getCurrentImageName = (): ImageName => {
    const imageMap: Record<string, ImageName> = {
      [happyImg]: 'happy',
      [sadImg]: 'sad',
      [lpaImg]: 'lpa',
      [reImg]: 're',
      [maskImg]: 'mask',
    };
    return imageMap[currentImage] || 'happy';
  };

const surpriseMe = async () => {
  try {
    const response = await fetch("http://localhost:5001/surprise", {
      method: "POST",  // Add this!
      headers: {
        "Content-Type": "application/json",
      },
    });
    const result = await response.json();
    console.log("Surprise me button --> city ", result.city);
    setSurpriseData(result); 
  } catch (error) {
    console.error("Error fetching data:", error);
  }
};



  // --- Function to switch images ---
  const showImage = (imageName: ImageName) => {
    // If user asked for "happy", decide dynamically
    if (imageName === "happy") {
      const aqiFlags = getProtectionFlags(aqi ?? 0, susceptible);
      const allFlagsTrue = (aqiFlags.mask === false && aqiFlags.reducedActivity === false && aqiFlags.stayIndoors === false);
      const moodImage = allFlagsTrue ? happyImg : sadImg;
      setCurrentImage(moodImage);
      setSpeechText(getImageSpeech(allFlagsTrue ? "happy" : "sad", aqi, susceptible));
      return;
    }
  
    // Otherwise use static mapping
    const map: Record<ImageName, any> = {
      happy: happyImg,
      sad: sadImg,
      lpa: lpaImg,
      re: reImg,
      mask: maskImg,
    };
  
    setCurrentImage(map[imageName]);
    setSpeechText(getImageSpeech(imageName, aqi, susceptible));
  };
  

  // --- Button icons and actions ---
  const buttonIcons = [button0icon, button1icon, button2icon, button3icon];
  const ButtonNames: ImageName[] = ['happy','mask', 're', 'lpa'];


return (
    <ParallaxScrollView
      headerImage={<ThemedView style={{ height: 0, backgroundColor: 'transparent' }} />}
      headerBackgroundColor={{ light: 'transparent', dark: 'transparent' }}
      //headerHeight={10}
    >
      {/* --- Your mockup starts here --- */}
      <ThemedView style={styles.imageBox}>
        <Image source={currentImage} style={styles.image} />
        {/* --- Speech Bubble --- */}
        {speechText && (
          <ThemedView style={styles.speechBubble}>
            <ThemedText style={styles.speechText}>{speechText}</ThemedText>
            <ThemedView style={styles.speechArrow} />
          </ThemedView>
         )}
        <TouchableOpacity style={styles.editButton}
         onPress={() =>{console.log('Edit button pressed'); setModalVisible(true)}}>
          <Ionicons name="information-circle-outline" size={28} color="black" />
        </TouchableOpacity>
        {/* Susceptible circle indicator */}
          {susceptible && (
          <ThemedView style={styles.susceptibleCircle}>
          <ThemedText style={styles.susceptibleText}>susceptible</ThemedText>
          </ThemedView>
        )}    
      </ThemedView>

      {/* Buttons to switch images */}
      <ThemedView style={styles.circleRow}>
       {buttonIcons.map((icon, index) => (
          <TouchableOpacity
            key={index}
            style={styles.circleButton}
            onPress={() => showImage(ButtonNames[index])}
          >
            <Image 
            source={icon} 
            style={{ width: 30, height: 30, resizeMode: 'contain' }} />
          </TouchableOpacity>
        ))}
      </ThemedView>
      
  {/* Buttons stacked vertically */}
  {/* --- Square with Buttons beside it --- */}
 
  
<ThemedView style={styles.squareRow}>
  <ImageWithLoadingBackground aqi={aqi} error={error} imageSource = {getAqiBackgroundImage(aqi, aqiverygood, aqigood, aqifair, aqipoor, aqiverypoor, aqihazardous)!}/>
 {/*<AqiCardPopup aqi={aqi} error={error} /> */}
 {/* 
  <ImageBackground
    source={getAqiBackgroundImage(aqi, aqiverygood, aqigood, aqifair, aqipoor, aqiverypoor, aqihazardous)!}
    style={styles.squareBackgroundImage} // container dimensions
    imageStyle={{ borderRadius: 20 }} // round corners of the image
  >
<ThemedView style={styles.textContainer}>
  {error ? (
    <ThemedText style={styles.squareText}>{error}</ThemedText>
  ) : aqi !== null ? (
    <ThemedText style={styles.squareText}>
      Current Air Quality Index: {'\n\n'}
      <ThemedText style={styles.aqiValue}>{aqi}</ThemedText>
    </ThemedText>
  ) : (
    <LoadingMessage/>
  )}
</ThemedView> 
  </ImageBackground> */}

    {/* Random buttons beside the square */}
    <ThemedView style={styles.buttonColumn}>
      <TouchableOpacity style={styles.sideButton}>
        <Image
          source={cloudImg}
          style={styles.backgroundIcon}
        />
        <ThemedText style={styles.buttonText}>
          {weather?.current?.temp
            ? `Temperature: ${Math.round(weather.current.temp)}°C`
            : "Temp"}
        </ThemedText>
      </TouchableOpacity>

      <TouchableOpacity style={styles.sideButton}>
        <Image
          source={cloudImg}
          style={styles.backgroundIcon}
        />
        <ThemedText style={styles.buttonText}>
          {weather?.current?.precipitation != null
            ? `Precipitation: ${Math.round(weather.current.precipitation)}mm`
            : "Precipitation"}
        </ThemedText>
      </TouchableOpacity>

      <TouchableOpacity style={styles.sideButton}>
        <Image
          source={cloudImg}
          style={styles.backgroundIcon}
        />
        <ThemedText style={styles.buttonText}>Button C</ThemedText>
      </TouchableOpacity>
    </ThemedView>

{/*surprise me button!*/} 
<ThemedView> 
  <TouchableOpacity onPress={surpriseMe} style={styles.surpriseMe}>
    <ImageBackground
      source={surpriseButton}
      style={styles.surpriseMe}
      imageStyle={{ borderRadius: 20 }}>
      <ThemedText style={styles.buttonText}>Surprise Me!</ThemedText>
    </ImageBackground>
  </TouchableOpacity>
  </ThemedView>

</ThemedView>


      {/* Modal for more information */}
{/* Modal popup */}
<Modal
  transparent={true}
  visible={modalVisible}
  animationType="fade"
  onRequestClose={() => setModalVisible(false)}
>
  <ThemedView style={styles.modalBackground}>
    <ThemedView style={styles.modalContainer}>
    <ThemedText style={styles.modalQuestion}>
  Are you susceptible to airborne pollutants?
</ThemedText>

<ThemedText style={styles.modalSubText}>
  Susceptible populations include children under 5, adults over 60 and 
  individuals with obesity, diabetes, hypertension, pulmonary disease, 
  or atherosclerotic cardiovascular disease.
</ThemedText>

      {/* Two buttons row */}
      <ThemedView style={styles.buttonRow}>
        <TouchableOpacity
          style={styles.modalButton}
          onPress={() => {
            console.log('Button 1 pressed');
            setSusceptible(true);
            setModalVisible(false);
          }}
        >
          <ThemedText style={{ color: 'white' }}>Yes</ThemedText>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.modalButton}
          onPress={() => {
            console.log('Button 2 pressed');
            setSusceptible(false);
            setModalVisible(false);
          }}
        >
          <ThemedText style={{ color: 'white' }}>No</ThemedText>
        </TouchableOpacity>
      </ThemedView>
    </ThemedView>
  </ThemedView>
</Modal>
      
      {/* --- Your mockup ends here --- */}
</ParallaxScrollView>
); 
}


//------ styles ----------//

const styles = StyleSheet.create({
  headerImage: {
    color: '#808080',
    bottom: -90,
    left: -35,
    position: 'absolute',
  },
  imageBox: {
    width: '90%',
    height: 200,
    backgroundColor: '#dfe9f3',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
    alignSelf: 'center',
    position: 'relative',
  },
  image: {
    width: '80%',
    height: '80%',
    resizeMode: 'contain',
  },
  editButton: {
    position: 'absolute',
    top: 10,
    right: 10,
    backgroundColor: 'white',
    borderRadius: 20,
    padding: 5,
    elevation: 3,
  },
  circleRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 20,
    gap: 8,
  },
  circleButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#bcd4e6',
    marginHorizontal: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  dataButton: {
    width: '90%',
    padding: 15,
    backgroundColor: '#cfe0f4',
    borderRadius: 10,
    marginVertical: 8,
    alignSelf: 'center',
    alignItems: 'center',
  },
  dataText: {
    fontSize: 16,
    fontWeight: '600',
  },
  modalBackground: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContainer: {
    width: 280,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
  },
  modalText: { marginBottom: 20, textAlign: 'center', fontSize: 16 },
  switchRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 20 },
  closeButton: {
    backgroundColor: '#2196F3',
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 16,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    gap: 10,
  },
  modalButton: {
    flex: 1,
    backgroundColor: '#2196F3',
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: 'center',
  },

surpriseMe: {
  marginTop: 20,
  marginLeft: 60, 
  width: 300,
  height: 200,
  padding: 15,
  borderRadius: 8,
  alignItems: 'center',
  justifyContent: 'center', 
},

  modalQuestion: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
    textAlign: 'center',
  },
  modalSubText: {
    fontSize: 14,
    color: '#555',
    textAlign: 'center',
  },
  susceptibleCircle: {
    width: 80,
    height: 25,
    borderRadius: 12.5,
    backgroundColor: '#FF4747',
    position: 'absolute',
    bottom: 10,
    right: 10,
    borderWidth: 2,
    borderColor: 'white', // makes it stand out
  },
  susceptibleText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
    textAlign: 'center'
  },

  imageRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 16,
    marginBottom: 20,
  },
  
  bigImageBox: {
    width: 250,
    height: 250,
    backgroundColor: '#e8f1f8',
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
  },
  aqiValue: {
    fontSize: 40,        // Larger font for AQI value
    fontFamily: Platform.select({
      ios: 'Avenir Next Rounded',
      android: 'sans-serif',
      default: 'System',
    }),
    fontWeight: 200,  
  },
  
  bigImage: {
    width: '85%',
    height: '85%',
    resizeMode: 'contain',
  },
  
  sideButtons: {
    flexDirection: 'column',
    justifyContent: 'space-around',
    alignItems: 'center',
    height: 250,
  },
  
  sideButton: {
    width: 225,
    height: 60,
    backgroundColor: '#76b6e8ff',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 2,
  },
  backgroundIcon: {
    width: 225,
    height: 60,
    position: 'absolute',
  },

  squareRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 20,
    marginVertical: 30,
  },

squareBackgroundImage: {
  width: 200,
  height: 300,
  justifyContent: 'center', // centers children vertically
  alignItems: 'center',     // centers children horizontally
},

textContainer: {
  justifyContent: 'center',
  alignItems: 'center',
  textAlign: 'center', // ensures text is centered
  backgroundColor: 'transparent',
},

squareText: {
  fontSize: 20,
  //fontWeight: '800',  // Extra bold makes it more playful
  fontFamily: Platform.select({
    ios: 'Avenir Next Rounded',
    android: 'sans-serif',
    default: 'System',
  }),
  //fontFamily: 'System',  // Clean and readable
  fontWeight: '400',
  color: '#333',
  textAlign: 'center', // crucial for multi-line text
  zIndex: 1,
  textShadowColor: 'rgba(255, 255, 255, 0.8)',
  textShadowOffset: { width: 0, height: 1 },
  textShadowRadius: 3,
},
  
  bigSquare: {
    width: 200,
    height: 200,
    justifyContent: 'center',
    alignItems: 'center',
  },
  
  buttonColumn: {
    flexDirection: 'column',
    justifyContent: 'space-between',
    alignItems: 'center',
    height: 230,
    marginLeft: 80,
  },
  
  
  buttonText: {
    fontSize: 16,
    fontFamily: Platform.select({
      ios: 'Avenir Next Rounded',
      android: 'sans-serif',
      default: 'System',
    }),
    fontWeight: '300',
    color: '#333',
  },


  //Speech bubble style
  speechBubble: {
    position: 'absolute',
    top: '5%',       // vertically aligned with the bird
    left: '55%',      // push to the right side inside the imageBox
    width: 120,
    backgroundColor: 'white',
    padding: 6,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#ccc',
    alignItems: 'center',
    zIndex: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
  },
  
  speechText: {
    fontSize: 12,
    color: '#333',
    textAlign: 'center',
  },
  
  speechArrow: {
    position: 'absolute',
    bottom: -6,
    left: 10,
    width: 0,
    height: 0,
    borderLeftWidth: 6,
    borderRightWidth: 6,
    borderTopWidth: 6,
    borderBottomWidth:0,
    borderLeftColor: 'transparent',
    borderRightColor: 'transparent',
    borderTopColor: 'white',
    borderBottomColor: 'transparent',
    backgroundColor: 'transparent',
  }
  
});

