import { useState, useEffect } from 'react';
import type { Track } from '../types/track';
import { useNavigate } from 'react-router';
import { Play, Check, ChevronLeft, ChevronRight } from 'lucide-react';

// 가짜 데이터 (나중에 백엔드 데이터로 교체됨)
const mockTracks: Track[] = [
  { id: '1', title: 'Hype Boy', artist: 'NewJeans', album: 'New Jeans', duration: '3:20', imageUrl: 'https://placehold.co/400/4f46e5/ffffff?text=HypeBoy', genre: 'K-Pop', bpm: 130 },
  { id: '2', title: 'Ditto', artist: 'NewJeans', album: 'OMG', duration: '3:05', imageUrl: 'https://placehold.co/400/ec4899/ffffff?text=Ditto', genre: 'K-Pop', bpm: 134 },
  { id: '3', title: 'Seven', artist: 'Jung Kook', album: 'Golden', duration: '3:04', imageUrl: 'https://placehold.co/400/10b981/ffffff?text=Seven', genre: 'Pop', bpm: 125 },
  { id: '4', title: 'I AM', artist: 'IVE', album: 'I\'ve IVE', duration: '3:00', imageUrl: 'https://placehold.co/400/f59e0b/ffffff?text=IAM', genre: 'K-Pop', bpm: 128 },
  { id: '5', title: 'Super Shy', artist: 'NewJeans', album: 'Get Up', duration: '2:34', imageUrl: 'https://placehold.co/400/3b82f6/ffffff?text=SuperShy', genre: 'K-Pop', bpm: 150 },
];

const TRACKS_PER_PAGE = 10;

