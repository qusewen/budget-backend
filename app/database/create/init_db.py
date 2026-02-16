import asyncio
import os

import asyncpg
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", "")
DB_NAME = os.getenv("DB_NAME", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_DRIVER = os.getenv("DB_DRIVER", "")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


async def create_table():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NULL,
            password TEXT NOT NULL,
            age INTEGER NOT NULL,
            isActive BOOLEAN NOT NULL DEFAULT false
        )
    """
    )
    print("Таблица users создана")

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS currency (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            value NUMERIC(10, 6) NULL
        )
    """
    )
    print("Таблица currency создана")

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS role (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            value NUMERIC(10, 6) NULL,
            description TEXT NULL
        )
    """
    )
    print("Таблица role создана")

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expense_types (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NULL,
            content TEXT NULL,
            user_id INT NULL REFERENCES users(id)
        )
    """
    )
    print("Таблица expense_types создана")

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS budget_list (
            id SERIAL PRIMARY KEY,
            date TIMESTAMPTZ NULL,
            name TEXT NOT NULL,
            value NUMERIC(10, 6) NULL,
            currency INT REFERENCES currency(id),
            description TEXT NULL,
            content TEXT NULL,
            user_id INT REFERENCES users(id),
            type_id INT NULL REFERENCES expense_types(id)
        )
    """
    )
    print("Таблица budget_list создана")

    await conn.close()


asyncio.run(create_table())
