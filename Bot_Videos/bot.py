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

        # Step 1: Ask for download option
        if user_message.lower().startswith("http"):
            context.user_data["video_url"] = user_message
            await update.message.reply_text(
                "Choose an option:\n1. Download full video\n2. Download segment (provide timestamps in HH:MM:SS-HH:MM:SS format)"
            )
            return

        # Step 2: Handle option selection
        if user_message.strip() == "1":
            video_url = context.user_data.get("video_url")
            if not video_url:
                await update.message.reply_text("Please send a video link first.")
                return

            video_path = self.parser.process(video_url)
            if video_path and os.path.exists(video_path):
                with open(video_path, 'rb') as video_file:
                    await update.message.reply_video(video=InputFile(video_file))
                    await update.message.reply_text("On my way!")
            else:
                await update.message.reply_text("Not a valid link or failed to download.")
            self.clear_downloads_folder()
            return

        if user_message.strip() == "2":
            await update.message.reply_text("Send the timestamps in format: HH:MM:SS-HH:MM:SS")
            context.user_data["awaiting_timestamps"] = True
            return

        # Step 3: Handle timestamps input (option 2)
        if context.user_data.get("awaiting_timestamps"):
            timestamps = user_message.strip()
            video_url = context.user_data.get("video_url")
            if not video_url:
                await update.message.reply_text("Please send a video link first.")
                return

            # Placeholder for segment logic
            await update.message.reply_text(f"Processing segment for {timestamps}... (logic not yet implemented)")
            context.user_data["awaiting_timestamps"] = False
            self.clear_downloads_folder()
            return

        await update.message.reply_text("Invalid input. Please send a video link.")


    def clear_downloads_folder(self, folder_path='downloads'):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    def run(self):
        self.app.run_polling()

    def get_bot_token(self):
        return self.token
