import { useState } from 'react';
import { useNavigate } from 'react-router';
import { useDataStore } from '../stores/useDataStore';
import { Zap, Heart, Music, Mic2, Volume2, Activity } from 'lucide-react';

interface FeatureSlider {
  id: string;
  name: string;
  icon: React.ElementType;
  description: string;
  min: number;
  max: number;
  defaultValue: number;
}

const features: FeatureSlider[] = [
  {
    id: 'energy',
    name: '에너지',
    icon: Zap,
    description: '곡의 강렬함과 활동성',
    min: 0,
    max: 1,
    defaultValue: 0.5,
  },
  {
    id: 'valence',
    name: '긍정도',
    icon: Heart,
    description: '곡이 전달하는 긍정적인 느낌',
    min: 0,
    max: 1,
    defaultValue: 0.5,
  },
  {
    id: 'danceability',
    name: '댄스 적합도',
    icon: Music,
    description: '춤추기에 적합한 정도',
    min: 0,
    max: 1,
    defaultValue: 0.5,
  },
  {
    id: 'acousticness',
    name: '어쿠스틱',
    icon: Mic2,
    description: '어쿠스틱 악기 사용 정도',
    min: 0,
    max: 1,
    defaultValue: 0.5,
  },
  {
    id: 'loudness',
    name: '사운드 크기',
    icon: Volume2,
    description: '음악 볼륨',
    min: -60,
    max: 10,
    defaultValue: -30,
  },
  {
    id: 'tempo',
    name: '템포 (BPM)',
    icon: Activity,
    description: '곡의 속도',
    min: 0,
    max: 220,
    defaultValue: 120,
  },
];

export function Preferences() {
  const navigate = useNavigate();
  const { setPreferences } = useDataStore();
  const [featureValues, setFeatureValues] = useState<Record<string, number>>(
    features.reduce((acc, feature) => ({
      ...acc,
      [feature.id]: feature.defaultValue,
    }), {})
  );

  // 슬라이더 움직이면 값 변경
  const handleSliderChange = (featureId: string, value: number) => {
    setFeatureValues((prev) => ({
      ...prev,
      [featureId]: value,
    }));
  };

  const handleContinue = async () => {
    // Store에 preferences 저장
    const payload = {
      acousticness: featureValues['acousticness'],
      valence: featureValues['valence'],
      energy: featureValues['energy'],
      danceability: featureValues['danceability'],
      loudness: featureValues['loudness'],
      tempo: featureValues['tempo'],
    };
    setPreferences(payload);
    navigate('/discover');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-teal-900 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 md:mb-12">
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-3">
            당신의 음악 취향을 알려주세요
          </h1>
          <p className="text-white/80 text-lg">
            슬라이더를 조절하여 선호하는 음악 특성을 설정해주세요
          </p>
        </div>

        {/* Feature Sliders */}
        <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-6 md:p-8 mb-8 shadow-2xl space-y-8">
          {features.map((feature) => {
            const Icon = feature.icon;
            const value = featureValues[feature.id];
            const percentage = ((value - feature.min) / (feature.max - feature.min)) * 100;

            return (
              <div key={feature.id} className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="bg-gradient-to-br from-blue-500 to-teal-500 rounded-xl p-2.5">
                      <Icon className="size-5 text-white" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-white">
                        {feature.name}
                      </h3>
                      <p className="text-sm text-white/60">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-white">
                      {value}
                    </div>
                    {feature.id === 'tempo' && (
                      <div className="text-xs text-white/60">BPM</div>
                    )}
                  </div>
                </div>

                {/* Slider */}
                <div className="relative">
                  <input
                    type="range"
                    min={feature.min}
                    max={feature.max}
                    value={value}
                    onChange={(e) => handleSliderChange(feature.id, Number(e.target.value))}
                    className="w-full h-3 bg-white/20 rounded-full appearance-none cursor-pointer slider"
                    style={{
                      background: `linear-gradient(to right, 
                        rgb(59 130 246) 0%, 
                        rgb(20 184 166) ${percentage}%, 
                        rgba(255, 255, 255, 0.2) ${percentage}%, 
                        rgba(255, 255, 255, 0.2) 100%)`,
                    }}
                  />
                  <style>{`
                    .slider::-webkit-slider-thumb {
                      appearance: none;
                      width: 24px;
                      height: 24px;
                      border-radius: 50%;
                      background: linear-gradient(135deg, #3b82f6, #14b8a6);
                      cursor: pointer;
                      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                      transition: transform 0.2s;
                    }
                    .slider::-webkit-slider-thumb:hover {
                      transform: scale(1.2);
                    }
                    .slider::-moz-range-thumb {
                      width: 24px;
                      height: 24px;
                      border-radius: 50%;
                      background: linear-gradient(135deg, #3b82f6, #14b8a6);
                      cursor: pointer;
                      border: none;
                      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                      transition: transform 0.2s;
                    }
                    .slider::-moz-range-thumb:hover {
                      transform: scale(1.2);
                    }
                  `}</style>
                </div>

                {/* Labels */}
                <div className="flex justify-between text-xs text-white/50">
                  <span>낮음</span>
                  <span>높음</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Continue Button */}
        <button
          onClick={handleContinue}

          className={`w-full py-4 px-6 rounded-full font-bold text-lg transition-all duration-300 bg-white text-blue-600 shadow-xl hover:shadow-2xl hover:scale-105 : ''
            }`}
        >
          {'음악 추천 받기'}
        </button>
      </div>
    </div>
  );
}