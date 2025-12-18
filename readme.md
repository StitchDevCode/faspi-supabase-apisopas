Aquí tienes un `README.md` completo (cópialo tal cual). Está escrito para que lo uses como **apunte personal** y como documentación del repo.

````md
# Sopas API (FastAPI + SQLAlchemy + Postgres/Supabase) — Offline First

API para registrar y consultar pedidos de “Sopas La Tía”, pensada para ser consumida por una app Android que trabaja **offline-first** (Room) y sincroniza cuando vuelve la conexión.

Este proyecto usa:
- **FastAPI** (API)
- **SQLAlchemy 2.x** (ORM)
- **PostgreSQL** (Supabase)
- **Pydantic v2** (DTOs / validación)
- **Uvicorn** (servidor)

---

## ✅ Objetivo principal (Offline-First)
La app Android guarda pedidos en Room cuando no hay internet y luego sincroniza con el backend.

Para evitar problemas típicos de offline:
- El backend genera el **ID oficial** del pedido (`id`, UUID).
- El cliente envía un **client_request_id** (idempotency key) para evitar duplicados cuando reintenta enviar el mismo pedido.
- Se usa **soft delete** (`is_deleted`, `deleted_at`) para que los “borrados” también se sincronicen a otros dispositivos.

---

## 📁 Estructura de carpetas

```text
app/
├── main.py                  # Crea app FastAPI, incluye routers, startup
├── config.py                # Settings (DATABASE_URL, etc.)
├── database/
│   ├── __init__.py          # Exporta Base
│   └── db.py                # engine, SessionLocal, get_db
├── models/
│   ├── pedido.py            # Modelo Pedido (tabla pedidos)
│   └── tipo_sopa.py         # Catálogo de tipos de sopa (precio editable)
├── schemas/
│   ├── pedido.py            # DTOs Pydantic (PedidoCreate, PedidoOut, etc.)
│   └── tipo_sopa.py         # DTOs del catálogo
├── routers/
│   ├── pedido_router.py     # Endpoints /pedidos
│   └── catalogo_router.py   # Endpoints /catalogo
└── services/
    ├── pedido_service.py    # Reglas de negocio: total/vuelto, validaciones
    └── catalogo_service.py  # CRUD catálogo (tipos de sopa)
````

---

## 🧰 Requisitos

* Python 3.12+
* `pip`
* (Opcional) Docker si usas Postgres local
* Cuenta de Supabase (si usas Supabase)

---

## ⚙️ Instalación (Local con venv)

### 1) Crear y activar venv

```bash
python -m venv venv
venv\Scripts\activate

```

### 2) Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3) Variables de entorno

Se usa `DATABASE_URL`. Ejemplo (Supabase):

```bash
# Windows PowerShell
$env:DATABASE_URL="postgresql+psycopg2://postgres:TU_PASSWORD@db.xxxxx.supabase.co:5432/postgres?sslmode=require"
```

> Nota: en Supabase la URL se obtiene en **Project Settings → Database → Connection string**.

---

## ▶️ Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

* API: `http://127.0.0.1:8000`
* Swagger: `http://127.0.0.1:8000/docs`

---

## 🧠 Conceptos clave aprendidos

### 1) Modelo vs Schema

* **Model (SQLAlchemy)**: representa la tabla en la base de datos.
* **Schema (Pydantic)**: representa lo que entra y sale por HTTP (DTOs).

### 2) `Mapped` en SQLAlchemy 2.x

En SQLAlchemy moderno se usa:

```py
id: Mapped[str] = mapped_column(String(36), primary_key=True)
```

* `Mapped[str]` = tipo Python del atributo
* `mapped_column(...)` = definición de columna DB

### 3) `create_all()` NO altera tablas existentes

`Base.metadata.create_all()`:

* ✅ crea tablas nuevas
* ❌ NO agrega columnas a tablas existentes

Si agregas campos nuevos al modelo y la tabla ya existía, debes hacer:

* migración (Alembic) o
* `ALTER TABLE` manual en Supabase

---

## 🗃️ Base de datos: Supabase (Postgres)

