# Despliegue en EC2

## Plataforma de referencia

- Region AWS: `us-west-1`.
- Ubuntu 24.04 x86_64.
- Instancia de referencia: `t3.small`.
- Volumen de referencia: 30 GB gp3.
- Proyecto remoto: `/opt/telegram-music-bot`.
- Docker Engine y Docker Compose plugin.
- Bucket S3 privado con prefijo `downloads/`.
- IAM role de instancia limitado al bucket/prefijo del proyecto.

No guardes IDs de cuenta, IPs, nombres reales de buckets ni llaves en este
repositorio. Descubre esos valores desde AWS durante la restauracion.

## Nueva instancia

1. Crea Ubuntu 24.04 x86_64 con al menos 30 GB gp3.
2. Asocia un security group con SSH limitado a tu IP.
3. Expone el puerto HTTP elegido solo si no hay proxy HTTPS delante.
4. Crea/asocia un IAM instance profile con permisos minimos sobre el bucket.
5. Si los contenedores no reciben credenciales del IAM role, configura IMDSv2
   con hop limit 2 en la instancia.
6. Instala Docker:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu
```

7. Clona el repositorio privado:

```bash
sudo mkdir -p /opt/telegram-music-bot
sudo chown ubuntu:ubuntu /opt/telegram-music-bot
git clone URL_PRIVADA /opt/telegram-music-bot
cd /opt/telegram-music-bot
```

8. Crea `.env` desde `.env.example` y completa los valores secretos en el
   servidor, nunca mediante un commit.
9. Valida con MockProvider:

```bash
docker compose build
docker compose run --rm --no-deps bot python -m py_compile bot.py config.py providers/base.py providers/mock.py
docker compose up -d
curl http://127.0.0.1:8080/health
```

10. Configura S3, prueba subida/lectura/eliminacion y despues cambia a
    `PROVIDER=custom`.
11. Reconstruye y revisa logs:

```bash
docker compose up -d --build
docker compose logs --tail=200 bot
```

## Variables recomendadas en produccion

```env
DOWNLOAD_PATH=/tmp/downloads
DATABASE_PATH=storage/downloads.sqlite3
LOGS_PATH=logs
HTTP_HOST=0.0.0.0
HTTP_PORT=8080
FILE_EXPIRY_HOURS=12
WORKERS=2
PLAYLIST_AUDIO_CONCURRENCY=2
ZIP_PART_MAX_GB=10
MIN_FREE_DISK_GB=5
PROVIDER=custom
STORAGE_BACKEND=s3
AWS_REGION=us-west-1
S3_PREFIX=downloads
MATCH_LOG_ENABLED=false
```

Completa de forma segura `TELEGRAM_BOT_TOKEN`, `BASE_URL`, `S3_BUCKET` y los
secretos que requiera el provider.

## IAM minimo conceptual

El role necesita acceso solo al bucket/prefijo del bot para:

- `s3:PutObject`
- `s3:GetObject`
- `s3:DeleteObject`
- listar el prefijo cuando una operacion de mantenimiento lo requiera

No uses credenciales root ni access keys permanentes dentro del contenedor.

## Actualizacion posterior

```bash
cd /opt/telegram-music-bot
git pull --ff-only
docker compose up -d --build
docker compose logs --tail=200 bot
```

Haz respaldo de SQLite antes de una actualizacion que cambie su esquema.
