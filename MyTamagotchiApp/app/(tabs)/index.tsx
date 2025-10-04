import { Image } from 'expo-image';
import { Modal, Platform, StyleSheet, TouchableOpacity, Text, View, SwitchProps } from 'react-native';
import ParallaxScrollView from '@/components/parallax-scroll-view';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { IconSymbol } from '@/components/ui/icon-symbol';
import { Fonts } from '@/constants/theme';
import { Ionicons } from '@expo/vector-icons';
import React, { useState } from 'react';
import happyImg from '../../assets/images/tamagachi-guys/happy.png';
import sadImg from '../../assets/images/tamagachi-guys/sad.png';
import lpaImg from '../../assets/images/tamagachi-guys/lpa.png';
import reImg from '../../assets/images/tamagachi-guys/re.png';
import maskImg from '../../assets/images/tamagachi-guys/mask.png'; 
import button0icon from '../../assets/images/mask-icon.png';
import button1icon from '../../assets/images/limit-outdoor.png';
import button2icon from '../../assets/images/reduce-exposure.png';
import button3icon from '../../assets/images/white-coach.png';

type ImageName = 'happy' | 'sad' | 'lpa' | 're' | 'mask';

export default function TabTwoScreen() {
  // --- State for the Tamagotchi image ---
  const [currentImage, setCurrentImage] = useState(happyImg);

  // --- State for the pop-up window ---
  const [modalVisible, setModalVisible] = useState(false);

  //Variable for if user is susceptible to pollution

  const [susceptible, setSusceptible] = useState(false);


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

  // --- Button icons and actions ---
  const buttonIcons = [button0icon, button1icon, button2icon, button3icon];
  const ButtonNames: ImageName[] = ['happy', 'sad', 'lpa', 're', 'mask'];

  return (
    <ParallaxScrollView
      headerBackgroundColor={{ light: '#D0D0D0', dark: '#353636' }}
      headerImage={
        <IconSymbol
          size={310}
          color="#808080"
          name="chevron.left.forwardslash.chevron.right"
          style={styles.headerImage}
        />
      }
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
      
      {/* Data buttons */}
      <TouchableOpacity style={styles.dataButton}>
        <ThemedText style={styles.dataText}>Data 1 (navigate)</ThemedText>
      </TouchableOpacity>
      <TouchableOpacity style={styles.dataButton}>
        <ThemedText style={styles.dataText}>Data 2 (navigate)</ThemedText>
      </TouchableOpacity>
      <TouchableOpacity style={styles.dataButton}>
        <ThemedText style={styles.dataText}>Data 3 (navigate)</ThemedText>
      </TouchableOpacity>
      
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
});

