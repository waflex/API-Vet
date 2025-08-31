# API Veterinaria

Pequeña API para gestionar mascotas (FastAPI + Postgres).

## Resumen
- Endpoints principales: `/mascotas/` (GET, POST) y `/mascotas/{id}` (GET).
- Base de datos: PostgreSQL (servicio `db` en `docker-compose.yml`).
- Código principal: `main.py`.

## Requisitos
- Docker & Docker Compose (recomendado) o Python 3.11+
- Dependencias Python en `requirements.txt`.

## Ejecutar con Docker (recomendado)
Desde la raíz del proyecto (Windows PowerShell):

```powershell
docker-compose up --build
```

La API quedará disponible en `http://localhost:8000`.

- Para iniciar en background:

```powershell
docker-compose up --build -d
```

## Ejecutar localmente sin Docker
Asegúrate de tener una base de datos Postgres accesible y exporta la variable `DATABASE_URL`:

```powershell
$env:DATABASE_URL = "postgresql://alumno:alumno123@localhost:5432/veterinaria"
uvicorn main:app --reload
```

## Variables de entorno importantes
- `DATABASE_URL` — URL de conexión a Postgres. En `docker-compose.yml` ya apunta a `db`.

## Endpoints
Todos los ejemplos usan `http://localhost:8000`.

- GET /mascotas/
  - Descripción: devuelve la lista de mascotas.
  - Respuesta (200): lista JSON de objetos `{ id, nombre, especie, edad }`.

- GET /mascotas/{id}
  - Descripción: devuelve una mascota por id.
  - Respuesta: 200 con objeto, o 404 si no existe.

- POST /mascotas/
  - Descripción: crea una mascota a partir del JSON.
  - Body JSON ejemplo:

```json
{
  "nombre": "Luna",
  "especie": "Gato",
  "edad": 1
}
```

- Respuestas: 201 (creado) / 400 (payload inválido).

## Ejemplos rápidos
Curl (crear):

```bash
curl -X POST http://localhost:8000/mascotas/ \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Luna","especie":"Gato","edad":1}'
```

Python (requests) — listar:

```python
import requests
print(requests.get('http://localhost:8000/mascotas/').json())
```

## Interfaz integrada
- `index.html` incluye documentación interactiva y botones "Try it" que llaman a la API.
- Para usar la página sin problemas de CORS, abre `http://localhost:8000/` cuando la API esté en ejecución (la app sirve el `index.html`).

## Notas y troubleshooting
- Si la API falla al arrancar con errores de conexión a Postgres, revisa `DATABASE_URL`. En Docker Compose la base de datos está en el host `db` (no `localhost`).
- Si la tabla `mascotas` no existe, el servicio intenta crearla en el arranque (hay reintentos incorporados en `main.py`).
- Logs de los contenedores:

```powershell
docker-compose logs -f api
docker-compose logs -f db
```

## Próximos pasos sugeridos
- Añadir endpoint `/healthz` para comprobación de liveness/readiness.
- Ajustar CORS para producción usando variable de entorno.
- Añadir tests con pytest + TestClient.

---
Pequeña guía creada automáticamente. Si quieres que añada el `/healthz` y los tests ahora, te lo implemento.
