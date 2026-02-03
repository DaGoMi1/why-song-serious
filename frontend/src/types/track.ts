export interface AudioFeatures {
  tempo: number;
  energy: number;
  danceability: number;
  valence: number;
  acousticness: number;
  loudness: number;
}

export interface Track {
  id: string;
  title: string;
  artist: string;
  album: string;
  duration: string;
  popularity: number;
  imageUrl: string;
  features: AudioFeatures;
}