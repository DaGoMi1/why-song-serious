import { useEffect } from 'react';
import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Music, Sparkles, BarChart3, ListMusic, Loader2, User } from 'lucide-react'; 
import { useDataStore } from '../stores/useDataStore';

export function Landing() {
  const navigate = useNavigate();
  const { loginAsGuest, checkLoginAndLoadHistory, isLoading: isGlobalLoading } = useDataStore();
  const [loginType, setLoginType] = useState<'spotify' | 'guest' | null>(null);

  useEffect(() => {
    const initSession = async () => {
      // 이미 토큰이 있는 경우 체크 시작
      if (localStorage.getItem('access_token')) {
         // 로딩 표시를 위해 loginType을 임시 설정할 수도 있음
         const nextPath = await checkLoginAndLoadHistory();
         
         if (nextPath !== 'landing') {
             navigate(`/${nextPath}`);
         }
      }
    };
    initSession();
  }, [checkLoginAndLoadHistory, navigate]);

  const handleSpotifyLogin = async () => {
    try {
      // 우선 게스트 로그인으로 처리 
      localStorage.removeItem('isGuest');
      localStorage.removeItem('login_type');
      localStorage.removeItem('user_id');
      localStorage.removeItem('nickname');
      await loginAsGuest();
      
      navigate('/preferences');
    } catch (error) {
      console.error('Login failed:', error);
      alert('로그인에 실패했습니다.');
    }
  };

  const handleGuestLogin = async () => {
    try {
        localStorage.clear(); 
        await loginAsGuest(); 
        
        navigate('/preferences');
    } catch (e) {
        console.error("Guest login failed", e);
        alert("게스트 로그인 중 오류가 발생했습니다.");
    }
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
                <h1 className="text-5xl font-bold text-white">Why Song Serious?</h1>
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
                disabled={isGlobalLoading && loginType === 'spotify'}
                className="!bg-green-500 hover:bg-green-600 disabled:bg-gray-500 disabled:cursor-not-allowed text-white py-4 px-8 rounded-full font-bold text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 flex items-center justify-center gap-3"
              >
                {isGlobalLoading && loginType === 'spotify' ? (
                    <>
                        <Loader2 className="size-6 animate-spin" />
                        로그인 중...
                    </>
                ) : (
                    <>
                        <Music className="size-7" />
                        스포티파이 로그인
                    </>
                )}
              </button>

              <button
                  onClick={handleGuestLogin}
                  disabled={isGlobalLoading && loginType === 'guest'}
                  className="flex-1 !bg-white/10 hover:bg-white/20 border border-white/20 backdrop-blur-sm text-white py-4 px-8 rounded-full font-bold text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 flex items-center justify-center gap-3 disabled:cursor-not-allowed disabled:bg-white/5"
                >
                  {isGlobalLoading && loginType === 'guest' ? (
                    <>
                      <Loader2 className="size-6 animate-spin" />
                      <span>로그인 중...</span>
                    </>
                  ) : (
                    <>
                      <User className="size-6" />
                      <span>게스트로 시작하기</span>
                    </>
                  )}
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