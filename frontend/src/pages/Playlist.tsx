import { useState, useEffect, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router';
import type { Track } from '../types/track';
import { SpotifyEmbed } from '../components/SpotifyEmbed';
import { Play, Share2, Download, Music, RefreshCw, Loader2, Pause } from 'lucide-react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
} from 'recharts';
import ReactECharts from 'echarts-for-react';
import { useDataStore } from '../stores/useDataStore';

// 클러스터 색상 정의 
// 기본적으로 4가지 색상을 정하고 그 사이를 그라데이션으로 부드럽게 연결
const baseColors = [
  { r: 59, g: 130, b: 246, name: 'test' }, // 파랑 (#3b82f6)
  { r: 239, g: 68, b: 68, name: 'test' },  // 빨강 (#ef4444)
  { r: 168, g: 85, b: 247, name: 'test' },            // 보라 (#a855f7)
  { r: 20, g: 184, b: 166, name: 'test' },   // 청록 (#14b8a6)
];

const interpolateColor = (color1: any, color2: any, factor: number) => {
  const result = {
    r: Math.round(color1.r + (color2.r - color1.r) * factor),
    g: Math.round(color1.g + (color2.g - color1.g) * factor),
    b: Math.round(color1.b + (color2.b - color1.b) * factor),
  };
  return result;
};

const rgbToHex = (r: number, g: number, b: number) => {
  return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
};

// 자동으로 색상 생성
const generateGradientColors = (totalSteps: number) => {
  const colors: Record<number, { bg: string; border: string; name: string }> = {};

  for (let i = 0; i < totalSteps; i++) {
    // 현재 단계의 위치 계산
    const distinctRatio = i / (totalSteps - 1);

    // 전체 비율을 3개의 구간으로 나눔
    const segment = Math.min(Math.floor(distinctRatio * (baseColors.length - 1)), baseColors.length - 2);
    const segmentRatio = (distinctRatio * (baseColors.length - 1)) - segment;

    const startColor = baseColors[segment];
    const endColor = baseColors[segment + 1];

    // 색상 섞기
    const mixed = interpolateColor(startColor, endColor, segmentRatio);
    const hex = rgbToHex(mixed.r, mixed.g, mixed.b);

    // 이름은 더 가까운 쪽의 이름을 따라감
    const name = segmentRatio < 0.5 ? startColor.name : endColor.name;

    colors[i + 1] = {
      bg: `rgba(${mixed.r}, ${mixed.g}, ${mixed.b}, 0.15)`, // 배경은 투명도 15%
      border: hex,
      name: name
    };
  }
  return colors;
};

const clusterColors = generateGradientColors(600);

