import { Image } from 'expo-image';
import { Platform, StyleSheet, TouchableOpacity, Text, View } from 'react-native';

import { Collapsible } from '@/components/ui/collapsible';
import { ExternalLink } from '@/components/external-link';
import ParallaxScrollView from '@/components/parallax-scroll-view';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { IconSymbol } from '@/components/ui/icon-symbol';
import { Fonts } from '@/constants/theme';
import { Ionicons } from '@expo/vector-icons';

export default function TabTwoScreen() {
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
      }>

      {/* --- Your mockup starts here --- */}
      <ThemedView>
        <Image
          source={require('@/assets/images/react-logo.png')}
          style={styles.image}
        />
        <TouchableOpacity style={styles.editButton}>
          <Ionicons name="information-circle-outline" size={28} color="black" />
        </TouchableOpacity>
      </ThemedView>

      {/* Circle buttons row */}
      <ThemedView style={styles.circleRow}>
        {[1, 2, 3, 4].map((_, index) => (
          <TouchableOpacity key={index} style={styles.circleButton} />
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
  titleContainer: {
    flexDirection: 'row',
    gap: 8,
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
  },
  circleButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#bcd4e6',
    marginHorizontal: 8,
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
});
