import json
from datetime import datetime, timedelta, timezone


def get_cached(db, cache_key):
    row = db.execute(
        "SELECT cache_data, expires_at FROM api_cache WHERE cache_key = ?",
        (cache_key,)
    ).fetchone()

    if not row:
        return None

    expires_at = datetime.fromisoformat(row["expires_at"]).replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expires_at:
        db.execute("DELETE FROM api_cache WHERE cache_key = ?", (cache_key,))
        db.commit()
        return None

    return json.loads(row["cache_data"])


def set_cached(db, cache_key, data, minutes=15):
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()
    cache_data = json.dumps(data)

    db.execute("""
        INSERT INTO api_cache (cache_key, cache_data, expires_at)
        VALUES (?, ?, ?)
        ON CONFLICT(cache_key) DO UPDATE SET
            cache_data = excluded.cache_data,
            cached_at = CURRENT_TIMESTAMP,
            expires_at = excluded.expires_at
    """, (cache_key, cache_data, expires_at))
    db.commit()
