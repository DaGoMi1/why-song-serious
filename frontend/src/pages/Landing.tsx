import { useNavigate } from 'react-router';
import { Music, Sparkles, BarChart3, ListMusic, User } from 'lucide-react';

export function Landing() {
  const navigate = useNavigate();

  const handleSpotifyLogin = () => {
    // Mock Spotify OAuth login - in production this would redirect to Spotify's OAuth page
    // const spotifyAuthUrl = `https://accounts.spotify.com/authorize?client_id=${CLIENT_ID}&response_type=code&redirect_uri=${REDIRECT_URI}&scope=user-read-private user-read-email`;
    // window.location.href = spotifyAuthUrl;

    // For prototype, just navigate to preferences
    navigate('/preferences');
  };

  const handleGuestLogin = () => {
    navigate('/preferences');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-teal-900">
      {/* Hero Section */}
      <div className="flex items-center justify-center min-h-screen p-4">
        <div className="max-w-5xl w-full">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            {/* Left: Main Content */}
            <div className="space-y-6">
              <div className="flex items-center gap-3">
                <div className="bg-gradient-to-br from-blue-400 to-teal-400 rounded-2xl p-4">
                  <Music className="size-12 text-white" />
                </div>
                <h1 className="text-5xl font-bold text-white">MusicMatch</h1>
              </div>

              <h2 className="text-3xl font-bold text-white leading-tight">
                당신만을 위한<br />
                완벽한 음악 추천 서비스
              </h2>

              <p className="text-lg text-white/80">
                AI 기반 분석으로 당신의 음악 취향을 이해하고,
                맞춤형 플레이리스트를 추천해드립니다.
                음악의 특성을 시각화하여 더 깊이 있는 음악 경험을 제공합니다.
              </p>

              {/* Spotify Login Button */}
              <button
                onClick={handleSpotifyLogin}
                className="flex-1 bg-[#1DB954] hover:bg-[#1ed760] text-white py-4 px-8 rounded-full font-bold text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 flex items-center justify-center gap-3"
              >
                <svg className="size-6" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z" />
                </svg>
                <span>Spotify 로그인</span>
              </button>

              <button
                  onClick={handleGuestLogin}
                  className="flex-1 bg-white/10 hover:bg-white/20 border border-white/20 backdrop-blur-sm text-white py-4 px-8 rounded-full font-bold text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 flex items-center justify-center gap-3"
                >
                  <User className="size-6" />
                  <span>게스트로 시작하기</span>
                </button>
            </div>

            {/* Right: Features */}
            <div className="space-y-4">
              <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-6 hover:bg-white/15 transition-all duration-300">
                <div className="flex items-start gap-4">
                  <div className="bg-blue-500/20 rounded-2xl p-3">
                    <Sparkles className="size-8 text-blue-300" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white mb-2">
                      AI 기반 취향 분석
                    </h3>
                    <p className="text-white/70">
                      선호하는 분위기를 선택하면 AI가 당신의 취향을 분석하여
                      최적의 음악을 추천합니다.
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-6 hover:bg-white/15 transition-all duration-300">
                <div className="flex items-start gap-4">
                  <div className="bg-teal-500/20 rounded-2xl p-3">
                    <ListMusic className="size-8 text-teal-300" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white mb-2">
                      맞춤형 플레이리스트
                    </h3>
                    <p className="text-white/70">
                      수백 개의 트랙 중에서 당신의 취향에 꼭 맞는 곡들만 선별하여
                      나만의 플레이리스트를 만들어보세요.
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-6 hover:bg-white/15 transition-all duration-300">
                <div className="flex items-start gap-4">
                  <div className="bg-cyan-500/20 rounded-2xl p-3">
                    <BarChart3 className="size-8 text-cyan-300" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white mb-2">
                      음악 특성 시각화
                    </h3>
                    <p className="text-white/70">
                      에너지, 댄스 적합도, 템포 등 음악의 다양한 특성을 차트로
                      확인하고 더 깊이 있는 음악 감상을 경험하세요.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="bg-gradient-to-b from-transparent to-slate-900/50 py-20 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            이렇게 사용해보세요
          </h2>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center space-y-3">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 size-16 rounded-2xl flex items-center justify-center mx-auto">
                <span className="text-2xl font-bold text-white">1</span>
              </div>
              <h3 className="font-bold text-white">Spotify 로그인</h3>
              <p className="text-sm text-white/60">
                간편하게 Spotify 계정으로 시작하세요
              </p>
            </div>
            <div className="text-center space-y-3">
              <div className="bg-gradient-to-br from-teal-500 to-teal-600 size-16 rounded-2xl flex items-center justify-center mx-auto">
                <span className="text-2xl font-bold text-white">2</span>
              </div>
              <h3 className="font-bold text-white">취향 선택</h3>
              <p className="text-sm text-white/60">
                좋아하는 장르와 분위기를 선택해주세요
              </p>
            </div>
            <div className="text-center space-y-3">
              <div className="bg-gradient-to-br from-cyan-500 to-cyan-600 size-16 rounded-2xl flex items-center justify-center mx-auto">
                <span className="text-2xl font-bold text-white">3</span>
              </div>
              <h3 className="font-bold text-white">음악 선택</h3>
              <p className="text-sm text-white/60">
                추천된 곡 중 마음에 드는 음악을 고르세요
              </p>
            </div>
            <div className="text-center space-y-3">
              <div className="bg-gradient-to-br from-blue-400 to-teal-400 size-16 rounded-2xl flex items-center justify-center mx-auto">
                <span className="text-2xl font-bold text-white">4</span>
              </div>
              <h3 className="font-bold text-white">플레이리스트 생성</h3>
              <p className="text-sm text-white/60">
                맞춤 플레이리스트와 음악 분석을 확인하세요
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}