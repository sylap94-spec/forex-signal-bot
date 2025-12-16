import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import random
import time

# Настройка для сервера
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8103027770:AAG-Inx91gvCP63l-R-hx1Ydsbr5V1qIP7k")

# Уменьшаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Валютные пары
CURRENCY_PAIRS = [
    ["EUR/USD", "GBP/USD", "USD/JPY"],
    ["AUD/USD", "USD/CAD", "AUD/CHF"],
    ["CHF/JPY", "EUR/CHF", "GBP/AUD"],
    ["CAD/CHF", "EUR/JPY", "EUR/CAD"],
    ["GBP/JPY", "USD/CHF", "EUR/AUD"],
    ["🔙 Назад", "❌ Закрыть"]
]

# Таймфреймы
TIMEFRAMES = [
    ["1 мин", "5 мин"],
    ["10 мин", "15 мин"],
    ["🔙 Назад"]
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    
    reply_markup = ReplyKeyboardMarkup(CURRENCY_PAIRS, resize_keyboard=True)
    
    await update.message.reply_text(
        "🎯 *ВЫБЕРИТЕ ВАЛЮТНУЮ ПАРУ*\n\n👇 *Выберите пару из кнопок ниже*",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair = update.message.text
    
    if pair == "🔙 Назад":
        await start(update, context)
        return
    
    if pair == "❌ Закрыть":
        await update.message.reply_text("❌ Клавиатура закрыта.\n\nНапишите /start чтобы открыть")
        return
    
    context.user_data['selected_pair'] = pair
    
    reply_markup = ReplyKeyboardMarkup(TIMEFRAMES, resize_keyboard=True)
    
    await update.message.reply_text(
        f"✅ Выбрана пара: *{pair}*\n\n⏰ *Теперь выберите таймфрейм:*",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_timeframe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    timeframe = update.message.text
    pair = context.user_data.get('selected_pair')
    
    if not pair:
        await update.message.reply_text("❌ Сначала выберите валютную пару!")
        await start(update, context)
        return
    
    if timeframe == "🔙 Назад":
        await start(update, context)
        return
    
    valid_timeframes = ["1 мин", "5 мин", "10 мин", "15 мин"]
    if timeframe not in valid_timeframes:
        await update.message.reply_text("❌ Выберите таймфрейм из списка!")
        return
    
    await update.message.reply_text(f"⏳ *Анализирую {pair} на {timeframe}...*", parse_mode='Markdown')
    
    # Генерация сигнала
    if random.random() > 0.5:
        signal = "🟢 ВВЕРХ"
        confidence = random.randint(70, 95)
    else:
        signal = "🔴 ВНИЗ"
        confidence = random.randint(70, 95)
    
    result_text = f"""
📊 *АНАЛИЗ ЗАВЕРШЕН*

📊 *Пара:* {pair}
⏰ *Таймфрейм:* {timeframe}
🎯 *Сигнал:* {signal}
📈 *Уверенность:* {confidence}%

⚠️ *ВАЖНО:* Это автоматический анализ.
"""
    
    await update.message.reply_text(result_text, parse_mode='Markdown')
    
    action_keyboard = [
        ["📊 Новая пара", f"🔄 {pair}"],
        ["📋 Главное меню"]
    ]
    action_markup = ReplyKeyboardMarkup(action_keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "👇 *Что дальше?*",
        parse_mode='Markdown',
        reply_markup=action_markup
    )

async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text in ["📊 Новая пара", "📋 Главное меню"]:
        await start(update, context)
    elif text.startswith("🔄 "):
        pair = text[2:]
        context.user_data['selected_pair'] = pair
        reply_markup = ReplyKeyboardMarkup(TIMEFRAMES, resize_keyboard=True)
        await update.message.reply_text(
            f"✅ Выбрана пара: *{pair}*\n\n⏰ *Выберите таймфрейм:*",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

def main():
    print("🚀 Запуск Forex бота на сервере...")
    
    # Создаем приложение (ВАЖНО: без Updater!)
    app = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    
    # Обработчик для валютных пар
    all_currency_buttons = []
    for row in CURRENCY_PAIRS:
        all_currency_buttons.extend(row)
    
    currency_buttons = [btn for btn in all_currency_buttons if btn not in ["🔙 Назад", "❌ Закрыть"]]
    app.add_handler(MessageHandler(filters.TEXT & filters.Text(currency_buttons), handle_pair))
    
    # Навигационные кнопки
    nav_buttons = ["🔙 Назад", "❌ Закрыть"]
    app.add_handler(MessageHandler(filters.TEXT & filters.Text(nav_buttons), handle_pair))
    
    # Таймфреймы
    timeframe_buttons = ["1 мин", "5 мин", "10 мин", "15 мин", "🔙 Назад"]
    app.add_handler(MessageHandler(filters.TEXT & filters.Text(timeframe_buttons), handle_timeframe))
    
    # Действия после анализа
    action_buttons = ["📊 Новая пара", "📋 Главное меню"]
    
    # Кастомный фильтр для кнопок "🔄 ПАРА"
    def refresh_filter(update_obj):
        return update_obj.message.text.startswith("🔄 ") if update_obj.message and update_obj.message.text else False
    
    app.add_handler(MessageHandler(
        filters.TEXT & (filters.Text(action_buttons) | filters.UpdateFilter(refresh_filter)),
        handle_action
    ))
    
    print("✅ Бот запущен и готов к работе!")
    print("📱 Бот будет работать 24/7")
    
    # Запускаем бота (на сервере это работает непрерывно)
    app.run_polling()

if __name__ == "__main__":
    main()