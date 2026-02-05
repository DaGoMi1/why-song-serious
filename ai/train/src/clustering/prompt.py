def build_prompt(representative_tracks, feature_summary):
    """
    representative_tracks: list of (title, artist)
    feature_summary: dict {feature: "↑"/"↓"}
    """

    tracks_text = "\n".join(
        [f"- {title} - {artist}" for title, artist in representative_tracks]
    )

    feature_text = "\n".join(
        [f"- {feat} {direction}" for feat, direction in feature_summary.items()]
    )

    prompt = f"""
아래 정보는 사용자의 음악 취향을 바탕으로 추천 이유를 설명하기 위한 것이다.

- 음악 추천 서비스에서 사용자에게 보여주는 설명 문구처럼 자연스럽게 작성
- 음악적 특징과 느낌 중심으로 작성
- 한 줄로 간결하게 자연스러운 한국어로 작성

[대표곡] (이 군집의 성격을 가장 잘 드러내는 곡들)
{tracks_text}

[오디오 특성 요약] (다른 군집들과 비교하여 눈에 띄는 feature)
{feature_text}

위 정보를 바탕으로, 사용자의 취향을 바탕으로 한 추천 이유를 설명하라.
""".strip()
    
    return prompt