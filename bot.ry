**import logging**

**import base64**

**import httpx**

**from telegram import Update**

**from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes**



**# ============================**

**BOT\_TOKEN = "6903947493:AAEKPqpglr4WHxcREAJYcE554JVGeQOqF-0"**

**GEMINI\_API\_KEY = "AIzaSyDXBCp5UINXDeu8HLr9UOYRHcB9eo0m6tU"**

**# ============================**



**GEMINI\_URL = (**

&#x20;   **"https://generativelanguage.googleapis.com/v1beta/models/"**

&#x20;   **"gemini-2.0-flash-preview-image-generation:generateContent"**

&#x20;   **f"?key={GEMINI\_API\_KEY}"**

**)**



**logging.basicConfig(**

&#x20;   **format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",**

&#x20;   **level=logging.INFO**

**)**

**logger = logging.getLogger(\_\_name\_\_)**





**async def start(update: Update, context: ContextTypes.DEFAULT\_TYPE):**

&#x20;   **await update.message.reply\_text(**

&#x20;       **"👋 Привет! Я генерирую изображения по описанию.\\n\\n"**

&#x20;       **"Просто напиши мне что нарисовать — на русском или английском.\\n\\n"**

&#x20;       **"Например:\\n"**

&#x20;       **"• космический кот в неоновом городе\\n"**

&#x20;       **"• девушка-самурай под сакурой, digital art\\n"**

&#x20;       **"• заброшенный замок в туманном лесу"**

&#x20;   **)**





**async def help\_command(update: Update, context: ContextTypes.DEFAULT\_TYPE):**

&#x20;   **await update.message.reply\_text(**

&#x20;       **"ℹ️ Просто напиши описание картинки — и я её сгенерирую.\\n\\n"**

&#x20;       **"Советы для хорошего результата:\\n"**

&#x20;       **"• Добавь стиль: digital art, anime, photorealistic, oil painting\\n"**

&#x20;       **"• Укажи настроение: dark, vibrant, cinematic, dreamy\\n"**

&#x20;       **"• Опиши детали: освещение, время суток, окружение"**

&#x20;   **)**





**async def generate\_image(update: Update, context: ContextTypes.DEFAULT\_TYPE):**

&#x20;   **prompt = update.message.text.strip()**

&#x20;   **user = update.message.from\_user.first\_name**



&#x20;   **logger.info(f"Запрос от {user}: {prompt}")**



&#x20;   **status\_msg = await update.message.reply\_text("⏳ Генерирую изображение...")**



&#x20;   **try:**

&#x20;       **payload = {**

&#x20;           **"contents": \[{**

&#x20;               **"parts": \[{"text": prompt}]**

&#x20;           **}],**

&#x20;           **"generationConfig": {**

&#x20;               **"responseModalities": \["TEXT", "IMAGE"]**

&#x20;           **}**

&#x20;       **}**



&#x20;       **async with httpx.AsyncClient(timeout=60) as client:**

&#x20;           **response = await client.post(GEMINI\_URL, json=payload)**

&#x20;           **data = response.json()**



&#x20;       **if not response.is\_success:**

&#x20;           **error\_msg = data.get("error", {}).get("message", "Неизвестная ошибка")**

&#x20;           **await status\_msg.edit\_text(f"❌ Ошибка API: {error\_msg}")**

&#x20;           **return**



&#x20;       **parts = data.get("candidates", \[{}])\[0].get("content", {}).get("parts", \[])**

&#x20;       **image\_part = next((p for p in parts if "inlineData" in p), None)**



&#x20;       **if not image\_part:**

&#x20;           **await status\_msg.edit\_text(**

&#x20;               **"⚠️ Изображение не было сгенерировано.\\n"**

&#x20;               **"Попробуй другой промпт или добавь больше деталей."**

&#x20;           **)**

&#x20;           **return**



&#x20;       **image\_bytes = base64.b64decode(image\_part\["inlineData"]\["data"])**



&#x20;       **await status\_msg.delete()**

&#x20;       **await update.message.reply\_photo(**

&#x20;           **photo=image\_bytes,**

&#x20;           **caption=f"✦ {prompt}"**

&#x20;       **)**



&#x20;   **except httpx.TimeoutException:**

&#x20;       **await status\_msg.edit\_text("⏱ Превышено время ожидания. Попробуй ещё раз.")**

&#x20;   **except Exception as e:**

&#x20;       **logger.error(f"Ошибка: {e}")**

&#x20;       **await status\_msg.edit\_text("❌ Что-то пошло не так. Попробуй ещё раз.")**





**def main():**

&#x20;   **app = Application.builder().token(BOT\_TOKEN).build()**



&#x20;   **app.add\_handler(CommandHandler("start", start))**

&#x20;   **app.add\_handler(CommandHandler("help", help\_command))**

&#x20;   **app.add\_handler(MessageHandler(filters.TEXT \& \~filters.COMMAND, generate\_image))**



&#x20;   **logger.info("Бот запущен. Нажми Ctrl+C для остановки.")**

&#x20;   **app.run\_polling()**





**if \_\_name\_\_ == "\_\_main\_\_":**

&#x20;   **main()**

