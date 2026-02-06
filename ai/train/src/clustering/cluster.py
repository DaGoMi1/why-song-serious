from sklearn.manifold import TSNE
import numpy as np
from sklearn.cluster import KMeans
import pandas as pd
from time import time

def tsne(full_embedding, dim):
    """
    원본 임베딩을 받고, dim-dimension까지 t-SNE 알고리즘으로 차원을 축소해 df 형태로 리턴해줍니다.
    
    :param full_embedding: 풀 임베딩
    :param dim: 타겟 차원 수
    """

    tsne = TSNE(
        n_components=dim,
        perplexity=30,
        learning_rate='auto',
        init='pca',
        max_iter=1000,
        random_state=42,
        n_jobs=-1
    )

    start_time = time()
    print("t-SNE 연산이 시작됐습니다!")
    low_order_embed_np = tsne.fit_transform(full_embedding)

    end_time = time()
    print(f"t-SNE 연산이 끝났습니다! {end_time-start_time} 걸렸습니다.")
    low_order_embed_df = pd.DataFrame(low_order_embed_np, columns=['emb0','emb1'])

    return low_order_embed_df

def kmeans(embedding, random_state, k):
    """
    2차원 임베딩을 받고, k-means 클러스터링 알고리즘 수행 후 df 형태로 return합니다.
    
    :param embedding: 풀 임베딩
    :param k: 군집 수
    """

    cluster_summary = []

    kmeans = KMeans(n_clusters=k, random_state=random_state).fit(embedding)
    centroids = kmeans.cluster_centers_
    labels = kmeans.labels_

    for i in range(k):
        cluster_points = embedding[labels == i]
        
        distances = np.linalg.norm(cluster_points - centroids[i], axis=1)
        radius = np.max(distances)
        
        cluster_summary.append({
            'cluster_number': i,
            'emb0': centroids[i][0],
            'emb1': centroids[i][1],
            'radius': radius
        })

    cluster_df = pd.DataFrame(cluster_summary)

    return cluster_df, kmeans.labels_


if __name__=="__main__":

    # model 인자는 파일명과 관련.
    model = "DeepFM"
    df = pd.read_csv(f"/data/ephemeral/home/clustering/embs/{model}_embeddings.csv")
    full_embedding = df.drop("id", axis=1).values
    emb = tsne(full_embedding, 2)

    print(f"임베딩 shape은 {emb.shape}입니다.")

    cluster_info_df, labels = kmeans(emb.values, 42, 600)

    emb['cluster_number'] = labels
    emb.to_json(f'/data/ephemeral/home/clustering/low_dim_info/{model}_tsne_embed.json',
                orient='records', indent=4)
    print("저차원 임베딩이 성공적으로 저장됐습니다!")
    
    cluster_info_df.to_json(f'/data/ephemeral/home/clustering/low_dim_info/{model}_cluster_info.json',
                            orient='records', indent=4)
    print("클러스터 정보가 성공적으로 저장됐습니다!")