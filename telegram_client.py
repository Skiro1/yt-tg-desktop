import asyncio
from pyrogram import Client
from pyrogram.enums import ParseMode

from settings_manager import get_runtime_path


class TelegramClient:
    """User Client for sending video to Saved Messages."""

    def __init__(self, api_id: int, api_hash: str, session_name: str = "yt_tg_session"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = get_runtime_path(session_name)
        self.connected = False
        self.last_error = ""

    async def connect(self):
        """
        Connects to Telegram to verify authorization.
        On first run, will ask in console:
        - Phone number
        - Confirmation code
        - 2FA password (if enabled)
        """
        if self.connected:
            return True

        client = None
        try:
            client = Client(
                self.session_name,
                api_id=self.api_id,
                api_hash=self.api_hash
            )

            await client.start()
            self.connected = True
            self.last_error = ""
            print("[OK] Successfully connected to Telegram!")
            return True

        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
            self.connected = False
            self.last_error = str(e)
            return False
        finally:
            if client:
                await client.stop()

    def disconnect(self):
        """Disconnects from Telegram."""
        self.connected = False
        print("[INFO] Disconnected from Telegram.")

    async def send_video(self, video_path: str, caption: str, thumb_path: str = None,
                         duration: int = 0, width: int = 1920, height: int = 1080):
        """
        Sends video to Saved Messages with full metadata.
        
        Args:
            video_path: Path to video file
            caption: HTML-formatted caption
            thumb_path: Path to thumbnail (optional)
            duration: Video duration in seconds
            width: Video width
            height: Video height
        
        Returns:
            bool: Success status
        """
        client = None
        try:
            print("[INFO] Sending video to Saved Messages...")

            # Create new client with existing session
            client = Client(
                self.session_name,
                api_id=self.api_id,
                api_hash=self.api_hash
            )

            await client.start()

            kwargs = {
                'chat_id': "me",  # Saved Messages
                'video': video_path,
                'caption': caption,
                'parse_mode': ParseMode.HTML,
                'supports_streaming': True,
                'width': width,
                'height': height,
                'duration': duration,
            }

            if thumb_path:
                kwargs['thumb'] = thumb_path

            await client.send_video(**kwargs)
            self.last_error = ""
            print("[OK] Video successfully sent to Saved Messages!")
            return True

        except Exception as e:
            print(f"[ERROR] Send error: {e}")
            self.last_error = str(e)
            return False
        finally:
            if client:
                await client.stop()

    def is_connected(self):
        """Checks if client is connected (session is authorized)."""
        return self.connected
