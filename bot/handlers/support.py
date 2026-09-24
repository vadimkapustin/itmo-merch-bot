"""Техподдержка: пользователь пишет вопрос, бот пересылает его админу."""
from html import escape

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot import texts
from bot.keyboards import cancel_menu, main_menu
from bot.states import SupportForm
from config import Config
from database import SupportRepository

router = Router(name="support")


# Два декоратора = две причины запустить функцию: кнопка или команда.
# /paysupport требуется правилами Telegram для ботов, принимающих звёзды.
@router.message(F.text == texts.BTN_SUPPORT)
@router.message(Command("paysupport"))
async def start_support(message: Message, state: FSMContext) -> None:
    """Включает режим «пишу вопрос»."""
    await state.set_state(SupportForm.waiting_message)
    await message.answer(texts.SUPPORT_ASK, reply_markup=cancel_menu())


@router.message(SupportForm.waiting_message, F.text == texts.BTN_CANCEL)
async def cancel_support(
    message: Message, state: FSMContext, config: Config
) -> None:
    """Кнопка «Отмена»: выходим из режима и возвращаем меню."""
    await state.clear()
    await message.answer(
        texts.SUPPORT_CANCELLED, reply_markup=main_menu(config.webapp_url)
    )


@router.message(SupportForm.waiting_message, F.text)
async def receive_question(
    message: Message,
    state: FSMContext,
    bot: Bot,
    support: SupportRepository,
    config: Config,
) -> None:
    """Сохраняет вопрос и отправляет его администратору."""
    user = message.from_user
    ticket_id = await support.create(user.id, message.text)

    # escape() защищает от поломки HTML-разметки, если в тексте есть < или >
    sent = await bot.send_message(
        config.admin_id,
        f"✉️ <b>Обращение №{ticket_id}</b> от {escape(user.full_name)} "
        f"(id {user.id})\n\n{escape(message.text)}\n\n"
        "<i>Ответьте на это сообщение (reply), чтобы ответить пользователю.</i>",
    )
    await support.set_admin_message(ticket_id, sent.message_id)

    await state.clear()
    await message.answer(
        texts.SUPPORT_SENT, reply_markup=main_menu(config.webapp_url)
    )


@router.message(SupportForm.waiting_message)
async def question_not_text(message: Message) -> None:
    """Если вместо текста прислали фото, стикер и т.п."""
    await message.answer(texts.SUPPORT_ONLY_TEXT)
