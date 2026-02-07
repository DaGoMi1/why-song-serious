export interface AudioFeatures {
  acousticness: number,
  valence: number,
  energy: number,
  danceability: number,
  loudness: number,
  tempo: number,
}

export interface Track {
  id: string;
  spotify_track_id: string;
  name: string;
  artist: string;
  album: string;
  duration_ms: string;
  popularity: number;
  image_url: string;
  audio_features: AudioFeatures;
}