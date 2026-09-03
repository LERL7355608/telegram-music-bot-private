"""El file server local arma Content-Disposition a mano, sin sanitizar."""
from __future__ import annotations

import socket
from datetime import timedelta

import aiohttp
import pytest

from conftest import make_settings

from services.database import DownloadRepository, utc_now
from services.file_server import FileServer


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


async def _servidor_con_archivo(tmp_path, nombre_archivo: str):
    archivo = tmp_path / nombre_archivo
    archivo.write_bytes(b"ID3fake-audio-bytes")

    repo = DownloadRepository(tmp_path / "db.sqlite3")
    await repo.init()
    token = "token-de-prueba"
    await repo.create_ready_file(
        user_id=1,
        track={"id": "1", "title": "T", "artist": "A"},
        quality="mp3_320",
        file_path=archivo,
        token=token,
        expires_at=utc_now() + timedelta(hours=1),
    )

    puerto = _puerto_libre()
    server = FileServer(repo, "127.0.0.1", puerto)
    await server.start()
    return server, f"http://127.0.0.1:{puerto}/download/{token}"


async def test_descarga_nombre_ascii(tmp_path):
    server, url = await _servidor_con_archivo(tmp_path, "Song.mp3")
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                assert r.status == 200
                assert await r.read() == b"ID3fake-audio-bytes"
                assert "Song.mp3" in r.headers["Content-Disposition"]
    finally:
        await server.stop()


async def test_descarga_nombre_no_ascii(tmp_path):
    """EL BUG: los headers HTTP son latin-1. Un titulo en japones revienta.

    Deezer devuelve titulos en cualquier idioma, asi que esto no es teorico.
    """
    server, url = await _servidor_con_archivo(tmp_path, "\u5b87\u591a\u7530 - First Love.mp3")
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                assert r.status == 200, f"el servidor devolvio {r.status}"
                assert await r.read() == b"ID3fake-audio-bytes"
                cd = r.headers["Content-Disposition"]
                assert "filename*=UTF-8''" in cd, f"sin RFC5987: {cd!r}"
    finally:
        await server.stop()


@pytest.mark.parametrize(
    "sucio",
    ['co"millas.mp3', "salto\r\ninyectado.mp3", r"back\slash.mp3"],
)
def test_sanitizador_limpia_nombres_peligrosos(sucio):
    from services.storage import _content_disposition

    header = _content_disposition(sucio)
    assert "\r" not in header and "\n" not in header
    assert header.count('"') == 2, f"comillas desbalanceadas: {header!r}"
    header.encode("latin-1")


async def test_token_invalido_da_404(tmp_path):
    server, url = await _servidor_con_archivo(tmp_path, "Song.mp3")
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url.replace("token-de-prueba", "no-existe")) as r:
                assert r.status == 404
    finally:
        await server.stop()


async def test_link_expirado_da_410(tmp_path):
    archivo = tmp_path / "viejo.mp3"
    archivo.write_bytes(b"x")
    repo = DownloadRepository(tmp_path / "db2.sqlite3")
    await repo.init()
    await repo.create_ready_file(
        user_id=1,
        track={"id": "1", "title": "T", "artist": "A"},
        quality="mp3_320",
        file_path=archivo,
        token="viejo",
        expires_at=utc_now() - timedelta(hours=1),
    )
    puerto = _puerto_libre()
    server = FileServer(repo, "127.0.0.1", puerto)
    await server.start()
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"http://127.0.0.1:{puerto}/download/viejo") as r:
                assert r.status == 410
    finally:
        await server.stop()