export function Discover() {
  const navigate = useNavigate();
  const [selectedTracks, setSelectedTracks] = useState<string[]>([]);
  const [currentPage, setCurrentPage] = useState(1);

//   useEffect(() => {
//     // Check if user has set preferences
//     const preferences = localStorage.getItem('preferences');
//     if (!preferences) {
//       navigate('/preferences');
//     }
//   }, [navigate]);

  const totalPages = Math.ceil(mockTracks.length / TRACKS_PER_PAGE);
  const startIndex = (currentPage - 1) * TRACKS_PER_PAGE;
  const endIndex = startIndex + TRACKS_PER_PAGE;
  const currentTracks = mockTracks.slice(startIndex, endIndex);

  const toggleTrackSelection = (trackId: string) => {
    setSelectedTracks((prev) =>
      prev.includes(trackId)
        ? prev.filter((id) => id !== trackId)
        : [...prev, trackId]
    );
  };

  const handleCreatePlaylist = () => {
    if (selectedTracks.length > 0) {
      localStorage.setItem('selectedTracks', JSON.stringify(selectedTracks));
      navigate('/playlist');
    }
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-teal-900">
      {/* Header */}
      <div className="bg-gradient-to-b from-blue-600/30 to-transparent p-6 md:p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">
            당신을 위한 추천 음악
          </h1>
          <p className="text-white/80 mb-4">
            총 {mockTracks.length}개의 트랙 • 마음에 드는 곡을 선택하면 맞춤 플레이리스트를 만들어드립니다
          </p>
          {selectedTracks.length > 0 && (
            <div className="bg-teal-500/20 backdrop-blur-sm rounded-xl p-4 border border-teal-400/30">
              <p className="text-teal-200">
                <span className="font-bold text-teal-100">{selectedTracks.length}개의 곡</span>이 선택되었습니다. 
                여러 곡을 선택하여 더 풍부한 플레이리스트를 만들어보세요!
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Tracks List */}
      <div className="max-w-6xl mx-auto px-4 md:px-8 pb-32">
        <div className="bg-white/5 backdrop-blur-sm rounded-2xl overflow-hidden">
          {/* Table Header */}
          <div className="hidden md:grid grid-cols-12 gap-4 px-6 py-4 bg-white/5 border-b border-white/10 text-sm text-white/60">
            <div className="col-span-1 text-center">#</div>
            <div className="col-span-5">제목</div>
            <div className="col-span-3">앨범</div>
            <div className="col-span-1">장르</div>
            <div className="col-span-1">BPM</div>
            <div className="col-span-1 text-center">시간</div>
          </div>

          {/* Track Rows */}
          <div className="divide-y divide-white/5">
            {currentTracks.map((track, index) => {
              const isSelected = selectedTracks.includes(track.id);
              const globalIndex = startIndex + index + 1;

              return (
                <div
                  key={track.id}
                  onClick={() => toggleTrackSelection(track.id)}
                  className={`grid grid-cols-12 gap-4 px-4 md:px-6 py-4 cursor-pointer transition-all duration-200 hover:bg-white/10 group ${
                    isSelected ? 'bg-teal-500/20' : ''
                  }`}
                >
                  {/* Index / Play Button */}
                  <div className="col-span-12 md:col-span-1 flex md:justify-center items-center">
                    <div className="relative flex items-center gap-3 md:block">
                      {isSelected ? (
                        <div className="bg-teal-400 rounded-md size-10 md:size-8 flex items-center justify-center">
                          <Check className="size-5 md:size-4 text-slate-900" />
                        </div>
                      ) : (
                        <>
                          <span className="text-white/40 group-hover:hidden text-sm md:text-base w-10 md:w-8 text-center">
                            {globalIndex}
                          </span>
                          <Play className="hidden group-hover:block text-white size-10 md:size-8 fill-white" />
                        </>
                      )}
                      <img
                        src={track.imageUrl}
                        alt={track.title}
                        className="md:hidden size-12 rounded-lg object-cover"
                      />
                    </div>
                  </div>

                  {/* Title & Artist */}
                  <div className="col-span-12 md:col-span-5 flex items-center gap-4">
                    <img
                      src={track.imageUrl}
                      alt={track.title}
                      className="hidden md:block size-12 rounded-lg object-cover"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="font-semibold text-white truncate">
                        {track.title}
                      </div>
                      <div className="text-sm text-white/60 truncate">
                        {track.artist}
                      </div>
                    </div>
                  </div>

                  {/* Album */}
                  <div className="col-span-6 md:col-span-3 flex items-center">
                    <span className="text-white/70 truncate text-sm md:text-base">
                      {track.album}
                    </span>
                  </div>

                  {/* Genre */}
                  <div className="col-span-6 md:col-span-1 flex items-center">
                    <span className="text-white/70 text-sm md:text-base truncate">
                      {track.genre}
                    </span>
                  </div>

                  {/* BPM - Hidden on mobile */}
                  <div className="hidden md:flex col-span-1 items-center">
                    <span className="text-white/70 text-sm">{track.bpm}</span>
                  </div>

                  {/* Duration */}
                  <div className="col-span-12 md:col-span-1 flex items-center justify-end md:justify-center">
                    <span className="text-white/40 text-sm">{track.duration}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-2 mt-8">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className={`p-2 rounded-lg transition-all duration-200 ${
                currentPage === 1
                  ? 'text-white/20 cursor-not-allowed'
                  : 'text-white hover:bg-white/10'
              }`}
            >
              <ChevronLeft className="size-6" />
            </button>

            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <button
                key={page}
                onClick={() => handlePageChange(page)}
                className={`size-10 rounded-lg transition-all duration-200 ${
                  currentPage === page
                    ? 'bg-gradient-to-br from-blue-500 to-teal-500 text-white'
                    : 'text-white/60 hover:bg-white/10 hover:text-white'
                }`}
              >
                {page}
              </button>
            ))}

            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className={`p-2 rounded-lg transition-all duration-200 ${
                currentPage === totalPages
                  ? 'text-white/20 cursor-not-allowed'
                  : 'text-white hover:bg-white/10'
              }`}
            >
              <ChevronRight className="size-6" />
            </button>
          </div>
        )}
      </div>

      {/* Bottom Action Bar */}
      {selectedTracks.length > 0 && (
        <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-slate-900 via-slate-900/95 to-transparent p-4 md:p-6 border-t border-white/10">
          <div className="max-w-6xl mx-auto flex items-center justify-between gap-4">
            <div className="text-white">
              <p className="font-bold">{selectedTracks.length}개 선택됨</p>
              <p className="text-sm text-white/60">플레이리스트를 만들어보세요</p>
            </div>
            <button
              onClick={handleCreatePlaylist}
              className="bg-gradient-to-r from-blue-500 to-teal-500 text-white px-8 py-4 rounded-full font-bold shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-300"
            >
              플레이리스트 생성
            </button>
          </div>
        </div>
      )}
    </div>
  );
}