export function Playlist() {
  const navigate = useNavigate();
  const [playlistTracks, setPlaylistTracks] = useState<Track[]>([]);

  // 임베딩 위젯에서 음악을 재생하기 위해 인덱스 관리
  const [currentTrackIndex, setCurrentTrackIndex] = useState<number | null>(null);
  const {
    recommendedTracks,
    clusterData,
    fetchRecommendations,
    preferences,
    selectedTracks,
    playlistExplanation,
    isLoading,
    reset
  } = useDataStore();

  useEffect(() => {
    // 추천 트랙이 없으면 받아옴
    if (recommendedTracks.length === 0 || !playlistExplanation) {
      fetchRecommendations(preferences!, selectedTracks);
    }
  }, [fetchRecommendations, recommendedTracks.length, playlistExplanation])

  useEffect(() => {
    if (recommendedTracks.length === 0) return;
    // 추천된 트랙 로드
    setPlaylistTracks(recommendedTracks);
  }, [navigate, recommendedTracks]);

  // 개별 곡 클릭
  const playTrack = (index: number) => {
    if (currentTrackIndex === index) {
      setCurrentTrackIndex(null); // 같은 곡 누르면 닫기
    } else {
      setCurrentTrackIndex(index); // 해당 인덱스 재생
    }
  };

  // 전체 재생 버튼 클릭
  const handlePlayAll = () => {
    if (playlistTracks.length > 0) {
      if (currentTrackIndex !== null) {
        // 이미 재생 중이면 정지
        setCurrentTrackIndex(null);
      } else {
        // 아니면 0번부터 시작
        setCurrentTrackIndex(0);
      }
    }
  };

  // 다음 곡 핸들러
  const handleNext = () => {
    if (currentTrackIndex !== null && currentTrackIndex < playlistTracks.length - 1) {
      setCurrentTrackIndex(currentTrackIndex + 1);
    }
  };

  // 이전 곡 핸들러
  const handlePrev = () => {
    if (currentTrackIndex !== null && currentTrackIndex > 0) {
      setCurrentTrackIndex(currentTrackIndex - 1);
    }
  };

  // 현재 재생중인 트랙
  const currentTrackId = currentTrackIndex !== null ? playlistTracks[currentTrackIndex]?.id : null;

  const handleShare = async () => {
    try {
      const currentUrl = window.location.href;
      await navigator.clipboard.writeText(currentUrl);
      alert("🔗 링크가 클립보드에 복사되었습니다!");
    } catch (err) {
      console.error("링크 복사 실패:", err);
      alert("링크 복사에 실패했습니다.");
    }
  };

  const handleReselect = () => {
    if (window.confirm("현재 추천 목록이 사라집니다. 취향을 다시 선택하시겠습니까?")) {

      // 스토어 상태 초기화 
      reset();
      navigate('/preferences');
    }
  };

  // audio features 계산
  const audioFeatures = useMemo(() => {
    if (playlistTracks.length === 0) return [
      { feature: 'Energy', value: 0 },
      { feature: 'Dance', value: 0 },
      { feature: 'Valence', value: 0 },
      { feature: 'Acoustic', value: 0 },
      { feature: 'Loudness', value: 0 },
      { feature: 'Tempo', value: 0 },
    ];

    // 트랙 feature들의 합, 평균 계산
    const sum = playlistTracks.reduce((acc, track) => ({
      energy: acc.energy + (track.features?.energy || 0),
      danceability: acc.danceability + (track.features?.danceability || 0),
      valence: acc.valence + (track.features?.valence || 0),
      acousticness: acc.acousticness + (track.features?.acousticness || 0),
      loudness: acc.loudness + (track.features?.loudness || 0),
      tempo: acc.tempo + (track.features?.tempo || 0)
    }), {
      energy: 0,
      danceability: 0,
      valence: 0,
      acousticness: 0,
      loudness: 0,
      tempo: 0
    });

    // loudness 정규화
    const normalizeLoudness = (avgLoudness: number) => {
      const avgDb = avgLoudness;
      const normalized = ((avgDb + 60) / 60) * 100;
      return Math.min(100, Math.max(0, Math.round(normalized)));
    };

    // tempo 정규화(0-200으로 가정)
    const normalizeTempo = (avgTempo: number) => {
      return Math.min(100, Math.round((avgTempo / 200) * 100));
    };
    const count = playlistTracks.length;
    const avg = (val: number) => Math.round(val / count);
    // console.log('Audio Feature Sums:', sum);

    // 차트용 포맷으로 변환
    return [
      { feature: 'Energy', value: avg(sum.energy) },
      { feature: 'Dance', value: avg(sum.danceability) },
      { feature: 'Valence', value: avg(sum.valence) },
      { feature: 'Acoustic', value: avg(sum.acousticness) },
      { feature: 'loudness', value: normalizeLoudness(avg(sum.loudness)) },
      { feature: 'tempo', value: normalizeTempo(avg(sum.tempo)) }
    ];

  }, [playlistTracks]);

  //zoom event
  const zoomLevelRef = useRef<number>(1)
  const onChartEvent = {
    'dataZoom': (params: any) => {
      let start = 0;
      let end = 100;

      if (params.batch && params.batch[0]) {
        start = params.batch[0].start;
        end = params.batch[0].end;
      } else {
        start = params.start;
        end = params.end;
      }

      const currentZoom = 100 / (end - start);
      zoomLevelRef.current = currentZoom;
    }
  }

  // echart용 데이터 포맷팅 및 거리 정규화
  const formattedClusterData = useMemo(() => {
    if (!clusterData || !Array.isArray(clusterData) || clusterData.length === 0) return [];

    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;

    clusterData.forEach((item: any) => {
      if (item.emb1 < minX) minX = item.emb1;
      if (item.emb1 > maxX) maxX = item.emb1;
      if (item.emb2 < minY) minY = item.emb2;
      if (item.emb2 > maxY) maxY = item.emb2;
    });

    // 분모가 0이 되지 않도록 함
    const rangeX = maxX - minX || 1;
    const rangeY = maxY - minY || 1;

    return clusterData.map((item: any) => {
      const normalizedX = 5 + ((item.emb1 - minX) / rangeX) * 90;
      const normalizedY = 5 + ((item.emb2 - minY) / rangeY) * 90;

      return [
        normalizedX,
        normalizedY,
        item.cluster_number,
        item.id
      ];
    });
  }, [clusterData]);

  // echart
  const getClusterChartOption = () => {
    return {
      backgroundColor: 'transparent',
      grid: { left: 20, right: 20, top: 20, bottom: 20 },
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(0, 0, 0, 0.85)',
        borderColor: '#555',
        textStyle: { color: '#fff' },
        formatter: (params: any) => {

          // zoom level에 따라 툴팁 내용을 동적으로 변경
          const zoomLevel = zoomLevelRef
          const clusterIndex = params.data[2] + 1;
          const clusterInfo = clusterColors[clusterIndex as keyof typeof clusterColors];
          const trackId = params.data[3];

          // zoomLevel<3이면 클러스터 정보만 보여줌
          if (zoomLevel.current < 3) {
            return `
              <div style="font-weight: bold; margin-bottom: 4px; color: ${clusterInfo?.border || 'white'}">
                ${clusterIndex || 'Unknown Group'}
              </div>
              <div style="font-size: 11px; color: #ccc;">
                확대해보세요
              </div>
            `;
          } else {
            // zoomLevel>=3이면 개별 곡 정보를 보여줌
            return `
               <div style="text-align: left;">
                <div style="font-size: 10px; color: #aaa; margin-bottom: 2px;">Track Info</div>
                <div style="font-weight: bold; font-size: 14px; margin-bottom: 2px;">
                  Track #${trackId}
                </div>
                <div style="color: ${clusterInfo?.border}; font-size: 11px;">
                  ${clusterInfo?.name}
                </div>
              </div>
            `;
          }
        }
      },
      xAxis: { type: 'value', show: false, scale: true },
      yAxis: { type: 'value', show: false, scale: true },
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0],
          filterMode: 'empty',
          maxSpan: 100,
          minSpan: 12.5,
          zoomOnMouseWheel: true,
          moveOnMouseMove: true,
          moveOnMouseWheel: false,
        }, {
          type: 'inside',
          yAxisIndex: [0],
          filterMode: 'empty',
          maxspan: 100,
          minSpan: 12.5,
          zoomOnMouseWheel: true,
          moveOnMouseMove: true,
          moveOnMouseWheel: true,
        },
      ],
      animation: false,
      animationDuration: 0,
      series: [
        {
          type: 'scatter',
          symbolSize: 3,

          // 데이터 연결
          data: formattedClusterData,

          itemStyle: {
            // 클러스터 ID에 따라 색상 자동 지정
            color: (params: any) => {
              const clusterIndex = params.data[2] + 1;
              const colorInfo = clusterColors[clusterIndex as keyof typeof clusterColors];
              return colorInfo?.border || '#ccc'; // 매칭 안되면 회색
            },
            opacity: 0.8,
            shadowBlur: 10,
            shadowColor: 'rgba(0,0,0,0.3)'
          },
          emphasis: {
            scale: 1.5,
            itemStyle: {
              shadowBlur: 15,
              shadowColor: 'white'
            }
          }
        }
      ]
    };
  };

  // 로딩 화면
  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center text-white">
        <Loader2 className="size-10 animate-spin text-teal-500 mb-4" />
        <p className="text-lg">당신의 취향을 분석하여 곡을 추천중입니다...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-teal-900">
      {/* Header */}
      <div className="bg-gradient-to-b from-blue-600/30 to-transparent p-6 md:p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-start gap-6">
            <div className="hidden md:block bg-gradient-to-br from-blue-400 to-teal-400 rounded-2xl size-48 shadow-2xl flex-shrink-0 flex items-center justify-center">
              <Music className="size-24 text-white" />
            </div>

            <div className="flex-1">
              <p className="text-white/60 text-sm mb-2">플레이리스트</p>
              <h1 className="text-3xl md:text-5xl font-bold text-white mb-4">
                나만의 플레이리스트
              </h1>
              <p className="text-white/80 mb-4">
                {playlistTracks.length}개 트랙 • 당신의 취향 기반 추천
              </p>
              <div className="flex gap-3">
                <button 
                  onClick={handlePlayAll}
                  className="bg-gradient-to-r from-blue-500 to-teal-500 text-white px-6 py-3 rounded-full font-bold shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 flex items-center gap-2"
                >
                  {currentTrackIndex !== null ? (
                    <>
                      <Pause className="size-5 fill-white" /> 재생 중지
                    </>
                  ) : (
                    <>
                      <Play className="size-5 fill-white" /> 재생
                    </>
                  )}
                </button>
                <button 
                  onClick={handleShare}
                  className="bg-white/10 backdrop-blur-sm text-white px-4 py-3 rounded-full hover:bg-white/20 transition-all duration-300"
                >
                  <Share2 className="size-5" />
                </button>
                <button className="bg-white/10 backdrop-blur-sm text-white px-4 py-3 rounded-full hover:bg-white/20 transition-all duration-300">
                  <Download className="size-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 md:px-8 pb-12 space-y-8">

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* 1. Radar Chart */}
          <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6">
            <h2 className="text-2xl font-bold text-white mb-6">
              음악 특성 분석
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={audioFeatures}>
                <PolarGrid stroke="#ffffff40" />
                <PolarAngleAxis
                  dataKey="feature"
                  tick={{ fill: '#ffffff', fontSize: 12 }}
                />
                <PolarRadiusAxis
                  angle={90}
                  domain={[0, 100]}
                  tick={{ fill: '#ffffff80' }}
                />
                <Radar
                  name="특성"
                  dataKey="value"
                  stroke="#14b8a6"
                  fill="#14b8a6"
                  fillOpacity={0.6}
                />
              </RadarChart>
            </ResponsiveContainer>
            <div className="mt-4 grid grid-cols-2 gap-3">
              {audioFeatures.map((feature) => (
                <div key={feature.feature} className="text-sm">
                  <div className="flex justify-between text-white/80 mb-1">
                    <span>{feature.feature}</span>
                    <span className="font-semibold">{feature.value}%</span>
                  </div>
                  <div className="bg-white/10 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-teal-500 h-2 rounded-full"
                      style={{ width: `${feature.value}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 2. Cluster Map (ECharts Integration) */}
          <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 flex flex-col">
            <h2 className="text-2xl font-bold text-white mb-6">
              음악 클러스터 맵
            </h2>

            {/* echart */}
            <div className="relative w-full flex-1 min-h-[400px] bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl border border-white/10 overflow-hidden">
              <ReactECharts
                option={getClusterChartOption()}
                style={{ height: '100%', width: '100%' }}
                onEvents={onChartEvent}
              />
              {/* 배경 라벨 */}
              <div className="absolute bottom-3 right-4 text-xs font-medium text-white/30 pointer-events-none">
                Dim 1 →
              </div>
              <div className="absolute top-4 left-3 text-xs font-medium text-white/30 transform -rotate-90 origin-left pointer-events-none">
                ← Dim 2
              </div>
            </div>
          </div>

        </div>

        {/* Additional Insights */}
        <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6">
          <h2 className="text-2xl font-bold text-white mb-4">
            플레이리스트 설명
          </h2>
          <div className="bg-gradient-to-br from-blue-500/20 to-teal-500/20 rounded-xl p-4">
            <div className="text-white text-xl font-bold">{playlistExplanation?.name || "분석 중..."}</div>
            <p className="text-white/60 text-sm mt-2">{playlistExplanation?.description || "데이터를 불러오는 중입니다."}</p>
          </div>
        </div>

        {/* Track List */}
        <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6">
          <h2 className="text-2xl font-bold text-white mb-6">트랙 목록</h2>
          <div className="space-y-2">
            {playlistTracks.map((track, index) => (
              <div
                key={track.id}
                className={`flex items-center gap-4 p-3 rounded-xl hover:bg-white/10 transition-all duration-300 cursor-pointer group ${currentTrackIndex === index ? 'bg-white/10' : ''
                  }`}
                onClick={() => playTrack(index)}
              >
                <div className="text-white/40 w-8 text-center group-hover:hidden">
                  {index + 1}
                </div>
                <button className="hidden group-hover:block">
                  <Play
                    className={`size-8 ${currentTrackIndex === index
                      ? 'text-teal-400 fill-teal-400'
                      : 'text-white'
                      }`}
                  />
                </button>
                <img
                  src={track.imageUrl}
                  alt={track.title}
                  className="size-12 rounded-lg"
                />
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-white truncate">
                    {track.title}
                  </div>
                  <div className="text-sm text-white/60 truncate">
                    {track.artist}
                  </div>
                </div>
                <div className="text-white/60 text-sm hidden md:block">
                  {track.album}
                </div>
                <div className="text-white/40 text-sm">{track.duration}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Reselect Button */}
        <div className="flex justify-center">
          <button
            onClick={handleReselect}
            className="bg-gradient-to-r from-blue-600 to-teal-600 hover:from-blue-500 hover:to-teal-500 text-white px-12 py-5 rounded-2xl font-bold text-xl shadow-2xl hover:shadow-blue-500/50 hover:scale-105 transition-all duration-300 flex items-center gap-3"
          >
            <RefreshCw className="size-7" />
            취향 다시 선택하기
          </button>
        </div>
      </div>
      <SpotifyEmbed 
        trackId={currentTrackId} 
        onClose={() => setCurrentTrackIndex(null)}
        onNext={handleNext}
        onPrev={handlePrev}
        hasNext={currentTrackIndex !== null && currentTrackIndex < playlistTracks.length - 1}
        hasPrev={currentTrackIndex !== null && currentTrackIndex > 0}
      />
    </div>
  );
}


