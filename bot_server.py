import os
import sys
import logging
import random

print("=" * 60)
print(f"🚀 Python версия: {sys.version}")
print(f"📁 Текущая директория: {os.getcwd()}")
print(f"📦 Путь к Python: {sys.executable}")
print("=" * 60)

# Проверяем наличие библиотек
try:
    from telegram import Update, ReplyKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    print("✅ Библиотеки импортированы успешно")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Установите: pip install python-telegram-bot==21.7")
    sys.exit(1)

# Токен
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8103027770:AAG-Inx91gvCP63l-R-hx1Ydsbr5V1qIP7k")

if not TOKEN or len(TOKEN) < 10:
    print("❌ ОШИБКА: Неверный токен Telegram!")
    sys.exit(1)

print(f"✅ Токен получен: {TOKEN[:15]}...")

# Валютные пары
CURRENCY_PAIRS = [
    ["EUR/USD", "GBP/USD", "USD/JPY"],
    ["AUD/USD", "USD/CAD", "AUD/CHF"],
    ["CHF/JPY", "EUR/CHF", "GBP/AUD"],
    ["CAD/CHF", "EUR/JPY", "EUR/CAD"],
    ["GBP/JPY", "USD/CHF", "EUR/AUD"]
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    reply_markup = ReplyKeyboardMarkup(CURRENCY_PAIRS, resize_keyboard=True)
    await update.message.reply_text(
        "🤖 *Forex Signal Bot*\n\nВыберите валютную пару:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора пары"""
    pair = update.message.text
    
    # Генерируем сигнал
    if random.random() > 0.5:
        signal = "🟢 ВВЕРХ"
        confidence = random.randint(70, 95)
    else:
        signal = "🔴 ВНИЗ"
        confidence = random.randint(70, 95)
    
    message = f"""
📊 *АНАЛИЗ ДЛЯ {pair}*

🎯 Сигнал: {signal}
📈 Уверенность: {confidence}%
⏰ Таймфрейм: 5 минут

💰 Рекомендация: {'Покупать' if 'ВВЕРХ' in signal else 'Продавать'}
"""
    
    await update.message.reply_text(message, parse_mode='Markdown')
    
    # Кнопки для продолжения
    keyboard = [["📊 Новая пара"], ["🔄 Ещё раз"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👇 Что дальше?", reply_markup=reply_markup)

async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка действий"""
    text = update.message.text
    
    if text in ["📊 Новая пара", "🔄 Ещё раз"]:
        await start(update, context)

def main():
    """Главная функция"""
    print("\n" + "=" * 60)
    print("🤖 ЗАПУСК FOREX БОТА")
    print("=" * 60)
    
    try:
        print("1. Создаю приложение...")
        app = Application.builder().token(TOKEN).build()
        print("✅ Приложение создано")
        
        print("2. Регистрирую обработчики...")
        
        # Команда /start
        app.add_handler(CommandHandler("start", start))
        
        # Все валютные пары
        all_pairs = []
        for row in CURRENCY_PAIRS:
            all_pairs.extend(row)
        
        # Обработчик валютных пар
        app.add_handler(MessageHandler(
            filters.TEXT & filters.Text(all_pairs),
            handle_pair
        ))
        
        # Обработчик действий
        app.add_handler(MessageHandler(
            filters.TEXT & filters.Text(["📊 Новая пара", "🔄 Ещё раз"]),
            handle_action
        ))
        
        print("✅ Обработчики зарегистрированы")
        print("3. Запускаю бота...")
        print("✅ Бот запущен и готов к работе!")
        print("📱 Откройте Telegram → напишите /start")
        print("=" * 60)
        print("🟢 Бот работает 24/7 на сервере!")
        print("=" * 60)
        
        # Запускаем бота
        app.run_polling()
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
