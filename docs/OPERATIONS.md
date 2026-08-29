# Operacion y diagnostico

## Comandos habituales

```bash
cd /opt/telegram-music-bot
docker compose ps
docker compose logs --tail=200 bot
docker compose logs -f bot
docker compose restart bot
docker compose up -d --build
docker compose down
```

`docker compose down` no elimina el volumen de descargas salvo que se agregue
`-v`. No uses `-v` durante mantenimiento normal.

## Health check

```bash
curl -fsS http://127.0.0.1:8080/health
```

Respuesta esperada: `{"ok": true}`.

## Validacion del provider

```bash
docker compose run --rm --no-deps bot python -m py_compile providers/custom.py
docker compose run --rm --no-deps bot python -c "from providers.custom import CustomProvider; print('Provider OK')"
```

El import no inicia sesion porque el provider usa inicializacion diferida. Una
prueba real requiere el secreto configurado en `.env`.

## Flujo de prueba despues de desplegar

1. `/start` en chat privado.
2. Buscar una cancion por inline y comprobar caratula/texto.
3. Elegir preview y descargar MP3.
4. Descargar FLAC y abrir el enlace.
5. Pegar un link de track de Spotify y uno de Deezer.
6. Pegar una playlist pequena.
7. Probar `Solo nuevas`, `Todas de nuevo`, con y sin letras.
8. Reiniciar el contenedor y comprobar que el historial persiste.
9. Confirmar que el objeto S3 y SQLite expiran segun lo configurado.

## Copia de seguridad de SQLite

Deten escrituras o usa la API de backup de SQLite. Una opcion conservadora:

```bash
cd /opt/telegram-music-bot
docker compose stop bot
cp storage/downloads.sqlite3 storage/downloads.sqlite3.backup
docker compose start bot
```

Guarda el backup fuera de Git y protegelo porque contiene IDs de usuarios y
metadatos de descargas.

## Limpiar expirados

El servicio corre automaticamente cada hora. Para una pasada manual:

```bash
docker compose run --rm bot python -m services.cleanup
```

No vacies el bucket ni borres SQLite como parte de una limpieza normal.

## Logs y privacidad

- Los logs rotan bajo `logs/`.
- No aumentes `httpx`/`httpcore` a DEBUG: las URLs de Telegram pueden contener
  el token del bot.
- No pegues `.env` completo en tickets, chats o reportes.
- `MATCH_LOG_ENABLED=true` agrega un CSV de matching al ZIP; usalo solo para
  diagnostico puntual.

## Fallos frecuentes

- `Missing TELEGRAM_BOT_TOKEN`: `.env` ausente o incompleto.
- `DEEZER_ARL no esta configurado`: provider custom sin su secreto.
- `ARL no valido o expiro`: renueva el secreto y reconstruye/reinicia.
- `Unable to locate credentials`: el contenedor no recibe el IAM role; revisa
  instance profile e IMDSv2 hop limit.
- Link S3 expirado: el boton contiene un enlace temporal; genera uno nuevo desde
  el endpoint/token mientras el objeto siga vigente.
- Playlist con canciones incorrectas: revisa `match_log.csv` y los umbrales del
  provider antes de relajar matching.
- Disco bajo: reduce concurrencia/tamano de parte, limpia expirados o aumenta
  EBS; el bot exige `MIN_FREE_DISK_GB` antes de procesar playlists.
