"""Точка входа: отсюда запускается бот.

Запуск:  python main.py
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.handlers import get_routers
from config import load_config
from database import OrderRepository, ProductRepository, SupportRepository


async def main() -> None:
    """Готовит базу данных, создаёт бота и запускает его."""
    # Логи: в консоли будет видно, что происходит с ботом.
    logging.basicConfig(level=logging.INFO)
    config = load_config()

    # 1. База данных: создаём таблицы и загружаем товары.
    products = ProductRepository(config.db_path)
    orders = OrderRepository(config.db_path)
    support = SupportRepository(config.db_path)
    for repository in (products, orders, support):
        await repository.create_table()
    await products.load_from_json(config.products_file)

    # 2. Сам бот. parse_mode=HTML — можно писать <b>жирный</b> в сообщениях.
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # 3. Диспетчер раздаёт сообщения обработчикам.
    # Всё, что передано сюда (config, products...), aiogram сам подставит
    # в обработчики, у которых есть параметр с таким именем.
    dispatcher = Dispatcher(
        config=config, products=products, orders=orders, support=support
    )
    dispatcher.include_routers(*get_routers())

    # 4. Polling: бот постоянно спрашивает Telegram «есть новые сообщения?»
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
