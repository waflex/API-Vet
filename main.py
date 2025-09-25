from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import databases
import sqlalchemy
import os

# Get DATABASE_URL from environment variable with fallback for local development
DATABASE_URL = os.getenv(
    "DATABASE_URL","postgresql://alumno:alumno123@localhost:3322/veterinaria"
)

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Definir tabla
mascotas = sqlalchemy.Table(
    "mascotas",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("nombre", sqlalchemy.String),
    sqlalchemy.Column("especie", sqlalchemy.String),
    sqlalchemy.Column("edad", sqlalchemy.Integer),
)

engine = sqlalchemy.create_engine(DATABASE_URL)
# Do not call create_all at import time: Postgres container may not be ready yet.
# We'll create tables on startup after the DB is reachable.

app = FastAPI()

# Development CORS — allow all origins so the local `index.html` can call the API while
# developing. For production restrict this to specific origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the local index.html so the interactive documentation works from the same origin."""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except Exception:
        return HTMLResponse("<html><body><h1>API Veterinaria</h1><p>Index no encontrado.</p></body></html>")


@app.get("/healthz")
async def healthz():
    """Liveness/readiness probe.

    By default this returns {"status":"ok"} without checking the DB to keep fast and
    not require Postgres for simple liveness checks. Set environment variable
    `HEALTH_DB=1` to enable a database connectivity check (returns 503 on failure).
    """
    check_db = os.getenv("HEALTH_DB")
    if not check_db:
        return {"status": "ok"}

    # Optional DB check path
    try:
        row = await database.fetch_one(query="SELECT 1")
        if row is None:
            return ("DB not ready", 503)
        return {"status": "ok", "db": "ok"}
    except Exception:
        return ("DB connection failed", 503)

class Mascota(BaseModel):
    id: int | None = None
    nombre: str
    especie: str
    edad: int

@app.on_event("startup")
async def startup():
    # First, connect the async database client (this will retry internally if needed)
    await database.connect()

    # Ensure the synchronous engine can create tables — retry until Postgres is accepting
    import asyncio
    max_retries = 10
    for attempt in range(1, max_retries + 1):
        try:
            metadata.create_all(engine)
            break
        except Exception as exc:  # pragma: no cover - runtime retry handling
            if attempt == max_retries:
                # If we exhaust retries, re-raise so the container exits and logs the error.
                raise
            await asyncio.sleep(1)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/mascotas/", response_model=Mascota)
async def crear_mascota(mascota: Mascota):
    query = mascotas.insert().values(nombre=mascota.nombre, especie=mascota.especie, edad=mascota.edad)
    last_record_id = await database.execute(query)
    mascota.id = last_record_id
    return mascota

@app.get("/mascotas/", response_model=List[Mascota])
async def listar_mascotas():
    query = mascotas.select()
    return await database.fetch_all(query)

@app.get("/mascotas/{mascota_id}", response_model=Mascota)
async def obtener_mascota(mascota_id: int):
    query = mascotas.select().where(mascotas.c.id == mascota_id)
    mascota = await database.fetch_one(query)
    if mascota is None:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    return mascota

# Replace entire resource
@app.put("/mascotas/{mascota_id}", response_model=Mascota)
async def reemplazar_mascota(mascota_id: int, mascota: Mascota):
    # Ensure the resource exists
    existing = await database.fetch_one(mascotas.select().where(mascotas.c.id == mascota_id))
    if existing is None:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")

    # Prevent changing the id
    update_values = {
        "nombre": mascota.nombre,
        "especie": mascota.especie,
        "edad": mascota.edad,
    }

    await database.execute(mascotas.update().where(mascotas.c.id == mascota_id).values(**update_values))

    updated = await database.fetch_one(mascotas.select().where(mascotas.c.id == mascota_id))
    return updated

# Partial update
class MascotaPatch(BaseModel):
    nombre: str | None = None
    especie: str | None = None
    edad: int | None = None

@app.patch("/mascotas/{mascota_id}", response_model=Mascota)
async def modificar_mascota(mascota_id: int, patch: MascotaPatch):
    existing = await database.fetch_one(mascotas.select().where(mascotas.c.id == mascota_id))
    if existing is None:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")

    changes = patch.dict(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")

    await database.execute(mascotas.update().where(mascotas.c.id == mascota_id).values(**changes))

    updated = await database.fetch_one(mascotas.select().where(mascotas.c.id == mascota_id))
    return updated
