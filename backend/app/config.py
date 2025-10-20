import os
from dotenv import load_dotenv

load_dotenv()
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "dev-admin-token")
DB_PATH = os.getenv("DB_PATH", "app.db")