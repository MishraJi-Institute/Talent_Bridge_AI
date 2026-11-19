"""Optional database driver setup.

SQLite is the default local database and does not need PyMySQL. Import and
register the MySQL driver only when the private environment explicitly selects
MySQL, so an unrelated/broken MySQL crypto dependency cannot prevent the
default SQLite development server from starting.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

if os.environ.get("DB_ENGINE", "sqlite").strip().lower() == "mysql":
    import pymysql

    pymysql.install_as_MySQLdb()
