from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import Settings  # noqa: E402


FAKE_TOKEN = "123456789:AAHfakefakefakefakefakefakefakefakefa"


def make_settings(tmp_path: Path, **overrides) -> Settings:
    """Settings completo apuntando a un tmp_path, sin tocar el .env real."""
    defaults = dict(
        telegram_bot_token=FAKE_TOKEN,
        telegram_user_id=None,
        download_path=tmp_path / "downloads",
        database_path=tmp_path / "storage" / "downloads.sqlite3",
        logs_path=tmp_path / "logs",
        base_url="http://localhost:8080",
        max_downloads_per_hour=10,
        file_expiry_hours=12,
        http_host="127.0.0.1",
        http_port=0,
        workers=1,
        provider_name="mock",
        playlist_audio_concurrency=2,
        zip_part_max_gb=10,
        min_free_disk_gb=1,
        storage_backend="local",
        aws_region="us-west-1",
        s3_bucket=None,
        s3_prefix="downloads",
    )
    defaults.update(overrides)
    return Settings(**defaults)


class FakeUser:
    def __init__(self, user_id: int):
        self.id = user_id
        self.username = f"user{user_id}"
        self.first_name = "Test"
        self.last_name = None


class FakeUpdate:
    """Update minimo: is_allowed solo lee effective_user."""

    def __init__(self, user_id: int | None):
        self.effective_user = FakeUser(user_id) if user_id is not None else None


@pytest.fixture
def settings(tmp_path):
    return make_settings(tmp_path)
