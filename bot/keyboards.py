"""Клавиатуры (кнопки под полем ввода сообщения)."""
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

from bot import texts


def main_menu(webapp_url: str) -> ReplyKeyboardMarkup:
    """Главное меню с четырьмя кнопками.

    Кнопка «Сделать заказ» особенная: у неё есть web_app, поэтому
    по нажатию Telegram открывает наш сайт-каталог внутри себя.
    Важно: передавать данные с сайта в бота (sendData) можно только
    из сайта, открытого именно такой кнопкой клавиатуры.

    Args:
        webapp_url: адрес сайта-каталога.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts.BTN_ORDER,
                            web_app=WebAppInfo(url=webapp_url))],
            [KeyboardButton(text=texts.BTN_MY_ORDERS),
             KeyboardButton(text=texts.BTN_INFO)],
            [KeyboardButton(text=texts.BTN_SUPPORT)],
        ],
        resize_keyboard=True,  # кнопки компактные, а не на пол-экрана
    )


def cancel_menu() -> ReplyKeyboardMarkup:
    """Одна кнопка «Отмена» — показываем, пока человек пишет в поддержку."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=texts.BTN_CANCEL)]],
        resize_keyboard=True,
    )
