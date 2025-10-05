import React, { useEffect, useRef, useState } from 'react';
import { TouchableOpacity, Image, ImageBackground, Text, View, StyleSheet, Modal } from 'react-native';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { getAqiBackgroundImage } from './data_functions';
import aqiverygood from '../../assets/images/widgets/verygood.jpg';
import aqigood from '../../assets/images/widgets/good.jpg';
import aqifair from '../../assets/images/widgets/fair.jpg';
import aqipoor from '../../assets/images/widgets/poor.jpg';
import aqiverypoor from '../../assets/images/widgets/verypoor.jpg';
import aqihazardous from '../../assets/images/widgets/hazardous.jpg';

export const LoadingMessage = () => {
  const messages = [
    "Counting the happy particles...", 
    "Waking up the clouds...", 
    "Checking on the invisible stuff..."
  ] as const; 

  const [index, setIndex] = useState(0);

    useEffect(() => {
    const interval: number = setInterval(() => {
        setIndex((prevIndex) => (prevIndex + 1) % messages.length);
    }, 7000) as unknown as number;

    return () => clearInterval(interval);
    }, []);

  return <Text style={{ fontSize: 18, justifyContent: 'center', alignItems: 'center',textAlign: 'center' }}>{messages[index]}</Text>;
};





interface Props {
  aqi: number | null;
  error?: string | null;
}

export function AqiCardPopup({ aqi, error }: Props) {
  const [modalVisible, setModalVisible] = useState(false);

  return (
    <>
      <TouchableOpacity onPress={() => setModalVisible(true)}>
        <ImageBackground source={getAqiBackgroundImage(aqi, aqiverygood, aqigood, aqifair, aqipoor, aqiverypoor, aqihazardous)!}
          style={styles.squareBackgroundImage}
          imageStyle={{ borderRadius: 20 }}
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
        </ImageBackground>
        {/*<ImageBackground
          source={getAqiBackgroundImage(aqi, aqiverygood, aqigood, aqifair, aqipoor, aqiverypoor, aqihazardous)!}
          style={styles.squareBackgroundImage}
          imageStyle={{ borderRadius: 20 }}
        >
          < LoadingMessage/> 
        </ImageBackground>*/}
      </TouchableOpacity>

      <Modal
        transparent
        visible={modalVisible}
        animationType="fade"
        onRequestClose={() => setModalVisible(false)}
      >
        <ThemedView style={styles.modalBackground}>
          <ThemedView style={styles.modalContainer}>
            {error ? (
              <ThemedText style={styles.squareText}>{error}</ThemedText>
            ) : (
              <>
                <ThemedText style={styles.squareText}>What is AQI? {'\n\n'}</ThemedText>
                <ThemedText style={[styles.squareText, { fontWeight: '100', fontSize: 16, }]}>

                 The Air Quality Index (AQI) is a system that tells us how clean or “friendly” the air around us is. 
                 The rating, a number from 0 to 200+, is based on the amount of tiny invisible particles, 
                 (like the ones from cars and factories) and specific chemicals called "pollutants" in the atmosphere. 
                 Knowing the AQI helps us decide when it’s perfect to go outside and play, or when it's better to 
                 stay inside. It's a tool that allows us to stay safe and healthy while having fun! 

                </ThemedText>
              </>
            )}
            <TouchableOpacity
              style={styles.modalCloseButton}
              onPress={() => setModalVisible(false)}
            >
              <ThemedText style={{ color: 'white' }}>Close</ThemedText>
            </TouchableOpacity>
          </ThemedView>
        </ThemedView>
      </Modal>
    </>
  );
}

interface ImageWithLoadingBackgroundProps {
  imageSource: any;
  aqi: number | null;
  error: string | null;
}

export const ImageWithLoadingBackground = ({ imageSource, aqi, error }: ImageWithLoadingBackgroundProps) => {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // simulate loading duration
    const timer = setTimeout(() => setLoading(false), 21000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <View style={styles.container}>
      {loading ? (
        <View style={styles.loadingBox}>
          <LoadingMessage />
        </View>
      ) : (
        <AqiCardPopup aqi={aqi} error={error} />
      )}
    </View>
  );
};


interface WeatherData {
  time: number;
  temp: number;
  humidity: number;
  pressure: number;
  wind_speed: number;
  wind_direction: number;
  precipitation: number;
  cloud_cover: number;
}



const styles = StyleSheet.create({
  squareBackgroundImage: 
  { width: 200, 
    height: 300, 
    justifyContent: 'center', 
    alignItems: 'center' 
  },
  container: {
    width: 200,
    height: 300,
    justifyContent: 'center',
    alignItems: 'center',
  },
  squareText: { fontSize: 18, textAlign: 'center' },
  aqiValue: { fontSize: 40, fontWeight: 'bold', textAlign: 'center' },
  textContainer: {justifyContent: 'center',alignItems: 'center',textAlign: 'center', backgroundColor: 'transparent',}, 
  modalBackground: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'center', alignItems: 'center' },
  modalContainer: { width: 500, backgroundColor: 'white', borderRadius: 12, padding: 20, alignItems: 'center' },
  modalCloseButton: { marginTop: 20, backgroundColor: '#2196F3', borderRadius: 8, paddingVertical: 10, paddingHorizontal: 20 },
    loadingBox: {
    width: 250,
    height: 300,
    backgroundColor: '#faabddff', // solid pink square
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 20,
    padding: 20,  
  },
});








