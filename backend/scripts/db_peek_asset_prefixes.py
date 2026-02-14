import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import text
from app.db.session import engine

# Inspect prefixes in story_assets.s3_key

with engine.connect() as conn:
    rows = conn.execute(text(
        "SELECT s3_key FROM story_assets ORDER BY id DESC LIMIT 500"
    )).fetchall()

c = Counter()
for (k,) in rows:
    if not k:
        continue
    k = str(k).lstrip('/')
    prefix = k.split('/', 1)[0]
    c[prefix] += 1

for p, n in c.most_common(30):
    print(p, n)
