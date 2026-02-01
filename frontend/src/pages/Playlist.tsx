import { useState, useEffect, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router';
import type { Track } from '../types/track';
import { Play, Heart, Share2, Download, Music, RefreshCw } from 'lucide-react';
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

// 클러스터 색상 정의 (1~4번 그룹)
// 1. 그라데이션을 위한 기본 4가지 색상 정의 (RGB 값)
const baseColors = [
  { r: 59, g: 130, b: 246, name: 'test' }, // 파랑 (#3b82f6)
  { r: 239, g: 68, b: 68, name: 'test' },  // 빨강 (#ef4444)
  { r: 168, g: 85, b: 247, name: 'test' },            // 보라 (#a855f7)
  { r: 20, g: 184, b: 166, name: 'test' },   // 청록 (#14b8a6)
];

// 2. 두 색상 사이를 섞어주는 함수 (Interpolation)
const interpolateColor = (color1: any, color2: any, factor: number) => {
  const result = {
    r: Math.round(color1.r + (color2.r - color1.r) * factor),
    g: Math.round(color1.g + (color2.g - color1.g) * factor),
    b: Math.round(color1.b + (color2.b - color1.b) * factor),
  };
  return result;
};

// 3. RGB를 Hex(#RRGGBB)로 변환하는 함수
const rgbToHex = (r: number, g: number, b: number) => {
  return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
};

// 4. 1~40번까지 색상 자동 생성 함수
const generateGradientColors = (totalSteps: number) => {
  const colors: Record<number, { bg: string; border: string; name: string }> = {};

  for (let i = 0; i < totalSteps; i++) {
    // 현재 단계가 전체 중 어디쯤인지 비율 계산 (0 ~ 1)
    const distinctRatio = i / (totalSteps - 1);
    
    // 전체 비율을 3개의 구간(파랑-빨강, 빨강-보라, 보라-청록)으로 나눔
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

// ⭐️ 최종 결과: 1~40번 색상이 생성됨
const clusterColors = generateGradientColors(50);

export function Playlist() {
  const navigate = useNavigate();
  const [playlistTracks, setPlaylistTracks] = useState<Track[]>([]);
  const [currentPlaying, setCurrentPlaying] = useState<string | null>(null);

  const {tracks, clusterData, fetchAllData, isLoading } = useDataStore();

  useEffect(() => {
    if (tracks.length === 0) {
      fetchAllData();
    }
  }, [fetchAllData, tracks.length])

  useEffect(() => {
    if (tracks.length === 0) return;
    const selectedTrackIds = localStorage.getItem('selectedTracks');
    
    // 데이터 로드 
    const ids = selectedTrackIds ? JSON.parse(selectedTrackIds) : [];

    const selectedTracks = tracks.filter((track) => ids.includes(track.id));
    const recommendedTracks = tracks.filter((track) => !ids.includes(track.id));
    const finalPlaylist = [...selectedTracks, ...recommendedTracks.slice(0, 6)];
    
    setPlaylistTracks(finalPlaylist.length > 0 ? finalPlaylist : tracks);
  }, [navigate, tracks]);

  const playTrack = (trackId: string) => {
    setCurrentPlaying(currentPlaying === trackId ? null : trackId);
  };

  const handleReselect = () => {
    navigate('/preferences');
  };

  const audioFeatures = [
    { feature: 'Energy', value: 70 },
    { feature: 'Danceability', value: 60 },
    { feature: 'Valence', value: 80 },
    { feature: 'Acousticness', value: 25 },
    { feature: 'Instrumentalness', value: 15 },
    { feature: 'Speechiness', value: 20 },
  ];

  //zoom event
  const zoomLevelRef=useRef<number>(1)
  const onChartEvent={
    'dataZoom':(params: any)=>{
      let start=0;
      let end=100;

      if (params.batch && params.batch[0]){
        start=params.batch[0].start;
        end=params.batch[0].end;
      }else{
        start=params.start;
        end=params.end;
      }

      const currentZoom=100/(end-start);
      zoomLevelRef.current=currentZoom;
    }
  }

  // 차트 옵션
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
          // 파이썬은 0,1,2,3을 주지만, 프론트는 1,2,3,4를 사용하므로 +1
          // zoom level에 따라 툴팁 내용을 동적으로 변경
          const zoomLevel = zoomLevelRef
          const clusterIndex = params.data[2] + 1;
          const clusterInfo = clusterColors[clusterIndex as keyof typeof clusterColors];
          
          // zoomLevel<3이면 클러스터 정보만 보여줌
          if(zoomLevel.current < 3){
            return `
              <div style="font-weight: bold; margin-bottom: 4px; color: ${clusterInfo?.border || 'white'}">
                ${clusterInfo?.name || 'Unknown Group'}
              </div>
              <div style="font-size: 11px; color: #ccc;">
                확대해보세요
              </div>
            `;
          }else{
            //zoomLevel>=3이면 개별 곡 정보를 보여줌
            return `
               <div style="text-align: left;">
                <div style="font-size: 10px; color: #aaa; margin-bottom: 2px;">Track Info</div>
                <div style="font-weight: bold; font-size: 14px; margin-bottom: 2px;">
                  Track #${params.dataIndex}
                </div>
                <div style="color: ${clusterInfo?.border}; font-size: 11px;">
                  ${clusterInfo?.name}
                </div>
              </div>
            `;
          }
        }
      },
      xAxis: { type:'value', show: false, scale: true },
      yAxis: { type:'value', show: false, scale: true },
      dataZoom: [
        { type: 'inside', 
          xAxisIndex: [0], 
          filterMode: 'empty',
          maxSpan: 100,
          minSpan: 12.5,
          zoomOnMouseWheel: true, 
          moveOnMouseMove: true,  
          moveOnMouseWheel: true,
         },{ type: 'inside', 
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
      animationDuration:0,
      series: [
        {
          type: 'scatter',
          symbolSize: 8, // 점 크기 살짝 키움
          
          // 데이터 연결
          data: clusterData, 

          itemStyle: {
            // 클러스터 ID(3번째 값)에 따라 색상 자동 지정
            color: (params: any) => {
              const clusterIndex = params.data[2] + 1; // 0->1, 1->2...
              const colorInfo = clusterColors[clusterIndex as keyof typeof clusterColors];
              return colorInfo?.border || '#ccc'; // 매칭 안되면 회색
            },
            opacity: 0.8,
            borderColor: 'rgba(255,255,255,0.8)',
            borderWidth: 1,
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
                <button className="bg-gradient-to-r from-blue-500 to-teal-500 text-white px-6 py-3 rounded-full font-bold shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 flex items-center gap-2">
                  <Play className="size-5 fill-white" />
                  재생
                </button>
                <button className="bg-white/10 backdrop-blur-sm text-white px-4 py-3 rounded-full hover:bg-white/20 transition-all duration-300">
                  <Heart className="size-5" />
                </button>
                <button className="bg-white/10 backdrop-blur-sm text-white px-4 py-3 rounded-full hover:bg-white/20 transition-all duration-300">
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

            {/* 범례 (Legend) */}
            <div className="mt-4 grid grid-cols-2 gap-2">
              {Object.entries(clusterColors).map(([clusterId, cluster]) => (
                <div key={clusterId} className="flex items-center gap-2 text-sm">
                  <div
                    className="size-3 rounded-full"
                    style={{ backgroundColor: cluster.border }}
                  />
                  <span className="text-white/70">{cluster.name}</span>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Additional Insights */}
        <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6">
          <h2 className="text-2xl font-bold text-white mb-4">
            플레이리스트 인사이트
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gradient-to-br from-blue-500/20 to-teal-500/20 rounded-xl p-4">
              <div className="text-blue-300 text-sm mb-2">주요 분위기</div>
              <div className="text-white text-xl font-bold">에너제틱</div>
              <p className="text-white/60 text-sm mt-2">
                활기차고 역동적인 트랙이 많습니다
              </p>
            </div>
            <div className="bg-gradient-to-br from-teal-500/20 to-cyan-500/20 rounded-xl p-4">
              <div className="text-teal-300 text-sm mb-2">댄스 적합도</div>
              <div className="text-white text-xl font-bold">70%</div>
              <p className="text-white/60 text-sm mt-2">
                춤추기 좋은 곡들로 구성되어 있습니다
              </p>
            </div>
            <div className="bg-gradient-to-br from-cyan-500/20 to-blue-500/20 rounded-xl p-4">
              <div className="text-cyan-300 text-sm mb-2">긍정도</div>
              <div className="text-white text-xl font-bold">75%</div>
              <p className="text-white/60 text-sm mt-2">
                밝고 긍정적인 느낌의 플레이리스트입니다
              </p>
            </div>
          </div>
        </div>

        {/* Track List */}
        <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6">
          <h2 className="text-2xl font-bold text-white mb-6">트랙 목록</h2>
          <div className="space-y-2">
            {playlistTracks.map((track, index) => (
              <div
                key={track.id}
                className={`flex items-center gap-4 p-3 rounded-xl hover:bg-white/10 transition-all duration-300 cursor-pointer group ${
                  currentPlaying === track.id ? 'bg-white/10' : ''
                }`}
                onClick={() => playTrack(track.id)}
              >
                <div className="text-white/40 w-8 text-center group-hover:hidden">
                  {index + 1}
                </div>
                <button className="hidden group-hover:block">
                  <Play
                    className={`size-8 ${
                      currentPlaying === track.id
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
    </div>
  );
}