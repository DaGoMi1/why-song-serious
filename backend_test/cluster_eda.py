import json
import matplotlib.pyplot as plt
import os

# 파일 경로 설정 (본인 환경에 맞게 수정)
file_path = os.path.join('backend_test', 'clustered_data.json')

try:
    # 1. 데이터 로드
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"데이터 로드 완료: {len(data)}개")

    # 2. 좌표 및 클러스터 정보 추출
    # emb1, emb2가 있는 데이터만 필터링
    valid_data = [d for d in data if 'emb1' in d and 'emb2' in d]
    
    x = [d['emb1'] for d in valid_data]
    y = [d['emb2'] for d in valid_data]
    clusters = [d.get('cluster_number', -1) for d in valid_data] # 없으면 -1

    # 3. 데이터 범위(Scale) 확인 (콘솔 출력용)
    print(f"\n📊 데이터 분포 확인:")
    print(f"X (emb1) 범위: {min(x):.6f} ~ {max(x):.6f}")
    print(f"Y (emb2) 범위: {min(y):.6f} ~ {max(y):.6f}")

    # 4. 시각화 (Scatter Plot)
    plt.figure(figsize=(12, 10)) # 그래프 크기 설정

    # 산점도 그리기
    # c=clusters: 클러스터 번호에 따라 색상 자동 지정
    # cmap='tab20': 색상 팔레트 (tab10, viridis, jet 등 변경 가능)
    # s=10: 점 크기 (데이터가 많으면 줄이세요)
    # alpha=0.6: 투명도 (점들이 겹쳐 있는지 확인하기 좋음)
    scatter = plt.scatter(x, y, c=clusters, cmap='tab20', s=15, alpha=0.7)

    # 범례(Legend) 추가
    plt.legend(*scatter.legend_elements(), title="Cluster No.")

    # 그래프 꾸미기
    plt.title(f"Cluster Visualization (Total: {len(valid_data)})", fontsize=16)
    plt.xlabel("Embedding Dimension 1 (emb1)", fontsize=12)
    plt.ylabel("Embedding Dimension 2 (emb2)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5) # 격자 추가

    # 5. 그래프 출력
    plt.tight_layout()
    plt.show()

except FileNotFoundError:
    print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
except Exception as e:
    print(f"❌ 오류 발생: {e}")