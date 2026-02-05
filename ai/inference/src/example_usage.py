from core.recommender import RecommenderEngine
import yaml

# 초기화 (서버 뜰 때 1번)
with open("config/config.yaml") as f:
    config = yaml.safe_load(f)
engine = RecommenderEngine(config)

# 사용 (API 요청 올 때마다)
results = engine.recommend(seed_song_ids=["0UaMYEvWZi0ZqiDOoHU3YI", "1HwpWwa6bnqqRhK8agG4RS"])
print(results)