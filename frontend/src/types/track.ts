export interface Track {
  id: string;
  title: string;
  artist: string;
  album: string;
  duration: string;
  imageUrl: string;
  genre: string;
  bpm: number;
  energy?: number;           
  danceability?: number;
  valence?: number;
  acousticness?: number;
  instrumentalness?: number;
}