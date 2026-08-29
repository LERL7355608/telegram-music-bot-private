# Arquitectura

## Flujo general

```text
Usuario en Telegram
  -> handlers (start, inline, callbacks, playlist)
  -> DownloadProvider
  -> asyncio queue o job de playlist
  -> descarga temporal en /tmp/downloads
  -> LocalStorage o S3Storage
  -> SQLite actualiza estado y expiracion
  -> boton /download/{token}
  -> aiohttp valida token y genera enlace S3 temporal
  -> cleanup elimina archivo/objeto expirado
```

## Componentes

### Entrada Telegram

- `bot.py`: ensambla dependencias, registra handlers y controla inicio/cierre.
- `handlers/search.py`: `/start`, menu y restriccion a chat privado.
- `handlers/inline.py`: busqueda inline, caratulas, previews y calidades.
- `handlers/callbacks.py`: enruta acciones de botones.
- `handlers/download.py`: encola descargas individuales.
- `handlers/playlist.py`: resuelve playlists, historial, progreso, letras y ZIP.

### Provider

- `providers/base.py`: contrato estable.
- `providers/mock.py`: prueba integral sin fuente real.
- `providers/custom.py`: implementacion actual basada en Deezer/deemix y
  resolucion Spotify a Deezer.
- `providers/__init__.py`: loader de `PROVIDER`.

### Servicios

- `services/queue.py`: workers asyncio para descargas individuales.
- `services/database.py`: SQLite, usuarios, descargas e historial de playlists.
- `services/storage.py`: backend local o S3.
- `services/file_server.py`: aiohttp, `/health` y `/download/{token}`.
- `services/cleanup.py`: eliminacion periodica de expirados.
- `services/lyrics.py`: busqueda LRCLIB de letras sincronizadas.
- `services/track_cache.py`: referencias cortas para callbacks de Telegram.
- `services/rate_limit.py`: componente disponible, actualmente no conectado.

## Estados de descarga

```text
pending -> downloading -> ready -> expired
                      \-> error
```

## Persistencia

Docker monta:

- `./storage:/app/storage` para SQLite.
- `./logs:/app/logs` para logs.
- volumen `downloads:/tmp/downloads` para procesamiento temporal.

Los archivos finales viven en S3 cuando `STORAGE_BACKEND=s3`. SQLite guarda el
URI `s3://...`, el token, metadata y expiracion.

## Concurrencia

- `WORKERS`: descargas individuales simultaneas, default 2.
- `PLAYLIST_AUDIO_CONCURRENCY`: audios simultaneos dentro de una playlist,
  default 2.
- El provider crea un pool independiente de sesiones Deezer con el mismo tamano,
  limitado entre 1 y 4.
- Solo un job ZIP de playlist se ejecuta a la vez en esta version.
- Letras de playlist: concurrencia interna 4.

## Matching Spotify a Deezer

1. Lee metadata publica de Spotify.
2. Intenta coincidencia por ISRC.
3. Si no existe, consulta varias combinaciones de artista, titulo y album.
4. Puntua artista, titulo, duracion, album y variantes como remix/live/sped-up.
5. Rechaza matches con puntuacion insuficiente y los informa como faltantes.

El ID entregado al downloader siempre es un ID descargable del provider, no el
ID original de Spotify.
