import { Image } from 'expo-image';
import { Modal, Platform, StyleSheet, TouchableOpacity, Text, View, SwitchProps } from 'react-native';
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
import { useUserCoordinates } from '../../components/get_usr_loc'; 
import { ImageBackground } from 'react-native';

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
  const [aqiRating, setAqiRating] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // --- Function to send coordinates to backend ---
  const sendCoordsToBackend = async () => {
    console.log("Current coords:", coords);

    if (!coords) {
      console.log("Coords not available yet.");
      return;
    }

    try {
      console.log("Sending request to backend...");

      //Changed port from 8081 to 5000
      const response = await fetch('http://localhost:5001/aqi', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          latitude: coords.latitude,
          longitude: coords.longitude,
        }),
      });

      console.log("Response received:", response);

      //Check if response is ok before parsing JSON
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Data received from backend:", data);

      if (data.aqi !== undefined) {
        console.log("Setting AQI:", data.aqi);
        setAqi(data.aqi);
        setError(null);
        
        // Also set the rating if available
        if (data.rating) {
          setAqiRating(data.rating);
        }
      } else {
        console.log("AQI not found in response:", data);
        setError("AQI data not available");
      }
    } catch (error) {
      console.error('Failed to send coordinates:', error);
      setError('Failed to fetch AQI data');
    }
  };

  useEffect(() => {
    if (coords?.latitude && coords?.longitude) {
      sendCoordsToBackend();
    }
  }, [coords?.latitude, coords?.longitude]); // Only re-run when lat/lon actually changes


  // --- Function to switch images ---
  const showImage = (imageName: ImageName) => {
    const map: Record<ImageName, any> = {
      happy: happyImg,
      sad: sadImg,
      lpa: lpaImg,
      re: reImg,
      mask: maskImg,
    };
    setCurrentImage(map[imageName]);
  };

  //function to select aqi widget background 
  const getAqiBackgroundImage = (aqiValue: number | null) => {
    if (aqiValue === null) return null;
    
    if (aqiValue <= 33) return aqiverygood;           // Good
    if (aqiValue <= 67) return aqigood;      // Moderate
    if (aqiValue <= 100) return aqifair;     // Unhealthy for Sensitive Groups
    if (aqiValue <= 150) return aqipoor; // Unhealthy
    if (aqiValue <= 200) return aqiverypoor;
    return aqihazardous;                           // Very Unhealthy/Hazardous
  };

  // --- Button icons and actions ---
  const buttonIcons = [button0icon, button1icon, button2icon, button3icon];
  const ButtonNames: ImageName[] = ['happy','mask', 're', 'lpa'];

  return (
    <ParallaxScrollView
      headerBackgroundColor={{ light: '#D0D0D0', dark: '#353636' }}
      headerHeight={10}
    >
      {/* --- Your mockup starts here --- */}
      <ThemedView style={styles.imageBox}>
        <Image source={currentImage} style={styles.image} />
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
  <ImageBackground
    source={getAqiBackgroundImage(aqi)!}
    style={styles.squareBackgroundImage} // container dimensions
    imageStyle={{ borderRadius: 20 }} // round corners of the image
  >
    <ThemedView style={styles.textContainer}>
      <ThemedText style={styles.squareText}>
        {error ? error : aqi !== null ? `Current Air Quality Index: ${aqi}` : "Loading AQI..."}
      </ThemedText>
      {aqiRating && (
        <ThemedText style={styles.squareText}>
          Rating: {aqiRating}
        </ThemedText>
      )}
    </ThemedView>
  </ImageBackground>
</ThemedView>



  {/* Random buttons beside the square */}
  <ThemedView style={styles.buttonColumn}>
    <TouchableOpacity style={styles.sideButton}>
      <ThemedText style={styles.buttonText}>Button A</ThemedText>
    </TouchableOpacity>
    <TouchableOpacity style={styles.sideButton}>
      <ThemedText style={styles.buttonText}>Button B</ThemedText>
    </TouchableOpacity>
    <TouchableOpacity style={styles.sideButton}>
      <ThemedText style={styles.buttonText}>Button C</ThemedText>
    </TouchableOpacity>
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
    width: 70,
    height: 40,
    backgroundColor: '#bcd4e6',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 2,
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
    //backgroundColor: '#f7cad0', // soft pastel red
    //borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    //shadowColor: '#000',
    //shadowOpacity: 0.1,
    //shadowRadius: 6,
    //hadowOffset: { width: 0, height: 3 },
  },
  
  buttonColumn: {
    flexDirection: 'column',
    justifyContent: 'space-between',
    alignItems: 'center',
    height: 200,
  },
  
  
  buttonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  
});

