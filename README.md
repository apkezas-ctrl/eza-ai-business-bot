# EZA AI Business Bot

Telegram AI assistant for business groups.

## Features
- AI answers through OpenAI or Gemini
- `/ask` command
- Works in Telegram groups when mentioned or when replying to the bot
- Amharic/English-friendly system prompt
- Designed for Render deployment

## Render Environment Variables
Required:
- `BOT_TOKEN`

Choose at least one AI provider:
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`

Optional:
- `OPENAI_MODEL` (default: `gpt-4o-mini`)
- `GEMINI_MODEL` (default: `gemini-1.5-flash`)

Never put API keys in GitHub files.
