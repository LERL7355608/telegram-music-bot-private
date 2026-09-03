"""El bot dice ser 'private'. Estas pruebas verifican que de verdad lo sea."""
from __future__ import annotations

from conftest import FakeUpdate, make_settings

from handlers.search import is_allowed


DUENO = 111111111
EXTRANO = 999999999


def test_dueno_pasa(tmp_path):
    settings = make_settings(tmp_path, telegram_user_id=DUENO)
    assert is_allowed(FakeUpdate(DUENO), settings) is True


def test_extrano_NO_pasa(tmp_path):
    """EL BUG: hoy is_allowed ignora settings y deja pasar a cualquiera."""
    settings = make_settings(tmp_path, telegram_user_id=DUENO)
    assert is_allowed(FakeUpdate(EXTRANO), settings) is False


def test_sin_usuario_no_pasa(tmp_path):
    settings = make_settings(tmp_path, telegram_user_id=DUENO)
    assert is_allowed(FakeUpdate(None), settings) is False


def test_sin_user_id_configurado_es_abierto(tmp_path):
    """Si TELEGRAM_USER_ID esta vacio, el bot es abierto a proposito."""
    settings = make_settings(tmp_path, telegram_user_id=None)
    assert is_allowed(FakeUpdate(EXTRANO), settings) is True
