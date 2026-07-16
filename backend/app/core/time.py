from datetime import datetime, timezone


def utcnow() -> datetime:
    """Текущее время UTC без tzinfo (совместимо с SQLite и naive-колонками БД)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
