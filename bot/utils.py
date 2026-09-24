"""Вспомогательные функции, которые нужны в нескольких местах."""
import json

from database.models import OrderItem

# Максимум штук одного товара в заказе (защита от ошибок и шуток).
MAX_QTY = 20

# Приставка в payload счёта, чтобы потом понять, какой заказ оплатили.
PAYLOAD_PREFIX = "order:"


def parse_cart(raw: str) -> dict[int, int]:
    """Разбирает корзину, которую прислал сайт.

    Сайт присылает строку вида
    {"items": [{"id": 1, "qty": 2}, {"id": 2, "qty": 1}]}

    Args:
        raw: строка JSON от сайта.

    Returns:
        Словарь {id товара: количество}.

    Raises:
        ValueError: если данные испорчены.
    """
    try:
        data = json.loads(raw)
        cart = {int(item["id"]): int(item["qty"]) for item in data["items"]}
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        raise ValueError("Некорректная корзина") from error

    if not cart or any(qty < 1 or qty > MAX_QTY for qty in cart.values()):
        raise ValueError("Некорректное количество товара")
    return cart


def format_items(items: list[OrderItem]) -> str:
    """Делает из товаров заказа красивый текст (по строчке на товар)."""
    return "\n".join(
        f"• {item.title} × {item.qty} = {item.total} ⭐" for item in items
    )


def make_payload(order_id: int) -> str:
    """Номер заказа → строка для счёта, например 'order:15'."""
    return f"{PAYLOAD_PREFIX}{order_id}"


def order_id_from_payload(payload: str) -> int:
    """Строка из счёта → номер заказа ('order:15' → 15)."""
    return int(payload.removeprefix(PAYLOAD_PREFIX))
