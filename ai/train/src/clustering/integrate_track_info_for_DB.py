import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

def get_track_info_for_DB(
        src_df: pd.DataFrame,
        deepFM_emb: pd.DataFrame,
        CML_emb: pd.DataFrame,
        feat_list: list
        ) -> pd.DataFrame:
    """
    소스 데이터프레임, 라벨인코더, DeepFM와 CML의 임베딩을 받고, ERD 트랙에 맞는 데이터프레임을 반환합니다.
    
    :param src_df: 원본 데이터 (add_feature_v3.csv)
    :param encoder: 학습용 ID와 API용 ID를 매핑해주는 라벨인코더
    :param deepFM_emb: DeepFM 모델에서 나온 임베딩
    :param CML_emb: CML 모델에서 나온 임베딩

    :return: ERD 트랙 파트에 맞는 데이터프레임
    :return columns:
    [ spotify_track_id, name, artist, album, duration_ms, popularity,
    preview_url, image_url, audio_features, emb_deepfm, emb_cml ]

    """
    out_df = src_df[['id', 'name', 'artists']].copy(deep=True)
    out_df.columns = ['spotify_track_id', 'name', 'artists']

    # 현재 데이터가 불완전하기 때문에 album, duration_ms, preview_url, image_url은 나중에 수정
    # out_df[['album', 'duration_ms'] = src_df['album', 'duration_ms']
    out_df['popularity'] = src_df['popularity']
    # out_df[['preview_url', 'image_url']] = src_df[['preview_url', 'image_url']]
    out_df[feat_list] = src_df[feat_list]
    print(out_df.values.shape)
    print(deepFM_emb.values.shape)
    print(CML_emb.values.shape)

    df_emb_values = deepFM_emb.iloc[:, 1:].values
    cml_emb_values = CML_emb.iloc[:, 1:].values

    df_emb_cols = [f"DeepFM_emb{i}" for i in range(1, df_emb_values.shape[1] + 1)]
    cml_emb_cols = [f"CML_emb{i}" for i in range(1, cml_emb_values.shape[1] + 1)]

    new_embs_df = pd.DataFrame(
        np.hstack([df_emb_values, cml_emb_values]),
        columns=df_emb_cols + cml_emb_cols,
        index=out_df.index
    )

    out_df = pd.concat([out_df, new_embs_df], axis=1)
    
    return out_df

if __name__=="__main__":
    """
    get_track_DB.py 파일을 실행하면 json 형식으로 파일을 저장합니다.

    * 실행방법
    >> python integrate_track_info_for_DB.py
    """

    deepFM_emb_path = "/data/ephemeral/home/clustering/embs/DeepFM_embeddings.csv"
    CML_emb_path = "/data/ephemeral/home/clustering/embs/CML_embeddings.csv"
    src_path = "/data/ephemeral/home/data/item_meta.csv"
    mapping_path = "/data/ephemeral/home/data/item_label_mapping.csv"
    feat_list = ["acousticness","valence","energy","danceability",
                 "instrumentalness","loudness","speechiness","tempo",
                 "popularity"]

    deepFM_emb = pd.read_csv(deepFM_emb_path)
    CML_emb = pd.read_csv(CML_emb_path)
    src_df = pd.read_csv(src_path)
    item_mapping_df = pd.read_csv(mapping_path)
    deepFM_emb = deepFM_emb.rename(columns={"id":"spotify_track_id"})
    CML_emb = CML_emb.rename(columns={"id":"spotify_track_id"})

    print("트랙 정보를 통합중입니다.")
    track_info_for_DB = get_track_info_for_DB(src_df, deepFM_emb, CML_emb, feat_list)
    track_info_for_DB.to_json('/data/ephemeral/home/data/track_info_for_DB.json', orient='records', force_ascii=False, indent=4)
    print("트랙 정보가 저장됐습니다!")