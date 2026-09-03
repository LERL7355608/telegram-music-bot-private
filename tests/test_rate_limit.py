"""MAX_DOWNLOADS_PER_HOUR existe en .env. Estas pruebas verifican que sirva."""
from __future__ import annotations

from conftest import make_settings

from services.rate_limit import InMemoryRateLimiter


def test_limitador_cuenta_y_corta():
    limiter = InMemoryRateLimiter(max_events=3, window_seconds=3600)
    assert [limiter.allow(7) for _ in range(3)] == [True, True, True]
    assert limiter.allow(7) is False
    assert limiter.remaining(7) == 0


def test_limitador_separa_usuarios():
    limiter = InMemoryRateLimiter(max_events=1, window_seconds=3600)
    assert limiter.allow(1) is True
    assert limiter.allow(1) is False
    assert limiter.allow(2) is True


def test_ventana_expira(monkeypatch):
    import services.rate_limit as rl

    reloj = {"t": 1000.0}
    monkeypatch.setattr(rl.time, "time", lambda: reloj["t"])

    limiter = rl.InMemoryRateLimiter(max_events=2, window_seconds=60)
    assert limiter.allow(1) is True
    assert limiter.allow(1) is True
    assert limiter.allow(1) is False

    reloj["t"] += 61
    assert limiter.allow(1) is True


def test_limitador_esta_conectado_a_la_app(tmp_path):
    """EL BUG: rate_limit.py existe pero nadie lo importa ni lo instancia."""
    from bot import build_application

    settings = make_settings(tmp_path, max_downloads_per_hour=5)
    settings.ensure_directories()
    app = build_application(settings)

    limiter = app.bot_data.get("rate_limiter")
    assert limiter is not None, "build_application no crea rate_limiter"
    assert isinstance(limiter, InMemoryRateLimiter)
    assert limiter.max_events == 5, "no usa settings.max_downloads_per_hour"


def test_consume_cobra_y_bloquea():
    from services.rate_limit import consume, limit_message

    bot_data = {"rate_limiter": InMemoryRateLimiter(max_events=2, window_seconds=3600)}
    assert consume(bot_data, 1) is True
    assert consume(bot_data, 1) is True
    assert consume(bot_data, 1) is False
    assert "2 descargas por hora" in limit_message(bot_data)


def test_consume_sin_limitador_no_estorba():
    from services.rate_limit import consume

    assert consume({}, 1) is True


def test_handlers_usan_el_guard():
    """Que el guard este importado y llamado donde se encolan descargas."""
    import inspect

    import handlers.download
    import handlers.playlist

    assert "consume(" in inspect.getsource(handlers.download._enqueue_track_download)
    assert "consume(" in inspect.getsource(handlers.playlist.enqueue_playlist_zip)
