from sqlalchemy import text
from app.db.session import engine

with engine.connect() as conn:
    r = conn.execute(text('SELECT 1')).scalar()
    print('DB_OK', r)