Si ya existía la tabla `pedidos` y se agregaron campos nuevos (offline-first), hay que crearlos manualmente:

```sql
alter table public.pedidos
  add column if not exists client_id varchar(80);

alter table public.pedidos
  add column if not exists client_request_id varchar(80);

alter table public.pedidos
  add column if not exists is_deleted boolean not null default false;

alter table public.pedidos
  add column if not exists deleted_at timestamptz null;

create index if not exists ix_pedidos_client_id on public.pedidos (client_id);
create unique index if not exists ux_pedidos_client_request_id on public.pedidos (client_request_id);
create index if not exists ix_pedidos_is_deleted on public.pedidos (is_deleted);
```

---

## 🧾 Reglas de negocio del Pedido (backend manda)

El backend recalcula:

* `total = precio_catalogo * cantidad`
* `vuelto = monto_pagado - total` (si no es pago exacto)
* No se confía en el total que mande el cliente.

---

## 🆔 IDs: `id` vs `client_request_id` vs `client_id`

### `id`

* Lo genera el backend (UUID).
* Es el ID oficial del pedido en servidor.

### `client_request_id` (idempotency key)

* Lo genera el cliente (Android) por cada pedido creado offline.
* Evita duplicados si la app reintenta enviar el mismo pedido por mala conexión.

### `client_id`

* Identificador del dispositivo/instalación (opcional).
* Ayuda a auditoría y debugging.

---

## 🧪 Pruebas rápidas (Swagger/Postman)

### 1) EFECTIVO pago exacto

```json
{
  "client_request_id": "a1f9b0d0-1c5f-4c90-9c3e-111111111111",
  "client_id": "android-julio-01",
  "cliente": "Carlos Pérez",
  "tipo_sopa_codigo": "CON_EMPAQUE",
  "metodo_pago": "EFECTIVO",
  "cantidad": 1,
  "direccion": "Managua Centro",
  "pago_con_monto_exacto": true,
  "monto_pagado": 0
}
```

### 2) EFECTIVO paga con 500 (vuelto)

```json
{
  "client_request_id": "b2e8c4a3-9f0b-4e5a-8d22-222222222222",
  "client_id": "android-julio-01",
  "cliente": "María López",
  "tipo_sopa_codigo": "CON_EMPAQUE",
  "metodo_pago": "EFECTIVO",
  "cantidad": 2,
  "direccion": "Altamira",
  "pago_con_monto_exacto": false,
  "monto_pagado": 500
}
```

### 3) TRANSFERENCIA

```json
{
  "client_request_id": "c3d7e9b1-7a44-4c33-9b88-333333333333",
  "client_id": "android-julio-02",
  "cliente": "José Martínez",
  "tipo_sopa_codigo": "SIN_EMPAQUE",
  "metodo_pago": "TRANSFERENCIA",
  "cantidad": 1,
  "direccion": "Carretera Sur",
  "pago_con_monto_exacto": true,
  "monto_pagado": 0
}
```

✅ Tip: manda el mismo JSON dos veces con el mismo `client_request_id`.

* No debe duplicar si la idempotencia está aplicada.

---

## 🧯 Cómo leer errores en FastAPI (guía rápida)

### `ResponseValidationError`

Significa: el endpoint devolvió algo que **no coincide con `response_model`**.

Ejemplo:

* `client_request_id` en la respuesta llegó `None`
* pero en `PedidoOut` era `str` (requerido)

Solución típica:

* asegurar que el servicio asigna esos campos al crear
* o hacer el campo opcional si hay data vieja
* o limpiar registros viejos en DB

---

## ✅ Pendientes / Próximos pasos

* Endpoint de sincronización real:

  * `GET /sync/pull?since=...`
  * `POST /sync/push`
* Implementar soft delete en endpoints (si aplica)
* Migraciones con **Alembic**
* Autenticación (si se necesita multiusuario formal)
* Deploy (Render/Railway/Fly.io)

---


## Proyecto de aprendizaje para dominar APIs con FastAPI y sincronización offline-first.


