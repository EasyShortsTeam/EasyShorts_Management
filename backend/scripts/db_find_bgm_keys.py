import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import text
from app.db.session import engine

patterns = [
    '%bgm%',
    '%BGM%',
]

with engine.connect() as conn:
    found = []
    for pat in patterns:
        rows = conn.execute(text(
            "SELECT id, episode_id, asset_type, provider, s3_key, created_at "
            "FROM story_assets WHERE s3_key LIKE :pat ORDER BY id DESC LIMIT 50"
        ), {"pat": pat}).fetchall()
        for r in rows:
            found.append(r)

if not found:
    print('NO_MATCH')
else:
    for r in found:
        print('---')
        print('id', r[0])
        print('episode_id', r[1])
        print('asset_type', r[2], 'provider', r[3])
        print('s3_key', r[4])
        print('created_at', r[5])
