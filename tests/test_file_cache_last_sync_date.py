import logging
import os

from icloudpd.file_cache import FileCache


def test_file_cache_last_sync_date_roundtrip(tmp_path) -> None:
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    cache_db_path = os.fspath(cache_dir / "file_cache.db")
    fc = FileCache(cache_db_path, logger=logging.getLogger("test"))

    ts = 1736380800.0  # 2025-01-09 00:00:00 UTC
    fc.set_last_sync_date(ts)

    assert fc.get_last_sync_date() == ts

    last_sync_file = cache_dir / ".last_sync_date"
    assert last_sync_file.exists()
    assert last_sync_file.read_text().strip() == str(ts)

