import sys
from pathlib import Path

# ensure backend/ is on sys.path so `import app` works
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import text
from app.db.session import engine

print('ENGINE_URL', engine.url)

with engine.connect() as conn:
    dbname = conn.execute(text('SELECT DATABASE()')).scalar()
    tables = conn.execute(text('SHOW TABLES')).fetchall()
    print('DATABASE()', dbname)
    print('TABLE_COUNT', len(tables))
    for t in tables[:100]:
        print('TABLE', t[0])
