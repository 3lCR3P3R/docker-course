# Despliegue con Docker y GitHub Actions

**Aprendiz:** Matthew Florez

**Curso:** Despliegue de aplicaciones y servicios en contenedores Docker - SENA

## Lo desarrollado

Despliegue de la API proporcionada por el instructor con Docker, PostgreSQL y Nginx. La API se construye con un Dockerfile de dos etapas y se ejecuta con un usuario sin privilegios. Compose coordina los tres servicios, conserva los datos de PostgreSQL en un volumen y publica únicamente el puerto del proxy.

Se configuró [Build and Test](.github/workflows/build-and-test.yml) para construir la imagen, levantar los servicios y verificar conexión, aislamiento y persistencia. El flujo se ejecuta con cambios en `main` o `master`, solicitudes de cambio y ejecución manual. Esta entrega valida y construye; la publicación en Docker Hub queda para una ampliación posterior.

## GitHub Actions

El flujo está definido en `.github/workflows/build-and-test.yml`. Sus ejecuciones se consultan en [Actions del repositorio](https://github.com/3lCR3P3R/docker-course/actions).

## Ejecutar localmente

Requisitos: Docker Engine con `docker compose` y Python 3 para las pruebas.

```bash
git clone https://github.com/3lCR3P3R/docker-course.git
cd docker-course
cp .env.example .env
docker compose up -d --build --wait --wait-timeout 120
curl http://localhost:8080/health
curl http://localhost:8080/db
```

`/health` devuelve `{"status":"ok"}` y `/db` debe indicar `"db":"conectada"`. La documentación de la API está en `http://localhost:8080/docs`.

`.env.example` contiene una contraseña ficticia para el laboratorio. `.env` queda excluido de Git. Si 8080 está ocupado, cambie `PROXY_PORT` en `.env`.

## Verificación

```bash
python3 scripts/validar.py
python3 scripts/validar.py --persistencia
```

La segunda prueba crea una tabla con un registro, recrea los contenedores y comprueba que el registro se conserva; después elimina solo su tabla de prueba. Interrumpe temporalmente este proyecto. Las pruebas se ejecutaron localmente; la evidencia de GitHub se consulta en la pestaña Actions una vez publicado el repositorio.

Para detener los servicios conservando los datos: `docker compose down`.
