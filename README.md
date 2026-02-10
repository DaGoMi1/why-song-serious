# 파일 구조

```
.
├── ai/
├── backend/
├── frontend/
├── .gitignore
└── README.md
```
<details>
   <summary><h2>AI</h2></summary>

```
ai/
├── inference/
│   ├── service_assets/
│   └── src/
│       ├── api/
│       ├── config/
│       ├── core/
│       ├── models/
│       └── main.py
├── train/
│   ├── checkpoints/
│   ├── configs/
│   ├── data/
│   ├── src/
│   │   ├── clustering/
│   │   ├── dataloaders/
│   │   ├── models/
│   │   ├── evaluator.py
│   │   ├── filtering.py
│   │   ├── losses.py
│   │   ├── retriever.py
│   │   ├── trainer.py
│   │   └── utils.py
│   └── main.py
└── requirements.txt

```
</details>
<details>
   <summary><h2>BE</h2></summary>

```
backend/
├── alembic/
├── app/
│   ├── auth/
│   ├── common/
│   ├── domain/
│   │   ├── cluster/
│   │   ├── interaction/
│   │   ├── playlist/
│   │   ├── preference/
│   │   ├── recommendation/
│   │   ├── track/
│   │   └── user/
│   ├── config.py
│   ├── database.py
│   └── main.py
├── README.md
├── alembic.ini
└── pyproject.toml
```
</details>
<details>
   <summary><h2>FE</h2></summary>

```
frontend/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   ├── data/
│   ├── pages/
│   │   ├── Discover.tsx
│   │   ├── Landing.tsx
│   │   ├── Playlist.tsx
│   │   └── Preferences.tsx
│   ├── stores/
│   ├── types/
│   ├── App.tsx
│   ├── index.css
│   ├── main.tsx
│   └── routes.ts
├── package.json
└── README.md
```
</details>
