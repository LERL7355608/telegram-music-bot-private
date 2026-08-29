# Contexto para otra IA

## Objetivo

Restaurar y operar un bot de Telegram que busca musica, recibe links de canciones
o playlists, descarga mediante un Provider intercambiable y entrega archivos
temporales desde S3 o almacenamiento local.

No redisenes la arquitectura durante una restauracion. Primero reproduce el
estado documentado, valida el flujo con `MockProvider` y despues activa el
provider real.

## Orden de trabajo obligatorio

1. Lee este archivo y el resto de `docs/`.
2. Inspecciona `git status`, la rama y el ultimo commit.
3. Comprueba que no haya secretos dentro del repositorio.
4. Identifica el destino: EC2 existente o instancia nueva.
5. Crea el `.env` manualmente a partir de `.env.example`.
6. Valida primero con `PROVIDER=mock` y `STORAGE_BACKEND=local`.
7. Configura IAM/S3 y valida el almacenamiento.
8. Cambia a `PROVIDER=custom`, agrega el secreto requerido y reconstruye.
9. Ejecuta `scripts/verify.sh`, revisa `/health` y prueba el chat real.
10. No declares terminada la restauracion hasta probar busqueda, calidad,
    descarga, link temporal, playlist, ZIP y limpieza.

## Decisiones que deben conservarse

- El bot y los handlers no deben depender de Deezer, Spotify ni deemix.
- Toda fuente de descarga vive detras de `DownloadProvider`.
- Una sola EC2, Docker Compose, SQLite y asyncio son suficientes para el uso
  actual; Redis/Celery no forman parte de esta version.
- Los archivos se procesan temporalmente en EC2, se suben a S3 y se borran del
  disco local.
- S3 permanece privado y se accede con IAM role de la instancia.
- Los links del usuario pasan por `/download/{token}`; el servidor genera el
  presigned URL al momento de la descarga.
- Las playlists grandes se dividen en ZIP de hasta `ZIP_PART_MAX_GB`.
- El historial es por `user_id`, `playlist_id`, `track_id` y calidad.
- Las letras `.lrc` son best effort: una letra faltante no debe fallar el audio.
- Los tracks de Spotify solo se aceptan cuando el match con Deezer es confiable.

## Estado funcional actual

- `PROVIDER` se lee desde `.env`; por defecto es `mock`.
- `custom` implementa `search`, `download`, `resolve_track` y
  `resolve_playlist`.
- Spotify publico se resuelve mediante el cliente gratuito incluido en spotdl;
  las variables antiguas `SPOTIFY_CLIENT_ID` y `SPOTIFY_CLIENT_SECRET` no se
  usan en esta version.
- La busqueda inline devuelve hasta 40 resultados.
- La concurrencia de audio de playlists es 2 por defecto y el provider limita
  su pool a un maximo de 4.
- Los links y objetos expiran en 12 horas por defecto.
- Solo se permite el chat privado, pero no hay whitelist efectiva actualmente.
- `MAX_DOWNLOADS_PER_HOUR` y `services/rate_limit.py` existen, pero el limiter
  no esta conectado al flujo actual.

## Criterio de restauracion completa

La restauracion esta completa cuando:

- `docker compose ps` muestra el bot activo.
- `/health` responde `{"ok": true}`.
- `/start` muestra Cancion/Playlist en chat privado.
- La busqueda inline muestra texto y caratulas.
- Una descarga MP3 y una FLAC terminan con boton funcional.
- Un link de Spotify o Deezer se resuelve correctamente.
- Una playlist genera ZIP, progreso y resumen de faltantes.
- SQLite conserva el historial despues de reiniciar el contenedor.
- S3 recibe el objeto mediante IAM role y cleanup elimina uno expirado.

## Lo que nunca debes hacer

- No subir `.env`, ARL, tokens, llaves SSH o access keys.
- No reemplazar el Provider por logica dentro de los handlers.
- No borrar SQLite o S3 durante una restauracion sin autorizacion explicita.
- No asumir que compilar equivale a que el flujo de Telegram funciona.
- No imprimir URLs de la API de Telegram que contengan el token.
