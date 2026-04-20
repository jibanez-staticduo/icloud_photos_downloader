"""Sync policy for incremental vs full synchronization.

This encapsulates the logic for:
- Determining if incremental sync should be used
- Applying addedDate filters to albums
- Tracking photos processed during sync
- Saving last sync date
"""

import datetime
from typing import Any

from icloudpd.file_cache import FileCache
from icloudpd.extensions.contracts import SyncPolicy


class IncrementalSyncPolicy(SyncPolicy):
    """Policy that enables incremental sync based on last sync date."""

    def __init__(self) -> None:
        self._incremental_active = False
        self._max_added_date_seen: float | None = None

    def prepare_albums(
        self, albums: Any, file_cache: FileCache | None, status_exchange: Any, logger: Any
    ) -> bool:
        """
        Prepare albums for sync by applying incremental filters if appropriate.
        
        Returns:
            True if incremental sync is active (filter applied)
        """
        if file_cache is None or status_exchange.get_force_full_sync():
            logger.info("🔄 FULL SYNC: No cache or forced full sync, processing all photos")
            return False

        last_sync_timestamp = file_cache.get_last_sync_date()
        if not last_sync_timestamp:
            logger.info("🔄 FULL SYNC: No previous sync date found, processing all photos")
            return False

        # Subtract 1 day margin for timing differences
        margin_seconds = 86400  # 1 day
        last_sync_with_margin = last_sync_timestamp - margin_seconds

        # Convert to milliseconds (what iCloud uses)
        added_date_ms = int(last_sync_with_margin * 1000)

        # Create filter
        added_date_filter = {
            "fieldName": "addedDate",
            "fieldValue": {"type": "INT64", "value": added_date_ms},
            "comparator": "GREATER_THAN_OR_EQUALS",
        }

        # Apply filter to all albums
        for photo_album in albums:
            if photo_album.query_filter is None:
                photo_album.query_filter = [added_date_filter]
            else:
                photo_album.query_filter = list(photo_album.query_filter) + [added_date_filter]

        last_sync_readable = datetime.datetime.fromtimestamp(last_sync_timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        margin_readable = datetime.datetime.fromtimestamp(last_sync_with_margin).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        logger.info(
            f"🔄 INCREMENTAL SYNC: Filtering photos added since {margin_readable} "
            f"(last sync: {last_sync_readable}, 1 day margin)"
        )

        self._incremental_active = True
        return True

    def on_item_seen(self, item: Any) -> None:
        """Called when a photo item is processed. Track max addedDate seen."""
        try:
            item_added_ts = item.added_date.timestamp()
            if self._max_added_date_seen is None or item_added_ts > self._max_added_date_seen:
                self._max_added_date_seen = item_added_ts
        except Exception:
            # addedDate should be present, but don't let this break downloads
            pass

    def finalize(
        self, file_cache: FileCache | None, status_exchange: Any, user_config: Any, logger: Any
    ) -> None:
        """Save last sync date if sync completed successfully."""
        if file_cache is None:
            return

        # Only save if:
        # - Not cancelled
        # - Not using --recent or --until-found limits
        progress = status_exchange.get_progress()
        if progress.cancel or user_config.recent is not None or user_config.until_found is not None:
            return

        if self._max_added_date_seen is not None:
            file_cache.set_last_sync_date(self._max_added_date_seen)
            logger.info(
                "Saved last sync date (iCloud addedDate): %s "
                "(next sync will only process new photos)",
                datetime.datetime.fromtimestamp(self._max_added_date_seen).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            )
        else:
            logger.debug("No photos were listed in this run; keeping previous last sync date unchanged.")

    @property
    def incremental_active(self) -> bool:
        """Check if incremental sync is currently active."""
        return self._incremental_active
