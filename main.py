import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SYSTEM_PROMPT = """You are EZA AI Business Assistant.
Help Telegram users with business ideas, customer support, marketing, product descriptions,
translations, sales copy, and general questions. Be concise, useful and professional.
If asked for financial/legal/medical advice, clearly state that professional advice may be needed.
Reply in the same language as the user when practical, including Amharic."""

async def ai_reply(text: str) -> str:
    # OpenAI first, Gemini fallback.
    if OPENAI_API_KEY:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            r = await client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
            )
            return r.choices[0].message.content.strip()
        except Exception as e:
            print("OpenAI error:", e)

    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(
                os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
                system_instruction=SYSTEM_PROMPT
            )
            r = await asyncio.to_thread(model.generate_content, text)
            return r.text.strip()
        except Exception as e:
            print("Gemini error:", e)

    return "AI is not configured yet. Please add OPENAI_API_KEY or GEMINI_API_KEY in Render Environment Variables."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to EZA AI Business Assistant!\n\n"
        "🤖 Ask me business, marketing, customer-support or general questions.\n"
        "💡 In a group, reply to my message or use /ask your question."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n"
        "/start - Start the bot\n"
        "/ask <question> - Ask AI\n"
        "/help - Show help\n\n"
        "In groups, mention @your_bot or reply to the bot to get an AI answer."
    )

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Example: /ask Give me 5 business ideas for Ethiopia")
        return
    await update.message.chat.send_action("typing")
    answer = await ai_reply(text)
    await update.message.reply_text(answer)

async def group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    bot = await context.bot.get_me()
    mentioned = f"@{bot.username.lower()}" in text.lower() if bot.username else False
    replied_to_bot = (
        update.message.reply_to_message
        and update.message.reply_to_message.from_user
        and update.message.reply_to_message.from_user.id == bot.id
    )

    if not mentioned and not replied_to_bot:
        return

    cleaned = text.replace(f"@{bot.username}", "").strip() if bot.username else text
    if not cleaned:
        cleaned = "Hello! How can you help me?"
    await update.message.chat.send_action("typing")
    answer = await ai_reply(cleaned)
    await update.message.reply_text(answer)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print("Telegram error:", context.error)

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing. Add it to Render Environment Variables.")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, group_message))
    app.add_error_handler(error_handler)

    print("EZA AI Business Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
