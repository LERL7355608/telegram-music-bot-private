# Seguridad y secretos

## Nunca subir a Git

- `.env` y variantes reales.
- Token de Telegram.
- ARL/cookies/tokens de providers.
- Client secrets OAuth.
- AWS access keys, especialmente root.
- Llaves SSH `.pem`, `.ppk` o privadas.
- SQLite, logs, descargas y ZIP.
- Nombres internos, IPs o IDs de infraestructura cuando no sean necesarios.

`.gitignore` cubre estos patrones, pero siempre ejecuta una auditoria antes de
cada publicacion importante.

## Modelo AWS

- Bucket privado, sin public access.
- IAM role asociado a EC2, con permisos minimos al prefijo del bot.
- Presigned URLs cortos generados bajo demanda.
- Lifecycle de S3 como segunda barrera de limpieza.
- SSH limitado a IPs concretas y reglas temporales retiradas al terminar.

## Telegram

Los requests de Telegram incluyen el token en la URL. Mantener `httpx` y
`httpcore` en nivel WARNING o superior evita escribirlo en logs normales.

Si un token aparece en un chat, log o commit, debe rotarse; borrarlo del archivo
no lo elimina del historial Git.

## Datos de usuarios

SQLite contiene IDs de Telegram, usernames y metadata de descargas. No se
versiona. Los backups deben almacenarse cifrados o en una ubicacion privada.

## Checklist antes de push

```bash
git status --short
git diff --cached
git grep -n -I -E "(TELEGRAM_BOT_TOKEN|DEEZER_ARL|AWS_SECRET_ACCESS_KEY|BEGIN .*PRIVATE KEY)" -- . ':!*.example'
```

Tambien revisa archivos grandes y nombres inesperados:

```bash
find . -type f -size +10M -not -path './.git/*'
```

No publiques hasta comprender cada coincidencia.
