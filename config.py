import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
SESSION = os.environ["SESSION"]
OWNER_ID = int(os.environ["OWNER_ID"])

TG_BOT_WORKERS = int(os.getenv("TG_BOT_WORKERS", "4"))
DOWNLOAD_DIR = "downloads"
MAX_CONCURRENT_DOWNLOADS = 5

# MongoDB connection. MONGO_URI is required (e.g. a MongoDB Atlas
# connection string). MONGO_DB_NAME defaults to "diskwala_bot".
MONGO_URI = os.environ["MONGO_URI"]
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "diskwala_bot")

# ---------------------------------------------------------------------
# Extra settings for premium / admin / cache features.
# ADMINS: comma-separated user ids in the ADMINS env var. OWNER_ID is
# always treated as an admin even if not listed.
# ---------------------------------------------------------------------
ADMINS = list({OWNER_ID, *[int(x) for x in os.getenv("ADMINS", "").split(",") if x.strip()]})

# Photo shown on /start. Can be a URL or a local file path.
START_PHOTO_URL = os.getenv("START_PHOTO_URL", "https://iili.io/nH8JrFI.jpg")

# Free (non-premium) users can download this many files per day (UTC).
DAILY_FREE_LIMIT = int(os.getenv("DAILY_FREE_LIMIT", "5"))

# If > 0, delivered videos are auto-deleted from the chat after this many
# seconds (the caption warns the user to forward it first). 0 disables it.
AUTO_DELETE_SECONDS = int(os.getenv("AUTO_DELETE_SECONDS", "0"))

# Optional: channel id (e.g. -100xxxxxxxxxx) where new-user/download logs
# are posted. Leave unset/empty to disable logging.
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0")) or None

# Optional: comma-separated channel ids to also receive a copy of every
# delivered video (a simple off-site backup). Leave empty to disable.
BACKUP_CHANNEL_IDS = [int(x) for x in os.getenv("BACKUP_CHANNEL_IDS", "").split(",") if x.strip()]
