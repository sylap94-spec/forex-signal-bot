import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import random
import time

# Настройка для сервера: токен берется из переменных окружения
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8103027770:AAG-Inx91gvCP63l-R-hx1Ydsbr5V1qIP7k")

# Уменьшаем логирование для сервера
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

# Таймфреймы (экспирации)
TIMEFRAMES = [
    ["1 мин", "5 мин"],
    ["10 мин", "15 мин"],
    ["🔙 Назад"]
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - показывает все валютные пары"""
    context.user_data.clear()
    
    reply_markup = ReplyKeyboardMarkup(CURRENCY_PAIRS, resize_keyboard=True, one_time_keyboard=False)
    
    welcome_text = """
🎯 *ВЫБЕРИТЕ ВАЛЮТНУЮ ПАРУ*
📊 *Доступные пары (14)*
👇 *Выберите пару из кнопок ниже*
    """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

async def handle_pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора валютной пары"""
    pair = update.message.text
    
    if pair == "🔙 Назад":
        await start(update, context)
        return
    
    if pair == "❌ Закрыть":
        await update.message.reply_text("❌ Клавиатура закрыта.\n\nЧтобы открыть снова, напишите /start")
        return
    
    context.user_data['selected_pair'] = pair
    
    reply_markup = ReplyKeyboardMarkup(TIMEFRAMES, resize_keyboard=True, one_time_keyboard=False)
    
    await update.message.reply_text(
        f"✅ Выбрана пара: *{pair}*\n\n⏰ *Теперь выберите таймфрейм:*",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_timeframe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора таймфрейма"""
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
    
    context.user_data['selected_timeframe'] = timeframe
    
    await update.message.reply_text(f"⏳ *Анализирую {pair} на {timeframe}...*", parse_mode='Markdown')
    
    # Имитация анализа
    signal_data = generate_signal_with_timeframe(pair, timeframe)
    result_text = format_signal_result(pair, timeframe, signal_data)
    
    await update.message.reply_text(result_text, parse_mode='Markdown')
    
    action_keyboard = [
        ["📊 Новая пара", f"🔄 {pair}"],
        ["📋 Главное меню", f"⏰ Сменить таймфрейм"]
    ]
    action_markup = ReplyKeyboardMarkup(action_keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "👇 *Что дальше?*",
        parse_mode='Markdown',
        reply_markup=action_markup
    )

def generate_signal_with_timeframe(pair, timeframe):
    """Генерация сигнала с учетом таймфрейма"""
    timeframe_params = {
        "1 мин": {"base_confidence": 60, "volatility": "Высокая", "risk": "Высокий"},
        "5 мин": {"base_confidence": 70, "volatility": "Средняя", "risk": "Средний"},
        "10 мин": {"base_confidence": 75, "volatility": "Средняя", "risk": "Средний"},
        "15 мин": {"base_confidence": 80, "volatility": "Низкая", "risk": "Низкий"}
    }
    
    params = timeframe_params.get(timeframe, timeframe_params["5 мин"])
    
    if random.random() > 0.5:
        signal = "🟢 ВВЕРХ"
        direction = "BUY"
        confidence = params["base_confidence"] + random.randint(0, 15)
    else:
        signal = "🔴 ВНИЗ"
        direction = "SELL"
        confidence = params["base_confidence"] + random.randint(0, 10)
    
    confidence = min(confidence, 95)
    
    if confidence > 85:
        recommendation = "Сильная рекомендация"
    elif confidence > 70:
        recommendation = "Рекомендация"
    else:
        recommendation = "Слабая рекомендация"
    
    base_prices = {
        "EUR/USD": 1.0850, "GBP/USD": 1.2650, "USD/JPY": 150.50,
        "AUD/USD": 0.6550, "USD/CAD": 1.3550, "AUD/CHF": 0.5850,
        "CHF/JPY": 170.50, "EUR/CHF": 0.9550, "GBP/AUD": 1.9250,
        "CAD/CHF": 0.6650, "EUR/JPY": 163.50, "EUR/CAD": 1.4650,
        "GBP/JPY": 190.50, "USD/CHF": 0.8850, "EUR/AUD": 1.6550
    }
    
    base_price = base_prices.get(pair, 1.0000)
    current_price = base_price * (1 + random.uniform(-0.002, 0.002))
    
    return {
        "signal": signal,
        "direction": direction,
        "confidence": confidence,
        "recommendation": recommendation,
        "price": current_price,
        "volatility": params["volatility"],
        "risk": params["risk"]
    }

def format_signal_result(pair, timeframe, signal_data):
    """Форматирование результата сигнала"""
    if signal_data["confidence"] > 85:
        conf_emoji = "🎯"
    elif signal_data["confidence"] > 70:
        conf_emoji = "📊"
    else:
        conf_emoji = "⚠️"
    
    if "Сильная" in signal_data["recommendation"]:
        rec_emoji = "💪"
    elif "Рекомендация" in signal_data["recommendation"]:
        rec_emoji = "👍"
    else:
        rec_emoji = "👀"
    
    return f"""
{conf_emoji} *АНАЛИЗ ЗАВЕРШЕН*

📊 *Пара:* {pair}
⏰ *Таймфрейм:* {timeframe}
💰 *Цена:* {signal_data['price']:.5f}

🎯 *СИГНАЛ:* {signal_data['signal']}
{rec_emoji} *Рекомендация:* {signal_data['recommendation']}
📈 *Уверенность:* {signal_data['confidence']}%

⚠️ *ВАЖНО:* Это автоматический анализ.
    """

async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка дополнительных действий"""
    text = update.message.text
    
    if text in ["📊 Новая пара", "📋 Главное меню"]:
        await start(update, context)
    elif text == "⏰ Сменить таймфрейм":
        pair = context.user_data.get('selected_pair', 'EUR/USD')
        reply_markup = ReplyKeyboardMarkup(TIMEFRAMES, resize_keyboard=True)
        await update.message.reply_text(
            f"✅ Текущая пара: *{pair}*\n\n⏰ *Выберите новый таймфрейм:*",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
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
    """Главная функция для сервера"""
    print("🚀 Запуск Forex бота на сервере...")
    
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
    action_buttons = ["📊 Новая пара", "📋 Главное меню", "⏰ Сменить таймфрейм"]
    
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