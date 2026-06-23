from dotenv import load_dotenv
import os

load_dotenv()

# PGHOST = os.environ.get("DB_HOST")
# PGPORT = os.environ.get("DB_PORT")
# DB_NAME = os.environ.get("DB_NAME")
# PGUSER = os.environ.get("DB_USER")
# PGPASSWORD = os.environ.get("DB_PASS")

DB_HOST = os.environ.get("PGHOST") or os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("PGPORT") or os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("PGDATABASE") or os.environ.get("DB_NAME", "diplom")
DB_USER = os.environ.get("PGUSER") or os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("PGPASSWORD") or os.environ.get("DB_PASS", "1234")