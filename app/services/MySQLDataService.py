from __future__ import annotations

import os
import mysql.connector
from mysql.connector import MySQLConnection
from .AbstractBaseDataService import AbstractBaseDataService


def _build_config_from_env() -> dict:
    return {
        "host":     os.environ.get("DB_HOST", "localhost"),
        "port":     int(os.environ.get("DB_PORT", "3306")),
        "user":     os.environ.get("DB_USER", "root"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "database": os.environ.get("DB_NAME", "classicmodels"),
    }


class MySQLDataService(AbstractBaseDataService):

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        env = _build_config_from_env()
        self._conn_params: dict = {
            "host":     config.get("host",     env["host"]),
            "port":     int(config.get("port", env["port"])),
            "user":     config.get("user",     env["user"]),
            "password": config.get("password", env["password"]),
            "database": config.get("database", env["database"]),
        }
        self._table: str = str(config["table"])
        pk = config["primary_key"]
        self._pk_fields: list[str] = [pk] if isinstance(pk, str) else list(pk)

    def _connect(self) -> MySQLConnection:
        return mysql.connector.connect(**self._conn_params)

    def _row_to_dict(self, cursor, row: tuple) -> dict:
        cols = [d[0] for d in cursor.description]
        return dict(zip(cols, row))

    def _pk_where_clause(self) -> str:
        return " AND ".join(f"`{col}` = %s" for col in self._pk_fields)

    def _pk_values(self, primary_key: str | dict) -> tuple:
        if isinstance(primary_key, dict):
            return tuple(primary_key[col] for col in self._pk_fields)
        return (primary_key,)

    def retrieveByPrimaryKey(self, primary_key: str | dict) -> dict:
        sql = f"SELECT * FROM `{self._table}` WHERE {self._pk_where_clause()}"
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, self._pk_values(primary_key))
                row = cur.fetchone()
                return {} if row is None else self._row_to_dict(cur, row)
        finally:
            conn.close()

    def retrieveByTemplate(self, template: dict) -> list[dict]:
        if template:
            where = " AND ".join(f"`{col}` = %s" for col in template)
            sql = f"SELECT * FROM `{self._table}` WHERE {where}"
            values = tuple(template.values())
        else:
            sql = f"SELECT * FROM `{self._table}`"
            values = ()
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                rows = cur.fetchall()
                return [self._row_to_dict(cur, row) for row in rows]
        finally:
            conn.close()

    def create(self, payload: dict) -> str:
        cols = ", ".join(f"`{c}`" for c in payload)
        placeholders = ", ".join(["%s"] * len(payload))
        sql = f"INSERT INTO `{self._table}` ({cols}) VALUES ({placeholders})"
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, tuple(payload.values()))
            conn.commit()
        finally:
            conn.close()
        if len(self._pk_fields) == 1:
            return str(payload.get(self._pk_fields[0], ""))
        return "|".join(str(payload.get(f, "")) for f in self._pk_fields)

    def updateByPrimaryKey(self, primary_key: str | dict, payload: dict) -> int:
        set_clause = ", ".join(f"`{col}` = %s" for col in payload)
        sql = f"UPDATE `{self._table}` SET {set_clause} WHERE {self._pk_where_clause()}"
        values = tuple(payload.values()) + self._pk_values(primary_key)
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                affected = cur.rowcount
            conn.commit()
            return affected
        finally:
            conn.close()

    def deleteByPrimaryKey(self, primary_key: str | dict) -> int:
        sql = f"DELETE FROM `{self._table}` WHERE {self._pk_where_clause()}"
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, self._pk_values(primary_key))
                affected = cur.rowcount
            conn.commit()
            return affected
        finally:
            conn.close()
