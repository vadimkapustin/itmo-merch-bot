"""Конкретные репозитории: товары, заказы, обращения в поддержку.

Каждый класс НАСЛЕДУЕТСЯ от BaseRepository и получает от него готовые
методы _execute, _fetch_all, _fetch_one. Сам класс только описывает
свою таблицу и свои запросы.
"""
import json
from pathlib import Path

from database.base import BaseRepository
from database.models import Order, OrderItem, Product


class ProductRepository(BaseRepository):
    """Работа с таблицей товаров."""

    @property
    def create_table_sql(self) -> str:
        return """
            CREATE TABLE IF NOT EXISTS products (
                id          INTEGER PRIMARY KEY,
                title       TEXT    NOT NULL,
                description TEXT    NOT NULL,
                price       INTEGER NOT NULL,
                image       TEXT    NOT NULL
            )
        """

    async def load_from_json(self, path: Path) -> None:
        """Загружает товары из products.json в базу.

        Этот же файл читает сайт-каталог. Так список товаров хранится
        в одном месте, и цены на сайте и в боте всегда совпадают.

        Args:
            path: путь к products.json
        """
        products = json.loads(path.read_text(encoding="utf-8"))
        for item in products:
            # INSERT OR REPLACE: если товар уже есть — обновим его
            await self._execute(
                "INSERT OR REPLACE INTO products "
                "(id, title, description, price, image) VALUES (?, ?, ?, ?, ?)",
                (item["id"], item["title"], item["description"],
                 item["price"], item["image"]),
            )

    async def get(self, product_id: int) -> Product | None:
        """Находит товар по id. Возвращает None, если такого нет."""
        row = await self._fetch_one(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        )
        return Product(**dict(row)) if row else None


class OrderRepository(BaseRepository):
    """Работа с таблицей заказов.

    Товары заказа храним одной строкой в формате JSON (колонка items) —
    для учебного проекта это проще, чем отдельная таблица.
    """

    @property
    def create_table_sql(self) -> str:
        return """
            CREATE TABLE IF NOT EXISTS orders (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                items      TEXT    NOT NULL,
                is_paid    INTEGER NOT NULL DEFAULT 0,
                charge_id  TEXT,
                created_at TEXT    NOT NULL
                           DEFAULT (strftime('%d.%m.%Y %H:%M', 'now', 'localtime'))
            )
        """

    async def create(self, user_id: int, items: list[OrderItem]) -> int:
        """Создаёт новый (пока не оплаченный) заказ.

        Returns:
            Номер созданного заказа.
        """
        items_json = json.dumps(
            [item.__dict__ for item in items], ensure_ascii=False
        )
        return await self._execute(
            "INSERT INTO orders (user_id, items) VALUES (?, ?)",
            (user_id, items_json),
        )

    async def mark_paid(self, order_id: int, charge_id: str | None) -> None:
        """Отмечает заказ оформленным и запоминает id платежа.

        Для бесплатного заказа charge_id = None (платежа не было).
        """
        await self._execute(
            "UPDATE orders SET is_paid = 1, charge_id = ? WHERE id = ?",
            (charge_id, order_id),
        )

    async def mark_refunded(self, order_id: int) -> None:
        """Отмечает, что деньги (звёзды) за заказ вернули."""
        await self._execute(
            "UPDATE orders SET is_paid = 0 WHERE id = ?", (order_id,)
        )

    async def get(self, order_id: int) -> Order | None:
        """Находит заказ по номеру."""
        row = await self._fetch_one(
            "SELECT * FROM orders WHERE id = ?", (order_id,)
        )
        return self._row_to_order(row) if row else None

    async def get_paid_by_user(self, user_id: int) -> list[Order]:
        """Все оплаченные заказы пользователя, новые — сверху."""
        rows = await self._fetch_all(
            "SELECT * FROM orders WHERE user_id = ? AND is_paid = 1 "
            "ORDER BY id DESC",
            (user_id,),
        )
        return [self._row_to_order(row) for row in rows]

    @staticmethod
    def _row_to_order(row) -> Order:
        """Превращает строку из базы в объект Order."""
        items = [OrderItem(**item) for item in json.loads(row["items"])]
        return Order(
            id=row["id"],
            user_id=row["user_id"],
            items=items,
            is_paid=bool(row["is_paid"]),
            charge_id=row["charge_id"],
            created_at=row["created_at"],
        )


class SupportRepository(BaseRepository):
    """Работа с обращениями в техподдержку.

    Главная задача — помнить, какое сообщение у админа относится
    к какому пользователю. Тогда админ просто отвечает (reply)
    на сообщение, а бот знает, кому переслать ответ.
    """

    @property
    def create_table_sql(self) -> str:
        return """
            CREATE TABLE IF NOT EXISTS tickets (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id          INTEGER NOT NULL,
                text             TEXT    NOT NULL,
                admin_message_id INTEGER
            )
        """

    async def create(self, user_id: int, text: str) -> int:
        """Сохраняет обращение. Возвращает его номер."""
        return await self._execute(
            "INSERT INTO tickets (user_id, text) VALUES (?, ?)",
            (user_id, text),
        )

    async def set_admin_message(self, ticket_id: int, message_id: int) -> None:
        """Запоминает id сообщения, которое бот отправил админу."""
        await self._execute(
            "UPDATE tickets SET admin_message_id = ? WHERE id = ?",
            (message_id, ticket_id),
        )

    async def get_user_by_admin_message(self, message_id: int) -> int | None:
        """По сообщению у админа находит, кто написал обращение."""
        row = await self._fetch_one(
            "SELECT user_id FROM tickets WHERE admin_message_id = ?",
            (message_id,),
        )
        return row["user_id"] if row else None
