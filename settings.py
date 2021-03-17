import dotenv

import os

dotenv.load_dotenv()

API_TOKEN = os.getenv("PROVERBOFTHEDAY_TOKEN")
DB_NAME = os.getenv("DB_NAME")
DB_DRIVER = os.getenv("DB_DRIVER")
