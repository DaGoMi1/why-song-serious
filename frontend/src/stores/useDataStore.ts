import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import localClusterData from '../data/clustered_data.json';

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

interface GuestLoginResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  nickname: string;
}

interface UserInfo {
    id: number;
    nickname: string;
    auth_type: string;
    created_at: string;
}

interface DataState {
    currentUser: UserInfo | null;
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
    checkLoginAndLoadHistory: () => Promise<string>;

    fetchRetrievals: (prefs: audioFeatures) => Promise<void>;
    fetchRecommendations: (selectedTracks: number[]) => Promise<void>;
    fetchTracksBySpotifyIds: (spotifyIds: string[]) => Promise<Track[]>;
    reset: () => void;
}

const cleanArtistName = (name: string) => {
    if (!name) return "Unknown Artist";
    // ['Artist'] -> Artist
    // ['Artist1', 'Artist2'] -> Artist1, Artist2
    return name.replace(/[\[\]']/g, ""); 
};

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
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    });

                    if (!res.ok) {
                        throw new Error('로그인 실패');
                    }

                    const data: GuestLoginResponse = await res.json();
                    
                    console.log("Guest Login Success:", data);

                    localStorage.setItem('login_type', 'guest');
                    localStorage.setItem('isGuest', 'true');
                    localStorage.setItem('user_id', data.user_id.toString()); 
                    localStorage.setItem('nickname', data.nickname);
                    localStorage.setItem('access_token', data.access_token);

                    set({ 
                        accessToken: data.access_token, 
                        preferences: null,
                        selectedTracks: [],
                        retrievalTracks: [],
                        recommendedTracks: [],
                        isLoading: false 
                    });
                } catch (err) {
                    console.error(err);
                    set({ error: "로그인 실패", isLoading: false });
                    throw err;
                }
            },

            currentUser: null,
            checkLoginAndLoadHistory: async () => {
                const token = get().accessToken;
                if (!token) return 'landing'; // 토큰 없으면 랜딩페이지

                set({ isLoading: true });
                try {
                    // 1. 내 정보 조회 (/api/auth/me)
                    const userRes = await fetch('/api/auth/me', {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    
                    if (!userRes.ok) throw new Error("Invalid Token");
                    const userData: UserInfo = await userRes.json();
                    set({ currentUser: userData });

                    // 2. 최신 추천 내역 조회 (/api/recommendations/latest)
                    const historyRes = await fetch('/api/recommendations/latest', {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });

                    if (historyRes.ok) {
                        const historyData = await historyRes.json();
                        
                        // 데이터가 있고 트랙이 존재하면
                        if (historyData.tracks && historyData.tracks.length > 0) {
                            console.log("과거 추천 내역 발견:", historyData);

                            // 아티스트 이름 정제 (cleanArtistName 헬퍼 함수 사용 가정)
                            const cleanedTracks = historyData.tracks.map((track: Track) => ({
                                ...track,
                                artist: track.artist.replace(/[\[\]']/g, "") // 헬퍼 함수 없으면 직접 정제
                            }));

                            set({
                                recommendedTracks: cleanedTracks,
                                description: historyData.description,
                                clusterData: localClusterData, // 클러스터 데이터도 필요하면 로드
                                isLoading: false
                            });
                            
                            return 'playlist'; // ✅ 바로 플레이리스트로 이동
                        }
                    }
                    
                    // 기록이 없으면 취향 선택 페이지로
                    set({ isLoading: false });
                    return 'preferences';

                } catch (e) {
                    console.error("Session check failed:", e);
                    // 토큰 만료 시 로그아웃 처리
                    localStorage.removeItem('access_token');
                    set({ accessToken: null, currentUser: null, isLoading: false });
                    return 'landing';
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

                    //console.log("fetch retrieval")
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
                    const cleanedTracks = data.tracks.map((track: Track) => ({
                        ...track,
                        artist: cleanArtistName(track.artist)
                    }));
                    //console.log("retrieval result: ",data)
                    set({ 
                        retrievalTracks: cleanedTracks, 
                        isLoading: false 
                    });
                } catch (err) {
                    set({ error: "데이터 로딩 실패", isLoading: false });
                }
            },

            // preferences와 선택된 트랙들을 전달하고 추천 결과를 받아옴
            fetchRecommendations: async (selectedTracks) => {
                if (!selectedTracks || selectedTracks.length === 0) {
                    console.warn("선택된 트랙이 없어 추천 요청을 중단합니다.");
                    return;
                }
                set({ isLoading: true, error: null });
                try {
                    const token = get().accessToken;
                    if (!token) {
                        throw new Error("로그인이 필요합니다.");
                    }

                    const payload = {
                        "inference_type": "embedding",
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
                    if (!res.ok) {
                        const errorData = await res.json();
                        console.error("추천 API 에러:", errorData);
                        set({ error: "추천 실패", isLoading: false });
                        return; // 🚨 여기서 끊어야 아래 .map()에서 에러가 안 납니다!
                    }
                    const data: RecommendationResponse = await res.json();
                    const cleanedTracks = data.tracks.map((track: Track) => ({
                        ...track,
                        artist: cleanArtistName(track.artist)
                    }));
                    //console.log("recommendation result:", cleanedTracks);

                    set({ 
                        recommendedTracks: cleanedTracks, 
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

            fetchTracksBySpotifyIds: async (spotifyIds: string[]) => {
                const token = get().accessToken;
                if (!token) throw new Error("로그인이 필요합니다.");

                try {
                // POST /api/tracks/spotify-ids
                const res = await fetch('/api/tracks/spotify-ids', {
                    method: 'POST', // GET -> POST 변경
                    headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                    },
                    // Body 구조: { "spotify_track_ids": ["string"] }
                    body: JSON.stringify({
                    spotify_track_ids: spotifyIds
                    })
                });

                if (!res.ok) {
                    throw new Error(`트랙 로드 실패: ${res.status}`);
                }

                // Response 구조: { "tracks": [ ... ] }
                const data = await res.json();
                
                // 아티스트 이름 정제 후 반환
                const cleanTracks = data.tracks.map((track: Track) => ({
                    ...track,
                    artist: cleanArtistName(track.artist)
                }));

                return cleanTracks; // Track[] 반환

                } catch (err) {
                console.error("API Error:", err);
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