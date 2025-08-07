import os
from bot import Bot
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise Exception("Bot token not found in .env file!")

if __name__ == "__main__":
    bot = Bot(TOKEN)  # Replace with your actual bot token
    bot.run()
