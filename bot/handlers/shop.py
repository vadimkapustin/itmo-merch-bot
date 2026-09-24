"""Заказ и оплата звёздами Telegram, раздел «Мои заказы».

Как проходит покупка:
1. Пользователь собирает корзину на сайте и жмёт «Оплатить».
2. Сайт отправляет корзину в бот (приходит как web_app_data).
3. Бот проверяет товары по своей базе, создаёт заказ и присылает счёт.
4. Telegram спрашивает бота «можно принимать оплату?» (pre_checkout).
5. После оплаты приходит successful_payment — отмечаем заказ оплаченным.
"""
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import LabeledPrice, Message, PreCheckoutQuery

from bot import texts
from bot.utils import (
    format_items,
    make_payload,
    order_id_from_payload,
    parse_cart,
)
from config import Config
from database import OrderItem, OrderRepository, ProductRepository

router = Router(name="shop")

# Валюта «звёзды Telegram». Для звёзд платёжный провайдер не нужен.
STARS_CURRENCY = "XTR"

# Сколько последних заказов показывать в «Мои заказы».
ORDERS_TO_SHOW = 10


@router.message(F.web_app_data)
async def handle_cart(
    message: Message,
    bot: Bot,
    products: ProductRepository,
    orders: OrderRepository,
    config: Config,
) -> None:
    """Получает корзину с сайта, создаёт заказ и отправляет счёт."""
    try:
        cart = parse_cart(message.web_app_data.data)
    except ValueError:
        await message.answer(texts.BAD_CART)
        return

    # Цены берём из НАШЕЙ базы, а не с сайта: так никто не сможет
    # подменить цену в браузере и купить свитшот за 0 звёзд.
    items = []
    for product_id, qty in cart.items():
        product = await products.get(product_id)
        if product is not None:
            items.append(OrderItem(product.id, product.title, qty, product.price))

    if not items:
        await message.answer(texts.BAD_CART)
        return

    order_id = await orders.create(message.from_user.id, items)
    total = sum(item.total for item in items)

    # Telegram не умеет выставлять счёт на 0 звёзд.
    # Поэтому бесплатный заказ сразу считаем оформленным, без оплаты.
    if total == 0:
        await complete_order(message, bot, orders, config, order_id, None)
        return

    await message.answer_invoice(
        title=f"Заказ №{order_id}",
        description=format_items(items),
        payload=make_payload(order_id),
        currency=STARS_CURRENCY,
        prices=[LabeledPrice(label="Мерч ИТМО", amount=total)],
    )


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery, orders: OrderRepository) -> None:
    """Последняя проверка перед списанием звёзд.

    На этот запрос нужно ответить в течение 10 секунд,
    иначе Telegram отменит оплату.
    """
    order = await orders.get(order_id_from_payload(query.invoice_payload))
    if order is None or order.is_paid:
        await query.answer(ok=False, error_message="Заказ не найден или уже оплачен")
        return
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def payment_done(
    message: Message, bot: Bot, orders: OrderRepository, config: Config
) -> None:
    """Оплата прошла: оформляем заказ."""
    payment = message.successful_payment
    await complete_order(
        message,
        bot,
        orders,
        config,
        order_id_from_payload(payment.invoice_payload),
        payment.telegram_payment_charge_id,
    )


async def complete_order(
    message: Message,
    bot: Bot,
    orders: OrderRepository,
    config: Config,
    order_id: int,
    charge_id: str | None,
) -> None:
    """Отмечает заказ оформленным и сообщает покупателю и админу.

    Одна функция и для платных, и для бесплатных заказов (принцип DRY).

    Args:
        order_id: номер заказа.
        charge_id: id платежа или None, если заказ бесплатный.
    """
    await orders.mark_paid(order_id, charge_id)
    await message.answer(texts.PAYMENT_OK.format(order_id=order_id))

    order = await orders.get(order_id)
    user = message.from_user
    await bot.send_message(
        config.admin_id,
        f"🛍 Новый заказ №{order_id} от {user.full_name} (id {user.id})\n\n"
        f"{format_items(order.items)}\nИтого: {order.total} ⭐",
    )


@router.message(F.text == texts.BTN_MY_ORDERS)
async def my_orders(
    message: Message, state: FSMContext, orders: OrderRepository
) -> None:
    """Показывает количество оплаченных заказов и их состав."""
    await state.clear()
    user_orders = await orders.get_paid_by_user(message.from_user.id)
    if not user_orders:
        await message.answer(texts.NO_ORDERS)
        return

    parts = [f"<b>📦 Всего заказов: {len(user_orders)}</b>"]
    for order in user_orders[:ORDERS_TO_SHOW]:
        parts.append(
            f"<b>№{order.id}</b> от {order.created_at}\n"
            f"{format_items(order.items)}\n"
            f"Итого: {order.total} ⭐"
        )
    await message.answer("\n\n".join(parts))
