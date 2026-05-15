import logging
import base64
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ============================
# НАСТРОЙКИ
# ============================
BOT_TOKEN = "6903947493:AAEKPqpglr4WHxcREAJYcE554JVGeQOqF-0"
GEMINI_API_KEY = "AIzaSyDXBCp5UINXDeu8HLr9UOYRHcB9eo0m6tU"

# Исправленный URL (убрано двойное "gemini-" и исправлено название модели)
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-3.1-flash-image-preview:generateContent"
    f"?key={GEMINI_API_KEY}"
)

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================
# КОМАНДЫ БОТА
# ============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я генерирую изображения по описанию.\n\n"
        "Просто напиши мне, что нарисовать.\n\n"
        "Например: космический кот в неоновом городе"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Советы для хорошего результата:\n"
        "• Добавляй стиль: digital art, anime, photorealistic\n"
        "• Указывай детали: освещение, время суток, окружение"
    )

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text.strip()
    user = update.message.from_user.first_name

    logger.info(f"Запрос от {user}: {prompt}")
    status_msg = await update.message.reply_text("⏳ Генерирую изображение...")

    try:
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"]
            }
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(GEMINI_URL, json=payload)
            data = response.json()

        if not response.is_success:
            error_msg = data.get("error", {}).get("message", "Неизвестная ошибка")
            await status_msg.edit_text(f"❌ Ошибка API: {error_msg}")
            return

        # Ищем изображение в ответе
        candidates = data.get("candidates", [{}])
        parts = candidates[0].get("content", {}).get("parts", [])
        image_part = next((p for p in parts if "inlineData" in p), None)

        if not image_part:
            await status_msg.edit_text(
                "⚠️ Изображение не создано. Попробуй изменить описание."
            )
            return

        # Декодируем и отправляем
        image_bytes = base64.b64decode(image_part["inlineData"]["data"])
        await status_msg.delete()
        await update.message.reply_photo(
            photo=image_bytes,
            caption=f"✦ {prompt}"
        )

    except httpx.TimeoutException:
        await status_msg.edit_text("⏱ Время ожидания вышло. Попробуй еще раз.")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await status_msg.edit_text("❌ Произошла ошибка. Проверь логи в Render.")

# ============================
# ЗАПУСК
# ============================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_image))

    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
