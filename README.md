# Telegram Music Bot

Bot de Telegram con arquitectura Provider para buscar canciones, resolver links y
procesar playlists. Corre en una sola instancia EC2 con Docker Compose, SQLite y
almacenamiento S3 o local.

Este repositorio contiene el codigo y la documentacion necesaria para reconstruir
el proyecto. No contiene credenciales, archivos descargados ni la base de datos de
produccion.

## Estado actual

- Bot por polling con `python-telegram-bot`.
- Solo responde en el chat privado del bot.
- Busqueda inline con hasta 40 resultados, caratulas y preview cuando existe.
- Provider seleccionable por `.env`: `mock` o `custom`.
- Descarga individual MP3 320 kbps o FLAC.
- Links de tracks y playlists de Spotify y Deezer.
- Matching Spotify a Deezer por ISRC y puntuacion de metadata.
- Playlists en ZIP, modo "Solo nuevas" o "Todas de nuevo".
- Letras sincronizadas `.lrc` mediante LRCLIB, en modo best effort.
- ZIP divididos por tamano, 10 GB por defecto.
- SQLite para usuarios, estados e historial por usuario/playlist/calidad.
- S3 privado con enlaces temporales y eliminacion automatica.
- Logs rotativos y metricas de tiempos para playlists.

## Lectura obligatoria para restaurar

1. [Contexto para otra IA](docs/AI_HANDOFF.md)
2. [Arquitectura](docs/ARCHITECTURE.md)
3. [Despliegue en EC2](docs/DEPLOYMENT.md)
4. [Descubrimiento de infraestructura](docs/INFRASTRUCTURE.md)
5. [Operacion y diagnostico](docs/OPERATIONS.md)
6. [Contrato de providers](docs/PROVIDER_GUIDE.md)
7. [Historia del proyecto](docs/HISTORY.md)
8. [Seguridad y secretos](docs/SECURITY.md)

## Inicio rapido local

```bash
cp .env.example .env
# Configura TELEGRAM_BOT_TOKEN y deja PROVIDER=mock para la primera prueba.
docker compose up -d --build
docker compose logs -f bot
```

Health check:

```bash
curl http://127.0.0.1:8080/health
```

Debe responder:

```json
{"ok": true}
```

## Configuracion principal

La configuracion se carga en `config.py` desde `.env`. El provider no esta
hardcodeado:

```env
PROVIDER=mock
# o
PROVIDER=custom
```

Para `custom` se necesita `DEEZER_ARL` en el `.env` del servidor. Nunca se debe
guardar ese valor en Git.

Para S3:

```env
STORAGE_BACKEND=s3
AWS_REGION=us-west-1
S3_BUCKET=nombre-del-bucket
S3_PREFIX=downloads
```

En EC2, S3 se autentica mediante un IAM role de instancia. No agregues access
keys de AWS al `.env`.

## Verificacion

```bash
bash scripts/verify.sh
```

El script valida Docker Compose, compila los modulos Python e importa ambos
providers sin iniciar una descarga.

## Datos que no estan en Git

- `.env` y todos los tokens.
- Llaves `.pem`/`.ppk`.
- SQLite de produccion.
- Logs y archivos descargados.
- Objetos de S3.
- Cookies o tokens de providers.

Consulta `docs/SECURITY.md` antes de publicar cambios.
