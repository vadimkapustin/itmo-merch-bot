"""Настройки бота.

Все секреты (токен бота, id администратора, адрес сайта) лежат в файле .env,
а не в коде. Так их не увидят другие люди, когда вы выложите проект на GitHub.
"""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Папка, в которой лежит этот файл (корень проекта).
BASE_DIR = Path(__file__).resolve().parent

# Читаем переменные из файла .env в окружение программы.
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Config:
    """Все настройки бота в одном месте.

    frozen=True значит, что после создания настройки нельзя случайно изменить.
    """

    bot_token: str       # токен от @BotFather
    admin_id: int        # Telegram id администратора (кому идут обращения)
    webapp_url: str      # адрес сайта-каталога на GitHub Pages
    db_path: Path        # файл базы данных SQLite
    products_file: Path  # файл с товарами (его читают и бот, и сайт)


def load_config() -> Config:
    """Читает настройки из .env и проверяет, что всё заполнено.

    Returns:
        Готовый объект Config.

    Raises:
        RuntimeError: если в .env чего-то не хватает.
    """
    token = os.getenv("BOT_TOKEN")
    admin_id = os.getenv("ADMIN_ID")
    webapp_url = os.getenv("WEBAPP_URL")

    if not token or not admin_id or not webapp_url:
        raise RuntimeError(
            "Заполните BOT_TOKEN, ADMIN_ID и WEBAPP_URL в файле .env "
            "(образец в .env.example)"
        )

    return Config(
        bot_token=token,
        admin_id=int(admin_id),
        webapp_url=webapp_url,
        db_path=BASE_DIR / "shop.db",
        products_file=BASE_DIR / "webapp" / "products.json",
    )
