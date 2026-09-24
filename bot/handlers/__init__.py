"""Обработчики (handlers) — функции, которые отвечают на действия пользователя.

Они разложены по файлам-«роутерам» по смыслу:
admin — ответы администратора, common — старт и информация,
shop — заказ и оплата, support — техподдержка.
"""
from aiogram import Router

from bot.handlers import admin, common, shop, support


def get_routers() -> list[Router]:
    """Возвращает все роутеры в нужном порядке.

    Порядок важен: aiogram проверяет роутеры сверху вниз.
    support стоит последним, потому что в режиме «пишу вопрос» он
    ловит ЛЮБОЕ сообщение, а кнопки меню должны срабатывать раньше.
    """
    return [admin.router, common.router, shop.router, support.router]
