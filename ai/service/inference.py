from core.recommender import RecommenderEngine
import yaml
import time

# 1. 설정 로드
with open('./config.yaml', 'r') as f:
    config = yaml.safe_load(f)
print("설정값 불러오기 성공")

# 2. 엔진 초기화 (모델 로딩 시간 포함)
start_init = time.time()
engine = RecommenderEngine(config)
end_init = time.time()
print(f"엔진 불러오기 성공 (소요시간: {end_init - start_init:.4f}s)")

# 3. 하이브리드 추천 테스트
print("\n--- 하이브리드 추천 결과 ---")
seed_ids = [
    "0UaMYEvWZi0ZqiDOoHU3YI", "6I9VzXrHxO9rA9A5euc8Ak", 
    "1AWQoqb9bSvzTjaLralEkT", "68vgtRHr7iZHpzGpon6Jlo", "3BxWKCI06eQ5Od8TY2JBeA"
]

start_hybrid = time.time()
hybrid_res = engine.recommend_hybrid(pid=100, seed_song_ids=seed_ids)
end_hybrid = time.time()

print(hybrid_res[['id', 'name', 'score']].head())
print(f"하이브리드 전체 소요시간: {end_hybrid - start_hybrid:.4f}s")

# 4. 슬라이더 추천 테스트 (Annoy)
print("\n--- 슬라이더 추천 결과 ---")
slider_input = {
    'energy': 0.8, 'valence': 0.2, 'danceability': 0.5, 
    'acousticness': 0.7, 'instrumentalness': 0.6, 'tempo': 120
}

start_slider = time.time()
slider_res = engine.recommend_by_slider(slider_input)
end_slider = time.time()

print(slider_res[['id', 'name']].head())
print(f"슬라이더 검색 소요시간: {end_slider - start_slider:.4f}s")