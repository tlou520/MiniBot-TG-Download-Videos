import yt_dlp
import instaloader
import re
import os
import subprocess


class Parser:
    def process(self, message: str) -> str:
        return self.checker(message)

    def checker(self, message: str) -> str:
        handlers = {
            "youtube.com": self.youtube,
            "youtu.be": self.youtube,
            "instagram.com": self.instagram,
            "tiktok.com": self.tiktok,
        }

        for key, handler in handlers.items():
            if key in message:
                return handler(message)

        return None

    def cut_segments(self, duration: int, segments: list[str], video_path: str) -> list[str]:
        output_files = []
        base_name, ext = os.path.splitext(video_path)

        for idx, start_time in enumerate(segments):
            output_path = f"{base_name}_part{idx+1}{ext}"
            output_files.append(output_path)

            cmd = [
                "ffmpeg",
                "-y",                  # overwrite without asking
                "-ss", start_time,     # start time in HH:MM:SS
                "-i", video_path,
                "-t", str(duration),   # duration in seconds
                "-c", "copy",          # no re-encoding
                output_path
            ]
            subprocess.run(cmd, check=True)

        return output_files

        

    def youtube(self, url: str) -> str:
        output_path = "downloads/%(title)s.%(ext)s"
        ydl_opts = {
            'outtmpl': output_path,
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',  # Ensures final file is in mp4 format
            'quiet': True,
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
            return filepath

    def instagram(self, url: str) -> str:
        # Extract shortcode from URL
        pattern = r"instagram\.com/(?:[^/]+/)?(?:reel|p)/([A-Za-z0-9_-]+)/?"
        
        match = re.search(pattern, url)
        if not match:
            raise ValueError("Invalid reel URL")
        shortcode = match.group(1)

        # Initialize Instaloader
        L = instaloader.Instaloader(
                download_pictures=False,       # Do not download photos (jpg)
                download_videos=True,          # Download videos (mp4)
                download_geotags=False,
                download_comments=False,
                save_metadata=False,            # Do not save metadata json.xz files
                post_metadata_txt_pattern=None
        )
        # Set filename pattern
        L.filename_pattern = "{shortcode}"

        # Optional login if needed
        # L.login('your_username', 'your_password')

        # Get the Post object
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        # Specify the target folder
        target_folder = 'downloads'

        # Download the post (just video)
        L.download_post(post, target=target_folder)

        # Construct the expected filename
        # Instaloader saves videos with filenames like {target_folder}/{shortcode}_{timestamp}.mp4
        for filename in os.listdir(target_folder):
            if filename.startswith(shortcode) and filename.endswith('.mp4'):
                video_path = os.path.join(target_folder, filename)
                print("Downloaded video path:", video_path)
                return video_path
                break
        pass

    def tiktok(self, url: str) -> str:
        output_path = "downloads/%(title)s.%(ext)s"
        ydl_opts = {
            'outtmpl': output_path,
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',  # Ensures final file is in mp4 format
            'quiet': True,
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
            return filepath
        pass
