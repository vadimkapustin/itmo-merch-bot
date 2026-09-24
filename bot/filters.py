"""Свои фильтры для обработчиков."""
from aiogram.filters import BaseFilter
from aiogram.types import Message

from config import Config


class IsAdmin(BaseFilter):
    """Пропускает только сообщения от администратора.

    Наследуемся от BaseFilter из aiogram и переопределяем __call__:
    aiogram вызывает его для каждого сообщения и смотрит на ответ
    True (пропустить) или False (не пропускать).
    """

    async def __call__(self, message: Message, config: Config) -> bool:
        return message.from_user.id == config.admin_id
