#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import subprocess
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]


def compose(*args):
    return subprocess.check_output(
        ["docker", "compose", *args], cwd=ROOT, text=True
    ).strip()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)
    print("OK:", message)


def request(base, path):
    with urllib.request.urlopen(base + path, timeout=10) as response:
        return json.load(response)


def sql(query):
    return compose("exec", "-T", "db", "sh", "-c",
                   'exec psql -U postgres -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -tAc "$1"',
                   "sh", query)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--persistencia", action="store_true")
    args = parser.parse_args()
    config = json.loads(compose("config", "--format", "json"))
    services = config["services"]
    require(set(services) == {"db", "api", "proxy"}, "Existen exactamente tres servicios")
    require(not services["db"].get("ports") and not services["api"].get("ports"),
            "BD y API no publican puertos")
    require(config["networks"]["interna"].get("internal") is True, "Red interna aislada")
    published = services["proxy"]["ports"][0]["published"]
    base = f"http://127.0.0.1:{published}"
    require(request(base, "/health") == {"status": "ok"}, "Proxy y API responden")
    database = request(base, "/db")
    require(database.get("db") == "conectada" and "PostgreSQL" in database.get("version", ""),
            "La API consulta PostgreSQL")
    ip = compose("exec", "-T", "api", "python", "-c",
                 "import socket; print(socket.gethostbyname('db'))")
    require(bool(ip), "DNS del servicio db: " + ip)
    uid = compose("exec", "-T", "api", "id", "-u")
    require(uid == "1001", "API ejecutada con UID 1001")
    for service in ("db", "api"):
        container = compose("ps", "-q", service)
        bindings = json.loads(subprocess.check_output(
            ["docker", "inspect", "--format", "{{json .HostConfig.PortBindings}}", container],
            text=True))
        require(not bindings, service + " sin enlaces de puertos al host")
    if args.persistencia:
        marker = uuid.uuid4().hex
        table = "prueba_persistencia_" + marker
        sql(f"CREATE TABLE {table} (dato TEXT NOT NULL); INSERT INTO {table} VALUES ('{marker}');")
        try:
            compose("down")
            compose("up", "-d", "--wait", "--wait-timeout", "120")
            require(sql(f"SELECT dato FROM {table}") == marker,
                    "El registro persiste tras eliminar y recrear contenedores")
            require(request(base, "/db").get("db") == "conectada", "API conectada después del reinicio")
        finally:
            sql(f"DROP TABLE IF EXISTS {table}")
    print("Validación completada" + (" con persistencia" if args.persistencia else ""))


if __name__ == "__main__":
    main()
