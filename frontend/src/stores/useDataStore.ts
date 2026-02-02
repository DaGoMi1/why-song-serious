import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware'; // 👈 추가됨

// 1. 데이터 타입
interface Preferences {
    energy: number;
    valence: number;
    danceability: number;
    acousticness: number;
    instrumentalness: number;
    tempo: number;
}

// 2. 인터페이스
interface DataState {
    preferences: Preferences | null;
    setPreferences: (prefs: Preferences) => void; // preferences 저장

    selectedTracks: string[];
    setSelectedTracks: (tracks: string[]) => void;

    retrievalTracks: any[];
    recommendedTracks: any[];
    clusterData: any[];
    isLoading: boolean;
    error: string | null;

    fetchRetrievals: (prefs: Preferences) => Promise<void>;
    fetchRecommendations: (prefs: Preferences, tracks: string[]) => Promise<void>;
}

// 3. 구현 (persist 적용)
export const useDataStore = create<DataState>()(
    persist(
        (set, get) => ({
            // 초기값
            preferences: null,
            selectedTracks: [],
            retrievalTracks: [],
            recommendedTracks: [],
            clusterData: [],
            isLoading: false,
            error: null,


            // preferences 및 selectedTracks 설정
            setPreferences: (prefs) => set({ preferences: prefs }),
            setSelectedTracks: (tracks) => set({ selectedTracks: tracks }),

            // Discover 데이터 (GET -> POST)
            fetchRetrievals: async (prefs) => {
                set({ isLoading: true, error: null });
                try {
                    const res = await fetch('http://localhost:8000/api/retrieval', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(prefs),
                    });
                    const data = await res.json();
                    set({ retrievalTracks: data, isLoading: false });
                } catch (err) {
                    set({ error: "데이터 로딩 실패", isLoading: false });
                }
            },

            // Playlist 데이터
            fetchRecommendations: async (prefs, tracks) => {
                set({ isLoading: true, error: null });
                try {
                    const payload = { ...prefs, selected_tracks: tracks };

                    const res = await fetch('http://localhost:8000/api/recommend', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload),
                    });
                    const recommendedTracks = await res.json();

                    const clusterRes = await fetch('http://localhost:8000/api/cluster');
                    const clusterData = await clusterRes.json();

                    set({ recommendedTracks, clusterData, isLoading: false });
                } catch (err) {
                    set({ error: "추천 결과 로딩 실패", isLoading: false });
                }
            }
        }),
        {
            name: 'music-storage', // ⭐️ 로컬 스토리지에 저장될 키 이름
            storage: createJSONStorage(() => localStorage), // 저장소 지정
            // preferences만 저장하고 싶다면 아래 옵션 사용 (지금은 다 저장해도 무방)
            // partialize: (state) => ({ preferences: state.preferences }), 
        }
    )
);