from dotenv import load_dotenv
import os

load_dotenv()

PGHOST = os.environ.get("DB_HOST")
PGPORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
PGUSER = os.environ.get("DB_USER")
PGPASSWORD = os.environ.get("DB_PASS")