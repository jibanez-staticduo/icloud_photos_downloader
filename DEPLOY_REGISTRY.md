# Despliegue por Registry

Este fork puede publicarse en tu registry privado y luego desplegarse desde el stack
`/volume2/docker/icloudpd` sin depender de un `Dockerfile` local en el stack.

## Imagen usada

- Registry: `docker.staticduo.com`
- Repositorio: `docker.staticduo.com/icloudpd`
- Arquitectura actual: `amd64`
- Tag por defecto para despliegue: `latest`

## Publicar imagen desde este repo

Desde `/home/staticduo/git/icloud_photos_downloader`:

```bash
REGISTRY_USER=... REGISTRY_PASSWORD=... ./release-image.sh
```

El script publica estas tags:

- `docker.staticduo.com/icloudpd:latest`
- `docker.staticduo.com/icloudpd:sha-<commit>`
- `docker.staticduo.com/icloudpd:branch-<rama>`

Notas:

- Usa `Dockerfile.local`, o sea, construye desde el checkout local actual.
- Por ahora publica solo `linux/amd64`.
- Si ya tienes sesión iniciada en Docker contra el registry, no hace falta pasar credenciales.

## Desplegar en el stack icloudpd

El stack `/volume2/docker/icloudpd` queda configurado para tirar de imagen remota.

Actualizar imagen y levantar contenedor:

```bash
docker compose -f /volume2/docker/icloudpd/docker-compose.yaml pull icloudpd
docker compose -f /volume2/docker/icloudpd/docker-compose.yaml up -d icloudpd
```

## Cambiar de tag

En `/volume2/docker/icloudpd/.env` puedes fijar otra tag:

```env
ICLOUDPD_IMAGE=docker.staticduo.com/icloudpd:latest
```

Ejemplos útiles:

```env
ICLOUDPD_IMAGE=docker.staticduo.com/icloudpd:branch-refactor
ICLOUDPD_IMAGE=docker.staticduo.com/icloudpd:sha-8aca9ee
```

## Flujo recomendado

1. Trabajar en `/home/staticduo/git/icloud_photos_downloader`
2. Commit y push de la rama
3. Publicar imagen con `./release-image.sh`
4. Ajustar `ICLOUDPD_IMAGE` si quieres una tag concreta
5. `docker compose pull && docker compose up -d`

## Futuro

Si luego quieres ejecutar la misma imagen en otra máquina, solo necesita:

- acceso a `docker.staticduo.com`
- login al registry si es privado
- un compose apuntando a `docker.staticduo.com/icloudpd:<tag>`
