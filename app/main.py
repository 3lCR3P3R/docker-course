import os

from fastapi import FastAPI
import psycopg

app = FastAPI(title="API App SENA", version="1.0.0")

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_ADMIN_PASSWORD", "")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db")
def db_version():
    conninfo = (
        f"host={DB_HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
    )
    try:
        with psycopg.connect(conninfo, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
        return {"db": "conectada", "version": version}
    except Exception as exc:
        return {"db": "sin conexion", "detalle": str(exc)}
