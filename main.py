import os, logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Add it in Render Environment Variables.")
client = OpenAI(api_key=KEY) if KEY else None

MENU = [
    ["🤖 Business Assistant", "✍️ Writing & Ads"],
    ["🌐 Translation", "💡 Business Ideas"],
    ["📄 CV & Documents", "💬 Ask AI"],
    ["💰 My Credits", "💳 Buy Credits"],
    ["🎁 Earn Credits", "📊 My Jobs"],
    ["⚙️ Settings", "🆘 Support"],
]
kb = lambda: ReplyKeyboardMarkup(MENU, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 EZA AI Business Bot\n\nእንኳን ደህና መጡ!\nከታች ካሉት Shortcut Buttons አንዱን ይምረጡ።",
        reply_markup=kb())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("የሚገኙ አገልግሎቶች፦\nBusiness • Writing • Translation • CV • AI • Credits • Support", reply_markup=kb())

async def ask_ai(text):
    if not client:
        return "⚠️ OPENAI_API_KEY አልተገኘም። Render Environment Variables ውስጥ ያስገቡ።"
    try:
        r = client.responses.create(
            model=MODEL,
            instructions="You are EZA AI Business Assistant. Support Amharic and English. Give practical, concise business help and writing/translation assistance.",
            input=text)
        return r.output_text
    except Exception:
        logging.exception("AI request failed")
        return "⚠️ AI ጊዜያዊ ችግር አጋጥሞታል። እባክዎ በኋላ ይሞክሩ።"

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    canned = {
      "🤖 Business Assistant":"💼 የንግድ ጥያቄዎን ይጻፉ።",
      "✍️ Writing & Ads":"✍️ ማስታወቂያ፣ Facebook/Telegram post ወይም የንግድ መግለጫ የሚፈልጉትን ይጻፉ።",
      "🌐 Translation":"🌐 የሚተረጎም ጽሑፍዎን ይላኩ።",
      "💡 Business Ideas":"💡 በጀትዎን እና የንግድ ሀሳብ ፍላጎትዎን ይጻፉ።",
      "📄 CV & Documents":"📄 CV ወይም ደብዳቤ የሚፈልጉትን ይጻፉ።",
      "💬 Ask AI":"💬 ጥያቄዎን በቀጥታ ይጻፉ።",
      "💰 My Credits":"💰 Credits: 0 (የDatabase/Credit system በቀጣይ እትም ይከናወናል።)",
      "💳 Buy Credits":"💳 100=100 ETB | 500=400 ETB | 1000=700 ETB\nPayment verification በAdmin በኩል።",
      "🎁 Earn Credits":"🎁 Referral በመጋራት Credits ያግኙ።",
      "📊 My Jobs":"📊 የቀድሞ ስራዎች በDatabase ይቀመጣሉ (በቀጣይ እትም)።",
      "⚙️ Settings":"⚙️ Settings",
      "🆘 Support":"🆘 Support: @Ahm0710",
    }
    if text in canned:
        await update.message.reply_text(canned[text], reply_markup=kb()); return
    chat = update.effective_chat
    if chat.type in ("group","supergroup"):
        me = await context.bot.get_me()
        mentioned = bool(me.username and f"@{me.username}".lower() in text.lower())
        replied = bool(update.message.reply_to_message and update.message.reply_to_message.from_user and update.message.reply_to_message.from_user.id == me.id)
        if not (mentioned or replied): return
        if me.username: text = text.replace(f"@{me.username}", "").strip()
    await update.message.reply_text(await ask_ai(text), reply_markup=kb() if chat.type=="private" else None)

def build():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
    return app

if __name__ == "__main__":
    build().run_polling(allowed_updates=Update.ALL_TYPES)
