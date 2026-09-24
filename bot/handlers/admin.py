"""Команды администратора: ответ на обращения и возврат звёзд."""
from html import escape

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from bot.filters import IsAdmin
from database import OrderRepository, SupportRepository

router = Router(name="admin")
# Фильтр на весь роутер: все обработчики ниже работают только для админа.
router.message.filter(IsAdmin())


@router.message(F.reply_to_message, F.text)
async def answer_ticket(
    message: Message, bot: Bot, support: SupportRepository
) -> None:
    """Админ ответил (reply) на обращение — пересылаем ответ пользователю."""
    user_id = await support.get_user_by_admin_message(
        message.reply_to_message.message_id
    )
    if user_id is None:
        await message.answer("Это сообщение не является обращением 🤔")
        return

    await bot.send_message(
        user_id, f"💬 <b>Ответ поддержки:</b>\n\n{escape(message.text)}"
    )
    await message.answer("Ответ отправлен ✅")


@router.message(Command("refund"))
async def refund(
    message: Message, command: CommandObject, bot: Bot, orders: OrderRepository
) -> None:
    """Возвращает звёзды за заказ. Пример: /refund 5

    Удобно при тестах: оплатили заказ — вернули звезду обратно.
    """
    if not command.args or not command.args.isdigit():
        await message.answer("Напишите номер заказа: /refund 5")
        return

    order = await orders.get(int(command.args))
    if order is None or not order.is_paid:
        await message.answer("Оплаченный заказ с таким номером не найден")
        return
    if order.charge_id is None:
        await message.answer("Заказ был бесплатным — возвращать нечего")
        return

    try:
        await bot.refund_star_payment(
            user_id=order.user_id,
            telegram_payment_charge_id=order.charge_id,
        )
    except TelegramBadRequest as error:
        await message.answer(f"Не получилось вернуть: {error.message}")
        return

    await orders.mark_refunded(order.id)
    await message.answer(f"Звёзды за заказ №{order.id} возвращены ✅")
