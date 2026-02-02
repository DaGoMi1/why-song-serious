import json

file_path = 'backend_test\clustered_data.json'  # 파일 경로를 확인하세요

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. 모든 cluster_number만 추출
    # (데이터가 없거나 키가 없는 경우를 대비해 get 사용)
    cluster_numbers = [item.get('cluster_number') for item in data if 'cluster_number' in item]

    # 2. 중복 제거하여 개수 세기 (set 사용)
    unique_clusters = set(cluster_numbers)
    
    # 3. 결과 출력
    print(f"✅ 총 데이터 개수: {len(data)}개")
    print(f"✅ 유니크한 클러스터 개수: {len(unique_clusters)}개")
    
    if unique_clusters:
        print(f"🔢 가장 작은 번호: {min(unique_clusters)}")
        print(f"🔢 가장 큰 번호: {max(unique_clusters)}")
        print("-" * 30)
        print(f"💡 팁: 프론트엔드 generateGradientColors({max(unique_clusters) + 1}) 이상으로 설정하세요.")
    else:
        print("⚠️ 클러스터 데이터가 없습니다.")

except FileNotFoundError:
    print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
except json.JSONDecodeError:
    print("❌ JSON 파일 형식이 올바르지 않습니다.")