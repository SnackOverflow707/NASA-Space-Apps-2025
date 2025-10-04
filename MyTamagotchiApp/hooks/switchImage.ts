import { useState } from 'react';
import happyImg from '../assets/images/tamagachi-guys/happy.png';
import sadImg from '../assets/images/tamagachi-guys/sad.png';
import lpaImg from '../assets/images/tamagachi-guys/lpa.png';
import reImg from '../assets/images/tamagachi-guys/re.png';
import maskImg from '../assets/images/tamagachi-guys/mask.png';

export type ImageName = 'happy' | 'sad' | 'lpa' | 're' | 'mask';

export function useTamagachiImage() {
  const [currentImage, setCurrentImage] = useState(happyImg);

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

  return { currentImage, showImage };
}
