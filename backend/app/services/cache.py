import json
from datetime import datetime, timedelta, timezone


def get_cached(db, cache_key):
    row = db.execute(
        "SELECT cache_data, expires_at FROM api_cache WHERE cache_key = %s",
        (cache_key,)
    ).fetchone()

    if not row:
        return None

    expires_at = row["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expires_at:
        db.execute("DELETE FROM api_cache WHERE cache_key = %s", (cache_key,))
        db.commit()
        return None

    cache_data = row["cache_data"]
    if isinstance(cache_data, str):
        return json.loads(cache_data)
    return cache_data


def set_cached(db, cache_key, data, minutes=15):
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
    cache_data = json.dumps(data)

    db.execute("""
        INSERT INTO api_cache (cache_key, cache_data, expires_at)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            cache_data = VALUES(cache_data),
            cached_at = CURRENT_TIMESTAMP,
            expires_at = VALUES(expires_at)
    """, (cache_key, cache_data, expires_at))
    db.commit()
