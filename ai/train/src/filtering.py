import pandas as pd
import numpy as np
from annoy import AnnoyIndex
from sklearn.preprocessing import MinMaxScaler
import time

# Local에서 Service 부분으로 넘어가면 DB에서 받아오는 방식으로 변경
data_path = "./data/"
feature_df = pd.read_csv(data_path + "add_feature_v1.csv")

# pid컬럼 제거 후 id 기준으로 중복 제거, 최종적으로 인덱스 리셋
# annoy로 곡 찾을 때 오디오피쳐를 기준으로 찾는데 중복된 곡이 계속 나오는 상황 방지
filtered_df = feature_df.drop('pid', axis=1)
filtered_df = filtered_df.drop_duplicates('id', keep='first')
filtered_df = filtered_df.reset_index(drop=True)

print(f"전체 곡 개수: {len(filtered_df)}")

# 사용할 오디오 피쳐
audio_cols = ['energy', 'valence', 'danceability', 'acousticness', 'instrumentalness', 'tempo']

# scikit-learn의 MinMaxScaler를 통해 각 컬럼의 수치를 0~1로 변환
scaler = MinMaxScaler()
filtered_df[audio_cols] = scaler.fit_transform(filtered_df[audio_cols])

# 유저가 슬라이더를 통해 다음과 같이 설정해서 입력 했다고 가정
# 마찬가지로 실제 Service화 되면 client로부터 받아오도록 변경
user_slider_input = {
    'valence': 0.8, 'danceability': 0.2, 
    'energy': 0.8, 'tempo': 120, 'popularity': 60
}

# 유저의 입력값도 MinMaxScaler
user_input_df = pd.DataFrame([user_slider_input])
slider_vector_scaled = scaler.transform(user_input_df[audio_cols])[0]

# 스케일링 된 벡터 출력
print(slider_vector_scaled)

# Annoy에게 그릴 map의 차원을 구하는 과정
f = len(audio_cols) # 오디오 컬럼 개수 5 -> 5차원

# 5차원 데이터를 담을 검색 인덱스를 만듦, 'angular'는 각도를 기반으로 유사도 측정
# 그외에 'euclidean', 'manhattan', 'dot', 'hamming'이 있음
annoy_index = AnnoyIndex(f, 'euclidean')

# 위에서 만든 index에 실제 곡 데이터를 추가해서 맵을 채워나가는 과정
audio_data = filtered_df[audio_cols].to_numpy()
for i, vector in enumerate(audio_data):
    annoy_index.add_item(i, vector)

# 최종적으로 채워진 annoy map을 n개로 나눔, 여기서 n은 10
annoy_index.build(10)

start_time = time.time()

# 채워진 맵을 통해 파라미터로 입력한 벡터와 가장 가까운 아이템을 n개 가져오는 부분, 여기서 n은 100
# include_distance는 아이템만 가져오지말고, 추가로 해당 아이템과의 거리가 어느 정도인지도 가져오라는 파라미터
indices, distances = annoy_index.get_nns_by_vector(slider_vector_scaled, 100, include_distances=True)

# 가져온 indices를 통해 후보군 생성 및 거리 정보 포함
candidates = filtered_df.iloc[indices].copy()
candidates['similarity_distance'] = distances

# MinMaxScaler 복원
candidates[audio_cols] = scaler.inverse_transform(candidates[audio_cols])

end_time = time.time()

print("\n추출된 후보군 상위 10개")
print(candidates[['id', 'name', 'artists', 'energy', 'tempo', 'popularity', 'similarity_distance']].head(10))

print(f"걸린 시간: {end_time - start_time}")