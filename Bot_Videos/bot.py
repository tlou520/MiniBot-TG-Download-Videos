from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from parser import Parser
import os

class Bot:
    def __init__(self, token: str):
        self.token = token
        self.app = ApplicationBuilder().token(self.token).build()

        # Add handlers here, for example:
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.on_update_received))

        #My functions
        self.parser = Parser()  # instantiate your parser


    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Hello! I am your bot.")

    async def on_update_received(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_message = update.message.text
        video_path = self.parser.process(user_message)

        if video_path and os.path.exists(video_path):
            with open(video_path, 'rb') as video_file:
                await update.message.reply_video(video=InputFile(video_file))
                await update.message.reply_text("On my way!")
        else:
            await update.message.reply_text("Not a valid link or failed to download.")

        
        self.clear_downloads_folder()


    def clear_downloads_folder(self, folder_path='downloads'):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    def run(self):
        self.app.run_polling()

    def get_bot_token(self):
        return self.token
