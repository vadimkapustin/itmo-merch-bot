"""Базовый класс для всех «репозиториев».

Репозиторий — это класс, который умеет работать с одной таблицей в базе.
Общий код (подключиться, выполнить запрос, получить строки) написан
здесь ОДИН раз, а конкретные репозитории его наследуют.
Это принцип DRY: «не повторяйся».
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import aiosqlite


class BaseRepository(ABC):
    """Родительский класс для работы с таблицей SQLite.

    ABC означает «абстрактный класс»: создать объект прямо от него нельзя,
    только от наследников, которые заполнят метод create_table_sql.
    """

    def __init__(self, db_path: Path) -> None:
        """Запоминаем путь к файлу базы данных.

        Args:
            db_path: путь к файлу .db
        """
        self.db_path = db_path

    @property
    @abstractmethod
    def create_table_sql(self) -> str:
        """SQL-запрос, который создаёт таблицу. Каждый наследник пишет свой."""

    async def create_table(self) -> None:
        """Создаёт таблицу, если её ещё нет."""
        await self._execute(self.create_table_sql)

    async def _execute(self, query: str, params: tuple[Any, ...] = ()) -> int:
        """Выполняет запрос, который ИЗМЕНЯЕТ данные (INSERT, UPDATE...).

        Args:
            query: текст SQL-запроса, вместо значений ставим знаки ?
            params: значения для знаков ? (так защищаемся от SQL-инъекций)

        Returns:
            id последней добавленной строки.
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, params)
            await db.commit()  # сохраняем изменения в файл
            return cursor.lastrowid

    async def _fetch_all(
        self, query: str, params: tuple[Any, ...] = ()
    ) -> list[aiosqlite.Row]:
        """Выполняет SELECT и возвращает все найденные строки."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row  # строки как словари: row["title"]
            cursor = await db.execute(query, params)
            return list(await cursor.fetchall())

    async def _fetch_one(
        self, query: str, params: tuple[Any, ...] = ()
    ) -> aiosqlite.Row | None:
        """Выполняет SELECT и возвращает одну строку (или None)."""
        rows = await self._fetch_all(query, params)
        return rows[0] if rows else None
