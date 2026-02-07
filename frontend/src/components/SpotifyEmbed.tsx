import { SkipBack, SkipForward, X } from 'lucide-react';

interface SpotifyEmbedProps {
  trackId: string | null;
  onClose: () => void;
  onNext: () => void;
  onPrev: () => void;
  hasNext: boolean;
  hasPrev: boolean;
}

// 공식 임베드 위젯 컴포넌트
export const SpotifyEmbed = ({ trackId, onClose, onNext, onPrev, hasNext, hasPrev }: SpotifyEmbedProps) => {
  if (!trackId) return null;

  return (
    <div className="fixed bottom-25 right-6 z-50 flex flex-col items-end gap-2 animate-in slide-in-from-bottom-5 fade-in duration-300">

      {/* 커스텀 컨트롤러 (이전/다음) */}
      <div className="flex items-center gap-2 bg-black/80 backdrop-blur-md p-2 rounded-50 border border-white/10 shadow-xl">
        <button
          onClick={onPrev}
          disabled={!hasPrev}
          className={`p-2 rounded-full hover:bg-white/20 transition ${!hasPrev ? 'opacity-30 cursor-not-allowed' : 'text-white'}`}
        >
          <SkipBack size={20} fill="currentColor" />
        </button>

        <div className="w-px h-4 bg-white/20"></div>

        <button
          onClick={onNext}
          disabled={!hasNext}
          className={`p-2 rounded-full hover:bg-white/20 transition ${!hasNext ? 'opacity-30 cursor-not-allowed' : 'text-white'}`}
        >
          <SkipForward size={20} fill="currentColor" />
        </button>

        <div className="w-px h-4 bg-white/20"></div>

        <button onClick={onClose} className="p-2 rounded-full hover:bg-red-500/20 text-white/70 hover:text-red-400 transition">
          <X size={20} />
        </button>
      </div>

      {/* Spotify Widget */}
      <div className="shadow-2xl rounded-xl overflow-hidden border border-white/10">
        <iframe
          style={{ borderRadius: '12px' }}
          src={`https://open.spotify.com/embed/track/${trackId}?utm_source=generator&theme=0`}
          width="320"
          height="152"
          frameBorder="0"
          allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
          loading="lazy"
        />
      </div>
    </div>
  );
};