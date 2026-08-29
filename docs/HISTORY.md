# Historia y decisiones

## Etapa 1: esqueleto sin downloader real

El proyecto nacio como bot personal. Se eligio Python, `python-telegram-bot`,
aiohttp, SQLite y asyncio. El nucleo de descarga se dejo intencionalmente fuera
detras de `DownloadProvider`; `MockProvider` permitio probar todo el flujo sin
depender de una fuente real.

Se implementaron `/start`, busqueda, botones de calidad, estados, tokens,
expiracion, cleanup, logs rotativos, Docker y almacenamiento temporal.

## Etapa 2: EC2 y S3

Para evitar llenar EBS con FLAC y playlists, se agrego `S3Storage`. La
arquitectura se mantuvo en una sola EC2: descarga temporal, subida a S3,
eliminacion local y entrega mediante link temporal.

La autenticacion de la aplicacion con S3 se diseno con IAM role de instancia.
Se verificaron Docker Compose, `/health`, subida, presigned URL y borrado S3.

## Etapa 3: provider custom

El placeholder evoluciono a un provider real intercambiable. Se mantuvo
`PROVIDER=mock|custom` en `.env`. El provider actual agrega busqueda, descarga
MP3/FLAC y metadata visual.

## Etapa 4: interfaz inline

La busqueda de texto tradicional se sustituyo por inline en el chat privado.
Se agregaron caratulas, texto, previews, calidades y boton de nueva busqueda. El
limite actual es 40 resultados.

## Etapa 5: playlists y matching

Se agregaron links de playlists Spotify/Deezer, historial por usuario, modos
"Solo nuevas"/"Todas de nuevo", seleccion de calidad y progreso.

Las primeras coincidencias Spotify a Deezer eran demasiado permisivas y podian
escoger remix, live, sped-up o una cancion distinta. Se implementaron ISRC,
consultas alternativas, puntuacion de artista/titulo/album/duracion y rechazo de
matches dudosos. `match_log.csv` quedo como herramienta temporal de diagnostico.

## Etapa 6: ZIP, letras y rendimiento

Las playlists se empaquetan sin comprimir audio otra vez (`ZIP_STORED`) y se
dividen por tamano. Cada audio se borra despues de agregarlo al ZIP; cada parte
se sube a S3 y se elimina localmente. Esto limita el uso de disco.

Se agregaron letras sincronizadas LRCLIB, resumen de faltantes, tamano total,
metricas de descarga/subida/ZIP y concurrencia de audio configurable.

## Checkpoint de este repositorio

Antes de crear este respaldo se comparo la copia local con el proyecto activo de
EC2. Todo el codigo coincidia; solo cambiaba el valor ilustrativo de `BASE_URL`
en `.env.example`. Se conservo la variante generica local. Antes de publicar se
retiraron dos argumentos de aspecto sensible que FreeSpotify ignoraba; el cliente
publico funciona sin credenciales de aplicacion.

## Pendientes conocidos

- La whitelist por `TELEGRAM_USER_ID` esta desactivada en la logica actual.
- El rate limiter existe pero no esta conectado.
- No hay pruebas automatizadas amplias; la validacion principal ha sido Docker,
  imports, health check y pruebas reales en Telegram.
- Para escalar a muchos usuarios harian falta cola/persistencia distribuida y
  workers separados, pero no son necesarios para el alcance actual.
