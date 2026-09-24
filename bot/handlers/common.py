"""Команда /start и кнопка «Информация»."""
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot import texts
from bot.keyboards import main_menu
from config import Config

router = Router(name="common")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, config: Config) -> None:
    """Приветствие и главное меню. Срабатывает на команду /start."""
    await state.clear()  # сбрасываем любой «режим», если он был
    await message.answer(texts.START, reply_markup=main_menu(config.webapp_url))


@router.message(F.text == texts.BTN_INFO)
async def show_info(message: Message, state: FSMContext) -> None:
    """Показывает информацию о магазине."""
    await state.clear()
    await message.answer(texts.INFO)
