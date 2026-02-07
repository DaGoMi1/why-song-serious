import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import localClusterData from '../data/clustered_Data.json';

interface audioFeatures {
    energy: number;
    valence: number;
    danceability: number;
    acousticness: number;
    loudness: number;
    tempo: number;
}

export interface Track {
    id: number;
    spotify_track_id: string;
    name: string;
    artist: string;
    album: string;
    duration_ms: number;
    popularity: number;
    image_url: string;
    audio_features: audioFeatures;
}

interface RecommendationResponse {
    tracks: Track[];
    description: string;
}

interface DataState {
    preferences: audioFeatures | null;
    // preferences 저장
    setPreferences: (prefs: audioFeatures) => void; 

    selectedTracks: number[];
    // discover에서 선택한 트랙들 저장
    setSelectedTracks: (tracks: number[]) => void;

    retrievalTracks: any[];
    recommendedTracks: any[];
    description: string | null;
    clusterData: any[];
    isLoading: boolean;
    error: string | null;

    accessToken: string | null;
    loginAsGuest: () => Promise<void>;

    fetchRetrievals: (prefs: audioFeatures) => Promise<void>;
    fetchRecommendations: (selectedTracks: number[]) => Promise<void>;
    getTrackById: (trackId: string) => Promise<Track>;
    reset: () => void;
}

export const useDataStore = create<DataState>()(
    persist(
        (set, get) => ({
            preferences: null,
            selectedTracks: [],
            retrievalTracks: [],
            recommendedTracks: [],
            description: null,
            clusterData: [],
            isLoading: false,
            error: null,
            accessToken: null,


            // preferences 및 selectedTracks 설정
            setPreferences: (prefs) => set({ preferences: prefs }),
            setSelectedTracks: (tracks) => set({ selectedTracks: tracks }),

            // 게스트 로그인
            loginAsGuest: async () => {
                set({ isLoading: true, error: null });
                try {
                    const res = await fetch('/api/auth/guest', {
                        method: 'POST',
                    });
                    if (!res.ok) {
                        throw new Error('로그인 실패');
                    }

                    const data = await res.json();
                    set({ 
                        accessToken: data.access_token, 
                        preferences: null,
                        selectedTracks: [],
                        retrievalTracks: [],
                        recommendedTracks: [],
                        isLoading: false 
                    });
                } catch (err) {
                    set({ error: "로그인 실패", isLoading: false });
                    throw err;
                }
            },

            // preference를 전달하고 retrieval 데이터를 받아옴
            fetchRetrievals: async (prefs) => {
                set({ isLoading: true, error: null });
                try {
                    const token = get().accessToken;
                    if (!token) {
                        throw new Error("로그인이 필요합니다.");
                    }

                    console.log("fetch retrieval")
                    const payload={
                        preferences: prefs,
                        limit: 20
                    }
                    const res = await fetch('/api/tracks/search', {
                        method: 'POST',
                        headers: { 
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify(payload),
                    });
                    if (!res.ok) {
                        const errorData = await res.json();
                        console.error("백엔드 에러 응답:", errorData);
                        set({ retrievalTracks: [], isLoading: false, error: "서버 요청 실패" });
                        return; 
                    }
                    const data = await res.json();
                    console.log("retrieval result: ",data)
                    set({ 
                        retrievalTracks: data.tracks, 
                        isLoading: false 
                    });
                } catch (err) {
                    set({ error: "데이터 로딩 실패", isLoading: false });
                }
            },

            // preferences와 선택된 트랙들을 전달하고 추천 결과를 받아옴
            fetchRecommendations: async (selectedTracks) => {
                set({ isLoading: true, error: null });
                try {
                    const token = get().accessToken;
                    if (!token) {
                        throw new Error("로그인이 필요합니다.");
                    }

                    const payload = {
                        "inference_type": "string",
                        "track_ids": selectedTracks 
                    };
                    
                    // 추천 요청 시 헤더 추가
                    const res = await fetch('/api/recommendations', {
                        method: 'POST',
                        headers: { 
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify(payload),
                    });
                    const data: RecommendationResponse = await res.json();
                    console.log("recommendation result:", data);

                    set({ 
                        recommendedTracks: data.tracks, 
                        clusterData: localClusterData, 
                        description: data.description,
                        isLoading: false 
                    });
                } catch (err) {
                    console.error(err);
                    set({ error: "추천 결과 로딩 실패", isLoading: false });
                }
            },
            reset: () => set({
                preferences: null,
                recommendedTracks: [],
                clusterData: [],
                description: null,
                selectedTracks: [],
                isLoading: false,
            }),

            getTrackById: async (trackId: number | string) => {
                const token = get().accessToken;
                
                // 1. 토큰 체크
                if (!token) {
                    console.error("토큰이 없습니다.");
                    throw new Error("로그인이 필요합니다.");
                }

                try {
                    const res = await fetch(`/api/tracks/${trackId}`, {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}` // 토큰 헤더 필수
                        }
                    });

                    if (!res.ok) {
                        throw new Error(`트랙 로드 실패: ${res.status}`);
                    }

                    const data: Track = await res.json();
                    console.log(`${trackId}:`, data);
                    
                    return data;

                } catch (err) {
                    console.error(err);
                    throw err;
                }
            },
        }),
        {
            // 로컬 스토리지
            name: 'music-storage-v3', 
            storage: createJSONStorage(() => localStorage), 
        }
    )
);