from __future__ import annotations

from datetime import timedelta

from services.database import DownloadRepository, decode_dt, encode_dt, utc_now


def test_fecha_ida_y_vuelta():
    ahora = utc_now().replace(microsecond=0)
    assert decode_dt(encode_dt(ahora)) == ahora


def test_fecha_nula():
    assert encode_dt(None) is None
    assert decode_dt(None) is None
    assert decode_dt("") is None


async def test_ciclo_de_descarga(tmp_path):
    repo = DownloadRepository(tmp_path / "db.sqlite3")
    await repo.init()

    did = await repo.create_pending(
        user_id=42, track={"id": "abc", "title": "T", "artist": "A"}, quality="flac"
    )
    assert did > 0

    expira = utc_now() + timedelta(hours=1)
    await repo.set_ready(did, file_path="/tmp/x.flac", token="tok", expires_at=expira)

    fila = await repo.get_by_token("tok")
    assert fila is not None
    assert fila["status"] == "ready"
    assert fila["user_id"] == 42

    await repo.mark_expired(did)
    assert (await repo.get_by_token("tok"))["status"] == "expired"


async def test_expirados_se_listan(tmp_path):
    repo = DownloadRepository(tmp_path / "db.sqlite3")
    await repo.init()
    await repo.create_ready_file(
        user_id=1, track={"id": "1"}, quality="flac",
        file_path="/tmp/a", token="viejo", expires_at=utc_now() - timedelta(hours=2),
    )
    await repo.create_ready_file(
        user_id=1, track={"id": "2"}, quality="flac",
        file_path="/tmp/b", token="nuevo", expires_at=utc_now() + timedelta(hours=2),
    )
    expirados = await repo.get_expired_ready()
    assert [f["token"] for f in expirados] == ["viejo"]


async def test_init_es_idempotente(tmp_path):
    """init() corre la migracion de playlist_downloads cada arranque."""
    repo = DownloadRepository(tmp_path / "db.sqlite3")
    for _ in range(3):
        await repo.init()
    await repo.create_playlist_download(
        user_id=1, playlist_id="p1", playlist_title="P",
        track_id="t1", quality="flac", download_id=1,
    )
    ids = await repo.get_known_playlist_track_ids(user_id=1, playlist_id="p1", quality="flac")
    assert ids == {"t1"}
