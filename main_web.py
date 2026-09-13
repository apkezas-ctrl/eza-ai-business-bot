import os
from fastapi import FastAPI, Request
from main import build, TOKEN
app = FastAPI()
bot = build()

@app.on_event("startup")
async def startup():
    await bot.initialize()
    await bot.start()
    url = os.getenv("WEBHOOK_URL", "").rstrip("/") + "/telegram/webhook"
    if url.startswith("http"):
        await bot.bot.set_webhook(url=url)

@app.on_event("shutdown")
async def shutdown():
    await bot.stop()
    await bot.shutdown()

@app.get("/")
async def root():
    return {"status":"ok","service":"EZA AI Business Bot"}

@app.post("/telegram/webhook")
async def webhook(request: Request):
    from telegram import Update
    update = Update.de_json(await request.json(), bot.bot)
    await bot.process_update(update)
    return {"ok":True}
