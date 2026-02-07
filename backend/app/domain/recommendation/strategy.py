import random
from collections import Counter

import numpy as np
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.track.model import Track
from app.domain.cluster.model import Cluster


# ──────────────────────────────────────────────
# 1. 그룹 분할
#    입력 트랙 N개를 K개의 그룹으로 분할한다.
#    현재는 K=1 (전체를 하나의 그룹으로 취급).
#    추후 클러스터 기반 분할 등으로 확장 가능.
# ──────────────────────────────────────────────

def split_into_groups(tracks: list[Track]) -> list[list[Track]]:
    return [tracks]


# ──────────────────────────────────────────────
# 2. 대표 벡터 생성
#    각 그룹의 embedding을 집계하여 하나의 벡터로 만든다.
#    현재는 그룹 내 embedding의 평균 벡터를 사용.
# ──────────────────────────────────────────────

def compute_group_vector(group: list[Track]) -> list[float]:
    embeddings = np.array([track.embedding for track in group])
    return np.mean(embeddings, axis=0).tolist()


# ──────────────────────────────────────────────
# 3. 벡터 검색
#    각 그룹의 대표 벡터로 DB에서 유사 트랙을 조회한다.
#    <#> 연산자 (내적, 작을수록 유사)를 사용.
#    검색 개수: 그룹 크기 + M (입력 트랙이 결과에 포함될 수 있으므로 여유분 확보)
# ──────────────────────────────────────────────

async def search_by_group(
    db: AsyncSession,
    group_vector: list[float],
    limit: int,
) -> list[tuple[Track, float]]:
    embedding_str = f"[{','.join(map(str, group_vector))}]"

    query = text("""
        SELECT id, spotify_track_id, name, artist, album,
               duration_ms, popularity, image_url,
               raw_features, norm_features, embedding, cluster_id,
               (embedding <#> :embedding) AS score
        FROM tracks
        ORDER BY embedding <#> :embedding
        LIMIT :limit
    """)

    result = await db.execute(query, {"embedding": embedding_str, "limit": limit})
    rows = result.fetchall()

    tracks_with_scores = []
    for row in rows:
        track = Track(
            id=row.id,
            spotify_track_id=row.spotify_track_id,
            name=row.name,
            artist=row.artist,
            album=row.album,
            duration_ms=row.duration_ms,
            popularity=row.popularity,
            image_url=row.image_url,
            raw_features=row.raw_features,
            norm_features=row.norm_features,
            embedding=row.embedding,
            cluster_id=row.cluster_id,
        )
        tracks_with_scores.append((track, row.score))

    return tracks_with_scores


# ──────────────────────────────────────────────
# 4. 결과 통합 및 가중치 부여
#    여러 그룹의 검색 결과를 하나로 합친다.
#    동일 트랙이 여러 그룹에서 등장하면 최고 스코어를 채택.
#    현재는 K=1이므로 사실상 패스스루.
#    추후 그룹별 가중치 로직을 여기서 확장.
# ──────────────────────────────────────────────

def merge_results(
    group_results: list[list[tuple[Track, float]]],
) -> list[tuple[Track, float]]:
    best: dict[int, tuple[Track, float]] = {}

    for results in group_results:
        for track, score in results:
            if track.id not in best or score < best[track.id][1]:
                best[track.id] = (track, score)

    return sorted(best.values(), key=lambda x: x[1])


# ──────────────────────────────────────────────
# 5. 필터링
#    입력 트랙 제거 후 상위 M개를 반환한다.
# ──────────────────────────────────────────────

def filter_and_trim(
    ranked: list[tuple[Track, float]],
    exclude_ids: set[int],
    limit: int,
) -> list[Track]:
    return [track for track, _ in ranked if track.id not in exclude_ids][:limit]


# ──────────────────────────────────────────────
# 6. Description 생성
#    추천 결과의 클러스터 최빈값 기반으로 description을 결정한다.
#    동률일 경우 랜덤 선택.
# ──────────────────────────────────────────────

async def generate_description(db: AsyncSession, tracks: list[Track]) -> str:
    cluster_ids = [track.cluster_id for track in tracks]
    counter = Counter(cluster_ids)
    max_count = counter.most_common(1)[0][1]

    top_cluster_ids = [cid for cid, cnt in counter.items() if cnt == max_count]
    chosen_cluster_id = random.choice(top_cluster_ids)

    result = await db.execute(
        select(Cluster.cluster_description).where(Cluster.id == chosen_cluster_id)
    )
    return result.scalar_one()


# ──────────────────────────────────────────────
# 파이프라인 실행
#    위 단계들을 순서대로 실행하는 진입점.
#    strategy 내부의 각 단계를 교체하면 추천 방식을 변경할 수 있다.
# ──────────────────────────────────────────────

async def run_embedding_pipeline(
    db: AsyncSession,
    input_tracks: list[Track],
    recommendation_count: int = 10,
) -> tuple[list[Track], str]:
    # 1) 그룹 분할
    groups = split_into_groups(input_tracks)

    # 2~3) 각 그룹별 대표 벡터 생성 → 검색
    group_results = []
    for group in groups:
        vector = compute_group_vector(group)
        search_limit = len(group) + recommendation_count
        results = await search_by_group(db, vector, search_limit)
        group_results.append(results)

    # 4) 결과 통합
    ranked = merge_results(group_results)

    # 5) 입력 트랙 제거 및 상위 M개 선택
    exclude_ids = {track.id for track in input_tracks}
    recommended = filter_and_trim(ranked, exclude_ids, recommendation_count)

    # 6) Description 생성
    description = await generate_description(db, recommended)

    return recommended, description
