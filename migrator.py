from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects.mysql import ENUM as MySQLEnum
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import dialect as pg_dialect
from sqlalchemy.dialects.mysql import TINYINT, VARBINARY
from sqlalchemy.dialects.postgresql import UUID, BOOLEAN
from sqlalchemy import Table, Column
from sqlalchemy.sql.schema import MetaData
import re

# Conexiones
mysql_url = "mysql+pymysql://root:123456789@localhost:3306/granjacob_uuid_migration"
postgresql_url = "postgresql+psycopg2://postgres:123456789@localhost:7778/granjacob"

mysql_engine = create_engine(mysql_url)
postgres_engine = create_engine(postgresql_url)

# Leer metadatos desde MySQL
mysql_metadata = MetaData()
mysql_metadata.reflect(bind=mysql_engine)

# Función para convertir SQL a PostgreSQL-compatible
def convert_mysql_to_postgres(sql: str) -> str:
    sql = sql.strip()

    # Reemplazos simples
    sql = sql.replace("VARBINARY(16)", "UUID")
    sql = sql.replace("uuid_to_bin(uuid())", "gen_random_uuid()")  # o "gen_uuid_v4()"
    sql = re.sub(r"ON UPDATE CURRENT_TIMESTAMP", "", sql)
    sql = sql.replace("DATETIME", "TIMESTAMP")

    # Limpia dobles espacios
    sql = re.sub(r"\s{2,}", " ", sql)

    return sql

def replace_enum_columns(table):
    for column in table.columns:
        if isinstance(column.type, MySQLEnum):
            print(f"⚠️ Reemplazando ENUM en columna '{column.name}' por VARCHAR en tabla '{table.name}'")
            column.type = String(255)


def replace_mysql_types(table: Table):
    for column in table.columns:
        coltype = column.type

        # Reemplazar TINYINT → BOOLEAN
        if isinstance(coltype, TINYINT):
            column.type = BOOLEAN()

        # Reemplazar VARBINARY(16) → UUID
        elif isinstance(coltype, VARBINARY) and getattr(coltype, 'length', None) == 16:
            column.type = UUID()

        # Puedes agregar más reemplazos aquí si lo necesitas
        # Ej: DATETIME → TIMESTAMP, etc.

    return table

def replace_enum_with_varchar(sql: str) -> str:
    return re.sub(r'ENUM\([^)]+\)', 'VARCHAR(255)', sql, flags=re.IGNORECASE)

def fix_double_type(sql: str) -> str:
    return re.sub(r'\bDOUBLE\b', 'DOUBLE PRECISION', sql, flags=re.IGNORECASE)

def remove_collation(sql):
    return re.sub(r'COLLATE\s+\w+', '', sql)

def remove_foreign_keys(sql: str) -> str:
    lines = sql.splitlines()
    lines = [line for line in lines if 'FOREIGN KEY' not in line and 'REFERENCES' not in line]
    return "\n".join(lines)

# Crear tablas en PostgreSQL
with postgres_engine.begin() as conn:
    for table in mysql_metadata.sorted_tables:
        print(f"Creando tabla: {table.name}")


        try:
            replace_enum_columns(table)  # <--- aquí
            replace_mysql_types( table )
            raw_sql = str(CreateTable(table).compile(dialect=pg_dialect()))

            clean_sql = raw_sql.replace("ON UPDATE CURRENT_TIMESTAMP", "")

            '''if table.name not in [
                'gj_app_dto', 'gj_app_email_template', 'gj_app_form','gj_app_projection','gj_app_query',
                'gj_module', 'gj_account_group', 'gj_account_permission', 'gj_account_role', 'gj_activity_log']:'''
            try:
                clean_sql = convert_mysql_to_postgres(raw_sql)
                clean_sql = remove_collation(clean_sql)
                # clean_sql = remove_foreign_keys(clean_sql)
                clean_sql = fix_double_type(clean_sql)
                clean_sql = replace_enum_with_varchar(clean_sql)
            except Exception as e:
                continue

            clean_sql = clean_sql.replace("VARBINARY(16)", "UUID")
            clean_sql = clean_sql.replace("DEFAULT (uuid_to_bin(uuid()))", "DEFAULT gen_random_uuid()")
            clean_sql = clean_sql.replace("DEFAULT (md5(`name`))", "")

            conn.execute(text(clean_sql))

        except Exception as e:
            print(f"❌ Error al crear la tabla {table.name}: {e}")
            print(f"📄 SQL para {table.name}:\n{clean_sql}")





'''from sqlalchemy import create_engine, MetaData

# Conexión genérica
engine = create_engine("mysql+pymysql://root:123456789@localhost:3306/granjacob_uuid")  # cambia el motor aquí
metadata = MetaData()
metadata.reflect(bind=engine)

# Mostrar tablas y relaciones
for table_name, table in metadata.tables.items():
    print(f"Tabla: {table_name}")
    for fk in table.foreign_keys:
        print(f"  -> Relación: {fk.column.table.name} (columna: {fk.column.name})")'''