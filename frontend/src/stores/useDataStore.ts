import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware'; // 👈 추가됨
import { Preferences } from '../pages/Preferences';

interface Preferences {
    energy: number;
    valence: number;
    danceability: number;
    acousticness: number;
    loudness: number;
    tempo: number;
}

interface PlaylistExplanation {
    name: string;
    description: string;
}

interface DataState {
    preferences: Preferences | null;
    // preferences 저장
    setPreferences: (prefs: Preferences) => void; 

    selectedTracks: string[];
    // discover에서 선택한 트랙들 저장
    setSelectedTracks: (tracks: string[]) => void;

    retrievalTracks: any[];
    recommendedTracks: any[];
    playlistExplanation: PlaylistExplanation | null;
    clusterData: any[];
    isLoading: boolean;
    error: string | null;

    fetchRetrievals: (prefs: Preferences) => Promise<void>;
    fetchRecommendations: (prefs: Preferences, tracks: string[]) => Promise<void>;
    reset: () => void;
}

export const useDataStore = create<DataState>()(
    persist(
        (set) => ({
            preferences: null,
            selectedTracks: [],
            retrievalTracks: [],
            recommendedTracks: [],
            playlistExplanation: null,
            clusterData: [],
            isLoading: false,
            error: null,


            // preferences 및 selectedTracks 설정
            setPreferences: (prefs) => set({ preferences: prefs }),
            setSelectedTracks: (tracks) => set({ selectedTracks: tracks }),

            // preference를 전달하고 retrieval 데이터를 받아옴
            fetchRetrievals: async (prefs) => {
                set({ isLoading: true, error: null });
                try {
                    console.log("fetch retrieval")
                    const payload={
                        preferences: prefs,
                        limit: 20
                    }
                    const res = await fetch('http://localhost:8000/api/search', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload),
                    });
                    if (!res.ok) {
                        const errorData = await res.json();
                        console.error("🔥 백엔드 에러 응답:", errorData);
                        // 에러가 나면 빈 배열로 설정하여 .slice 에러 방지
                        set({ retrievalTracks: [], isLoading: false, error: "서버 요청 실패" });
                        return; 
                    }
                    const data = await res.json();
                    console.log("retrieval: ",data)
                    set({ 
                        retrievalTracks: data,
                        isLoading: false 
                    });
                } catch (err) {
                    set({ error: "데이터 로딩 실패", isLoading: false });
                }
            },

            // preferences와 선택된 트랙들을 전달하고 추천 결과를 받아옴
            fetchRecommendations: async (prefs, tracks) => {
                set({ isLoading: true, error: null });
                try {
                    const payload = { ...prefs, selected_tracks: tracks };

                    const res = await fetch('http://localhost:8000/api/recommend', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload),
                    });
                    const data = await res.json();

                    const clusterRes = await fetch('http://localhost:8000/api/cluster');
                    const clusterData = await clusterRes.json();
                    // console.log("Received data:", data);
                    set({ 
                        recommendedTracks: data.tracks, 
                        clusterData, 
                        playlistExplanation: data.explanation,
                        isLoading: false });
                } catch (err) {
                    set({ error: "추천 결과 로딩 실패", isLoading: false });
                }
            },
            reset: () => set({
                preferences: null,
                recommendedTracks: [],
                clusterData: [],
                playlistExplanation: null,
                selectedTracks: [],
                isLoading: false,
            }),
        }),
        {
            // 로컬 스토리지
            name: 'music-storage-v2', 
            storage: createJSONStorage(() => localStorage), 
        }
    )
);