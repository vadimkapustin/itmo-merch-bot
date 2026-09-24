"""Модели данных — простые классы, описывающие товар и заказ.

@dataclass сам создаёт конструктор __init__, поэтому класс получается
коротким: мы просто перечисляем поля и их типы.
"""
from dataclasses import dataclass, field


@dataclass
class Product:
    """Товар из каталога."""

    id: int
    title: str
    description: str
    price: int   # цена в звёздах Telegram
    image: str   # путь к картинке на сайте


@dataclass
class OrderItem:
    """Одна строчка заказа: какой товар и сколько штук."""

    product_id: int
    title: str
    qty: int
    price: int

    @property
    def total(self) -> int:
        """Стоимость строчки = цена × количество."""
        return self.price * self.qty


@dataclass
class Order:
    """Заказ пользователя."""

    id: int
    user_id: int
    items: list[OrderItem] = field(default_factory=list)
    is_paid: bool = False
    charge_id: str | None = None  # id платежа (нужен для возврата звёзд)
    created_at: str = ""

    @property
    def total(self) -> int:
        """Сумма заказа = сумма всех строчек."""
        return sum(item.total for item in self.items)
