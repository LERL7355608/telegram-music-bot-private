# Descubrimiento de infraestructura

Este archivo permite encontrar la infraestructura existente sin guardar IPs,
IDs de cuenta ni credenciales en Git.

## Identidad logica

- Region: `us-west-1`.
- Etiqueta EC2 `Name=telegram-music-bot`.
- Etiqueta EC2 `Project=telegram-music-bot`.
- Security group logico: `telegram-music-bot-sg`.
- IAM instance profile logico: `telegram-music-bot-instance-profile`.
- Prefijo S3 de objetos: `downloads/`.
- Directorio de aplicacion: `/opt/telegram-music-bot`.

## Encontrar la instancia

Con AWS CLI ya autenticada:

```bash
aws ec2 describe-instances \
  --region us-west-1 \
  --filters \
    Name=tag:Project,Values=telegram-music-bot \
    Name=instance-state-name,Values=pending,running,stopping,stopped \
  --query 'Reservations[].Instances[].{Id:InstanceId,State:State.Name,Type:InstanceType,Name:Tags[?Key==`Name`]|[0].Value}'
```

No copies la salida a un commit. Usa el ID solo para la sesion de trabajo.

## Encontrar configuracion vigente

Una vez conectado por SSH:

```bash
cd /opt/telegram-music-bot
docker compose ps
sudo test -f .env && echo '.env existe'
```

Para consultar nombres de variables sin revelar valores:

```bash
sudo sed -n 's/=.*$/=<redacted>/p' .env
```

El bucket real, BASE_URL y secretos deben obtenerse del `.env` de produccion o
del inventario AWS durante la restauracion, pero nunca imprimirse en un reporte
publico ni guardarse en Git.

## Estado de referencia

- EC2 `t3.small`, Ubuntu 24.04 x86_64 y 30 GB gp3.
- IMDSv2 requerido con response hop limit 2 para credenciales dentro de Docker.
- Docker Compose ejecuta un servicio `bot` y expone el puerto configurado.
- S3 usa un bucket privado y IAM role; no hay access keys en el contenedor.

## Regla de acceso SSH

Agrega temporalmente solo la IP publica actual como `/32`. Al terminar, elimina
esa regla concreta. No abras SSH a `0.0.0.0/0`.

## Comparar EC2 con Git

Antes de desplegar cambios:

1. Descarga a un directorio temporal solo codigo y configuracion de ejemplo.
2. Excluye `.env`, SQLite, logs, descargas y backups de WinSCP.
3. Compara hashes o usa `git diff --no-index`.
4. Decide de forma explicita cual copia es autoritativa.
5. No sobrescribas produccion por asumir que local es mas reciente.
