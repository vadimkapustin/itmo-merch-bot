// ============================================================
// Сайт-каталог (Telegram Mini App).
// Показывает товары, хранит корзину и отправляет заказ в бота.
// ============================================================

// Объект Telegram.WebApp даёт доступ к возможностям Telegram:
// большая кнопка внизу (MainButton), кнопка «назад», отправка данных боту.
const tg = window.Telegram.WebApp;
tg.ready();   // сообщаем Telegram, что сайт загрузился
tg.expand();  // раскрываем сайт на весь экран

// В обычном браузере platform = "unknown", внутри Telegram — "android", "ios", "tdesktop" и т.п.
const insideTelegram = tg.platform !== "unknown";

// Корзина: Map вида {id товара → количество}
const cart = new Map();
let products = [];  // список товаров (загрузим из products.json)

// Ссылки на элементы страницы
const catalogEl = document.getElementById("catalog");
const cartCountEl = document.getElementById("cartCount");
const overlayEl = document.getElementById("overlay");
const sheetEl = document.getElementById("sheet");
const sheetContentEl = document.getElementById("sheetContent");

// ---------- Загрузка товаров ----------
// Тот же файл products.json читает и бот — список товаров в одном месте.
async function loadProducts() {
  const response = await fetch("products.json");
  products = await response.json();
  renderCatalog();
}

// Цена текстом: 0 → «Бесплатно», иначе «5 ⭐»
function priceText(price) {
  return price === 0 ? "Бесплатно" : `${price} ⭐`;
}

// Находит товар по id
function findProduct(id) {
  return products.find((product) => product.id === id);
}

// ---------- Каталог ----------
// Рисует карточку для каждого товара
function renderCatalog() {
  catalogEl.innerHTML = "";
  for (const product of products) {
    const card = document.createElement("button");
    card.className = "card";
    card.innerHTML = `
      <img src="${product.image}" alt="${product.title}" loading="lazy">
      <div class="card-body">
        <div class="card-title">${product.title}</div>
        <div class="card-price">${priceText(product.price)}</div>
      </div>`;
    card.addEventListener("click", () => openProduct(product));
    catalogEl.appendChild(card);
  }
}

// ---------- Всплывающая панель ----------
function openSheet(html) {
  sheetContentEl.innerHTML = html;
  overlayEl.hidden = false;
  sheetEl.hidden = false;
  tg.BackButton.show();  // кнопка «назад» в шапке Telegram закроет панель
}

function closeSheet() {
  overlayEl.hidden = true;
  sheetEl.hidden = true;
  tg.BackButton.hide();
}

// Карточка товара: фото, описание, выбор количества, «В корзину»
function openProduct(product) {
  let qty = 1;
  openSheet(`
    <img src="${product.image}" alt="${product.title}">
    <h2>${product.title}</h2>
    <p>${product.description}</p>
    <div class="row">
      <span class="price-big">${priceText(product.price)}</span>
      <div class="stepper">
        <button id="minus" aria-label="Меньше">−</button>
        <span id="qty">1</span>
        <button id="plus" aria-label="Больше">+</button>
      </div>
    </div>
    <button class="primary" id="addBtn">Добавить в корзину</button>`);

  const qtyEl = document.getElementById("qty");
  document.getElementById("minus").onclick = () => {
    qty = Math.max(1, qty - 1);
    qtyEl.textContent = qty;
  };
  document.getElementById("plus").onclick = () => {
    qty = Math.min(20, qty + 1);
    qtyEl.textContent = qty;
  };
  document.getElementById("addBtn").onclick = () => {
    changeQty(product.id, qty);
    tg.HapticFeedback?.notificationOccurred("success");  // лёгкая вибрация
    closeSheet();
  };
}

// ---------- Корзина ----------
// Меняет количество товара в корзине на delta (+1, -1, +3...)
function changeQty(id, delta) {
  const newQty = Math.min(20, (cart.get(id) || 0) + delta);
  if (newQty <= 0) {
    cart.delete(id);
  } else {
    cart.set(id, newQty);
  }
  updateCartSummary();
}

// Сумма корзины в звёздах
function cartTotal() {
  let total = 0;
  for (const [id, qty] of cart) {
    total += findProduct(id).price * qty;
  }
  return total;
}

// Надпись на кнопке оплаты: если всё бесплатно — «Оформить заказ»
function payButtonText() {
  const total = cartTotal();
  return total === 0 ? "Оформить заказ" : `Оплатить ${total} ⭐`;
}

// Обновляет счётчик на иконке и большую кнопку Telegram внизу
function updateCartSummary() {
  const count = [...cart.values()].reduce((sum, qty) => sum + qty, 0);
  cartCountEl.textContent = count;
  cartCountEl.classList.toggle("empty", count === 0);

  if (count > 0) {
    tg.MainButton.setText(payButtonText());
    tg.MainButton.show();
  } else {
    tg.MainButton.hide();
  }
}

// Окно корзины со списком товаров
function openCart() {
  if (cart.size === 0) {
    openSheet(`<h2>Корзина</h2><p class="empty-cart">Пока пусто. Выберите что-нибудь в каталоге 🙂</p>`);
    return;
  }
  let html = "<h2>Корзина</h2>";
  for (const [id, qty] of cart) {
    const product = findProduct(id);
    html += `
      <div class="cart-item row">
        <div>
          <div class="cart-item-title">${product.title}</div>
          <div>${priceText(product.price * qty)}</div>
        </div>
        <div class="stepper">
          <button data-id="${id}" data-delta="-1" aria-label="Меньше">−</button>
          <span>${qty}</span>
          <button data-id="${id}" data-delta="1" aria-label="Больше">+</button>
        </div>
      </div>`;
  }
  html += `<div class="cart-total">Итого: ${priceText(cartTotal())}</div>
           <button class="primary" id="payBtn">${payButtonText()}</button>`;
  openSheet(html);

  // Кнопки +/- внутри корзины
  sheetContentEl.querySelectorAll("[data-delta]").forEach((button) => {
    button.onclick = () => {
      changeQty(Number(button.dataset.id), Number(button.dataset.delta));
      openCart();  // перерисовываем корзину
    };
  });
  document.getElementById("payBtn").onclick = checkout;
}

// ---------- Оформление заказа ----------
// Отправляет корзину боту. После sendData Telegram сам закроет сайт,
// а бот пришлёт подтверждение заказа.
function checkout() {
  if (cart.size === 0) return;
  const items = [...cart].map(([id, qty]) => ({ id, qty }));
  tg.sendData(JSON.stringify({ items }));
}

// ---------- Подключаем обработчики ----------
document.getElementById("cartBtn").onclick = openCart;
document.getElementById("sheetClose").onclick = closeSheet;
overlayEl.onclick = closeSheet;
tg.BackButton.onClick(closeSheet);
tg.MainButton.onClick(checkout);
document.getElementById("browserHint").hidden = insideTelegram;

loadProducts();
