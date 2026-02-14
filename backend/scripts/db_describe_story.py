import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import text
from app.db.session import engine

TARGETS = [
    'story_shots',
    'story_tts_segments',
    'story_assets',
    'user_generated_images',
    'episode_outputs',
]

with engine.connect() as conn:
    for t in TARGETS:
        print('\n===', t, '===')
        rows = conn.execute(text(f'DESCRIBE {t}')).fetchall()
        for r in rows:
            print(f"{r[0]:30} {r[1]:25} null={r[2]} key={r[3]} default={r[4]} extra={r[5]}")
