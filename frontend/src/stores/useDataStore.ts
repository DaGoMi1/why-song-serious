import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
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

    selectedTracks: number[];
    // discover에서 선택한 트랙들 저장
    setSelectedTracks: (tracks: number[]) => void;

    retrievalTracks: any[];
    recommendedTracks: any[];
    playlistExplanation: PlaylistExplanation | null;
    clusterData: any[];
    isLoading: boolean;
    error: string | null;

    accessToken: string | null;
    loginAsGuest: () => Promise<void>;

    fetchRetrievals: (prefs: Preferences) => Promise<void>;
    fetchRecommendations: (selectedTracks: number[]) => Promise<void>;
    reset: () => void;
}

export const useDataStore = create<DataState>()(
    persist(
        (set, get) => ({
            preferences: null,
            selectedTracks: [],
            retrievalTracks: [],
            recommendedTracks: [],
            playlistExplanation: null,
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
                        console.error("🔥 백엔드 에러 응답:", errorData);
                        // 에러가 나면 빈 배열로 설정하여 .slice 에러 방지
                        set({ retrievalTracks: [], isLoading: false, error: "서버 요청 실패" });
                        return; 
                    }
                    const data = await res.json();
                    console.log("retrieval: ",data)
                    set({ 
                        retrievalTracks: data.tracks, // 응답 구조에 맞게 수정 (.tracks)
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
                    const res = await fetch('/api/recommend', {
                        method: 'POST',
                        headers: { 
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify(payload),
                    });
                    const data = await res.json();

                    // 클러스터 요청 시 헤더 추가
                    const clusterRes = await fetch('/api/cluster', {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });
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
                accessToken: null,
            }),
        }),
        {
            // 로컬 스토리지
            name: 'music-storage-v3', 
            storage: createJSONStorage(() => localStorage), 
        }
    )
);