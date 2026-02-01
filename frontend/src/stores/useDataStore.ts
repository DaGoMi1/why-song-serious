import { create } from 'zustand';

interface DataState {
    tracks: any[],
    clusterData: any[],
    isLoading: boolean;
    error: string | null;

    fetchAllData: () => Promise<void>;
}

export const useDataStore = create<DataState>((set) => ({
    tracks: [],
    clusterData: [],
    isLoading: false,
    error: null,

    fetchAllData: async () =>{
        set({ isLoading: true, error: null });
        try {
            const tracksRes = await fetch('http://localhost:8000/api/tracks');
            const tracks = await tracksRes.json();

            const clusterRes = await fetch('http://localhost:8000/api/cluster');
            const clusterData = await clusterRes.json()

            set({ tracks, clusterData, isLoading: false});
            console.log("data loaded: ",tracks.length," tracks")
        }catch(err) {
            console.error("data loading fail: ", err);
            set({error: "data loading fail", isLoading: false});
        }
    }
}))