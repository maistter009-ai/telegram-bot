import logging
import base64
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ============================
BOT_TOKEN = "6903947493:AAEKPqpglr4WHxcREAJYcE554JVGeQOqF-0"
GEMINI_API_KEY = "AIzaSyDXBCp5UINXDeu8HLr9UOYRHcB9eo0m6tU"
# ============================

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-gemini-3.1-flash-image-preview:generateContent"
    f"?key={GEMINI_API_KEY}"
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я генерирую изображения по описанию.\n\n"
        "Просто напиши мне что нарисовать — на русском или английском.\n\n"
        "Например:\n"
        "• космический кот в неоновом городе\n"
        "• девушка-самурай под сакурой, digital art\n"
        "• заброшенный замок в туманном лесу"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Просто напиши описание картинки — и я её сгенерирую.\n\n"
        "Советы для хорошего результата:\n"
        "• Добавь стиль: digital art, anime, photorealistic, oil painting\n"
        "• Укажи настроение: dark, vibrant, cinematic, dreamy\n"
        "• Опиши детали: освещение, время суток, окружение"
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

        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        image_part = next((p for p in parts if "inlineData" in p), None)

        if not image_part:
            await status_msg.edit_text(
                "⚠️ Изображение не было сгенерировано.\n"
                "Попробуй другой промпт или добавь больше деталей."
            )
            return

        image_bytes = base64.b64decode(image_part["inlineData"]["data"])

        await status_msg.delete()
        await update.message.reply_photo(
            photo=image_bytes,
            caption=f"✦ {prompt}"
        )

    except httpx.TimeoutException:
        await status_msg.edit_text("⏱ Превышено время ожидания. Попробуй ещё раз.")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await status_msg.edit_text("❌ Что-то пошло не так. Попробуй ещё раз.")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_image))

    logger.info("Бот запущен. Нажми Ctrl+C для остановки.")
    app.run_polling()


if __name__ == "__main__":
    main()
