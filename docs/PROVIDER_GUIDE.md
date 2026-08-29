# Guia de providers

## Seleccion

`config.py` carga:

```python
os.getenv("PROVIDER", "mock")
```

`providers/__init__.py` registra las implementaciones. Para cambiar de provider:

1. Agrega una clase que herede de `DownloadProvider`.
2. Registrala en `build_provider()`.
3. Agrega sus dependencias a `requirements.txt`.
4. Agrega solo nombres/vacios a `.env.example`.
5. Configura secretos en el `.env` del servidor.
6. Cambia `PROVIDER=nombre` y reconstruye Docker.

## Contrato obligatorio

```python
async def search(self, query: str) -> list[dict]

async def download(
    self,
    track_id: str,
    quality: str,
    output_dir: Path,
) -> Path
```

Calidades que envian los handlers:

- `mp3_320`
- `flac`

`download()` debe escribir dentro de `output_dir` y devolver el `Path` final.

## Formato de busqueda

```python
{
    "id": "id_descargable",
    "title": "Titulo",
    "artist": "Artista",
    "album": "Album",
    "duration": "3:42",
    "cover_url": "https://...",
    "preview_url": "https://..."
}
```

`cover_url` y `preview_url` son opcionales. Los demas campos deben existir,
aunque alguno sea una cadena vacia.

## Contratos opcionales usados por esta aplicacion

```python
async def resolve_track(self, url: str) -> dict
async def resolve_playlist(self, url: str) -> dict
```

Playlist esperada:

```python
{
    "id": "source_playlist_id",
    "source": "spotify|deezer|otro",
    "title": "Nombre",
    "track_count": 100,
    "resolved_count": 97,
    "skipped_count": 3,
    "skipped_tracks": ["Artista - Cancion"],
    "tracks": [
        {
            "id": "id_descargable",
            "title": "Titulo",
            "artist": "Artista",
            "album": "Album",
            "duration": "3:42",
            "cover_url": "https://..."
        }
    ]
}
```

Los IDs de `tracks` deben ser aceptados directamente por `download()`.

## Reglas de integracion

- Usa `asyncio.to_thread()` o executor para SDKs bloqueantes.
- No compartas una sesion no thread-safe entre descargas concurrentes; usa pool,
  lock o una instancia por worker.
- No cambies handlers para adaptarlos a una fuente especifica.
- Conserva nombres y metadata del archivo final.
- Informa excepciones claras y no devuelvas un archivo parcial.
- Si un track de playlist no tiene match confiable, omitelo y reportalo; no
  descargues "el primer resultado".
- El provider no debe subir a S3: esa responsabilidad pertenece a Storage.

## Provider actual

`CustomProvider` usa:

- `DEEZER_ARL` con inicializacion diferida.
- deemix calidad `9` para FLAC y `3` para MP3 320.
- pool de sesiones para concurrencia segura.
- Spotify publico mediante spotdl.
- ISRC y scoring estricto para Spotify a Deezer.

El provider puede sustituirse sin cambiar queue, storage, SQLite ni UI siempre
que mantenga estos contratos.
