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
                "Choose an option:\n1. Download full video\n2. Download segments of a video"
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
            await update.message.reply_text("How many seconds do you want to extract from each segment?")
            context.user_data["awaiting_segment_duration"] = True
            return

        if context.user_data.get("awaiting_segment_duration"):
            try:
                duration_seconds = int(user_message.strip())
                context.user_data["duration_seconds"] = duration_seconds
                context.user_data["segments"] = []
                context.user_data["awaiting_segment_duration"] = False
                context.user_data["awaiting_segment_timestamps"] = True
                await update.message.reply_text("Send the start times for each segment in HH:MM:SS format. Type 'done' when finished.")
            except ValueError:
                await update.message.reply_text("Please enter a valid number of seconds.")
            return


        # Step 3: Handle timestamps input (option 2)
        if context.user_data.get("awaiting_segment_timestamps"):
            timestamp = user_message.strip()
            if timestamp.lower() == "done":
                segments = context.user_data.get("segments", [])
                duration = context.user_data.get("duration_seconds", 0)
                if not segments:
                    await update.message.reply_text("No segments received.")
                    return
                # Placeholder for actual processing
                await update.message.reply_text(f"Processing {len(segments)} segments of {duration} seconds each...")
                # Logic to cut the segments of the video
                video_url = context.user_data["video_url"]
                video_path = self.parser.process(video_url)
                segments_videos_paths = self.parser.cut_segments(duration, segments, video_path)
                for segment_path in segments_videos_paths:
                    if segment_path and os.path.exists(segment_path):
                        with open(segment_path, "rb") as video_file:
                            await update.message.reply_video(video=InputFile(video_file))
                context.user_data["awaiting_segment_timestamps"] = False
                return
            # Validate basic HH:MM:SS format (optional: use regex for stricter validation)
            if len(timestamp.split(":")) == 3:
                context.user_data["segments"].append(timestamp)
                await update.message.reply_text("Segment added. Send another or type 'done' to finish.")
            else:
                await update.message.reply_text("Invalid format. Please use HH:MM:SS.")
            return



    def clear_downloads_folder(self, folder_path='downloads'):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    def run(self):
        self.app.run_polling()

    def get_bot_token(self):
        return self.token
