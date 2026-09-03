from __future__ import annotations

from datetime import timedelta

from services.track_cache import TrackCache


def test_guarda_y_recupera():
    cache = TrackCache(ttl_minutes=30)
    ref = cache.add({"id": "1", "title": "T"})
    assert cache.get(ref) == {"id": "1", "title": "T"}


def test_ref_desconocida_es_none():
    assert TrackCache().get("no-existe") is None


def test_devuelve_copia_no_el_original():
    cache = TrackCache()
    ref = cache.add({"id": "1"})
    cache.get(ref)["id"] = "modificado"
    assert cache.get(ref)["id"] == "1"


def test_expira_por_ttl():
    cache = TrackCache(ttl_minutes=30)
    ref = cache.add({"id": "1"})
    viejo = cache._items[ref]
    cache._items[ref] = type(viejo)(track=viejo.track, expires_at=viejo.expires_at - timedelta(hours=2))
    assert cache.get(ref) is None


def test_evicta_al_llenarse():
    cache = TrackCache(ttl_minutes=30, max_items=3)
    refs = [cache.add({"id": str(i)}) for i in range(5)]
    assert len(cache._items) <= 3
    assert cache.get(refs[-1]) is not None


def test_refs_son_unicas():
    cache = TrackCache(max_items=500)
    refs = {cache.add({"id": str(i)}) for i in range(200)}
    assert len(refs) == 200
