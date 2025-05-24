# 🐘 MySQL a PostgreSQL Migration Script (con soporte extendido de tipos y funciones)

Este script en Python permite migrar de forma avanzada esquemas de bases de datos desde **MySQL** hacia **PostgreSQL** utilizando **SQLAlchemy**.

> ⚠️ Este script fue desarrollado debido a limitaciones encontradas en herramientas automatizadas como `pgloader`, especialmente en proyectos que dependen de tipos y funciones no soportadas como `uuid_to_bin(uuid())` o columnas `VARBINARY(16)` utilizadas para UUIDs.

---

## 🚀 Características principales

- ✔️ Conversión automática de tipos no soportados:
  - `VARBINARY(16)` → `UUID`
  - `TINYINT` → `BOOLEAN`
  - `ENUM(...)` → `VARCHAR(255)`
  - `DATETIME` → `TIMESTAMP`
  - `DOUBLE` → `DOUBLE PRECISION`

- 🔁 Reemplazo automático de funciones MySQL no disponibles en PostgreSQL:
  - `uuid_to_bin(uuid())` → `gen_random_uuid()` (requiere extensión `pgcrypto`)
  - Eliminación de `ON UPDATE CURRENT_TIMESTAMP` (no directamente soportado en PostgreSQL)

- 🧽 Limpieza del SQL antes de ejecutar:
  - Elimina claves foráneas si es necesario
  - Elimina collation (`COLLATE`) específico de MySQL
  - Reemplaza funciones y expresiones no compatibles

- 🛠️ Preparado para esquemas complejos y con múltiples tablas
- 👁️ Soporte visual de conversiones y advertencias en consola

---

## 📦 Requisitos

- Python 3.x
- Paquetes:
  ```bash
  pip install sqlalchemy pymysql psycopg2

## ¿Por qué no usar pgloader?
- Herramientas como pgloader son útiles para migraciones simples, pero fallan en situaciones como:

  - Uso de uuid_to_bin() y VARBINARY(16) para UUIDs.
  - Funciones como ON UPDATE CURRENT_TIMESTAMP.
  - Tipos ENUM no definidos previamente en PostgreSQL.
  - Collation no compatibles (utf8mb4_general_ci, etc.).
  - Necesidad de convertir estructuras SQL avanzadas y personalizadas.

Este script maneja todas esas situaciones de forma programática y transparente, ademas se estaran agregando mejoras.