# 🛍 ITMO Merch Bot

Telegram-бот — магазин мерча Университета ИТМО со встроенным сайтом-каталогом
(Telegram Mini App) и оплатой звёздами Telegram ⭐.

## Что умеет

| Кнопка | Что происходит |
|---|---|
| 🛒 Сделать заказ | Открывает внутри Telegram сайт-каталог: карточки товаров, корзина, оплата |
| 📦 Мои заказы | Количество оплаченных заказов и их состав |
| ℹ️ Информация | Сведения о магазине, где и когда забрать заказ |
| 🆘 Техподдержка | Сообщение уходит администратору, его ответ приходит пользователю |

Команды администратора: ответ (reply) на обращение — ответ пользователю;
`/refund <номер>` — вернуть звёзды за заказ.

## Как это работает

```
Пользователь → кнопка «Сделать заказ» → сайт (GitHub Pages)
    → корзина → «Оплатить» → sendData → бот
    → бот проверяет цены по базе → счёт в звёздах → оплата
    → заказ сохранён в SQLite → «Мои заказы»
```

## Технологии

Python 3.10+, [aiogram 3](https://docs.aiogram.dev/), SQLite (aiosqlite),
HTML/CSS/JavaScript + Telegram WebApp API, GitHub Pages, Doxygen.

## Структура проекта

```
itmo-merch-bot/
├── main.py                 # точка входа — запуск бота
├── config.py               # настройки из файла .env
├── bot/
│   ├── texts.py            # все тексты и надписи на кнопках
│   ├── keyboards.py        # клавиатуры
│   ├── filters.py          # фильтр IsAdmin
│   ├── states.py           # состояния (режим «пишу в поддержку»)
│   ├── utils.py            # вспомогательные функции
│   └── handlers/           # обработчики: common, shop, support, admin
├── database/
│   ├── base.py             # BaseRepository — родительский класс
│   ├── models.py           # Product, Order, OrderItem
│   └── repositories.py     # репозитории товаров, заказов, обращений
├── webapp/                 # сайт-каталог (публикуется на GitHub Pages)
│   ├── index.html, style.css, app.js
│   ├── products.json       # список товаров (общий для сайта и бота)
│   └── images/
└── .github/workflows/pages.yml  # автопубликация сайта
```

## Запуск

1. **Создайте бота** у [@BotFather](https://t.me/BotFather) командой `/newbot`
   и сохраните токен.
2. **Опубликуйте сайт.** Загрузите проект на GitHub, откройте
   *Settings → Pages → Source* и выберите **GitHub Actions**.
   Через минуту сайт будет доступен по адресу
   `https://<логин>.github.io/<репозиторий>/`.
3. **Установите зависимости:**
   ```bash
   python -m venv venv
   venv\Scripts\activate          # Windows  (Linux/macOS: source venv/bin/activate)
   pip install -r requirements.txt
   ```
4. **Заполните настройки:** скопируйте `.env.example` в `.env` и впишите
   токен, свой Telegram id (узнать у [@userinfobot](https://t.me/userinfobot))
   и адрес сайта.
5. **Запустите:** `python main.py` и отправьте боту `/start`.

## Документация

- Подробное описание — в [WIKI.md](WIKI.md) (этот текст размещён на wiki-странице).
- Документация по коду: `doxygen Doxyfile`, затем откройте
  `doxygen_docs/html/index.html`.
