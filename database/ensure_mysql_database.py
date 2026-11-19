"""Create the configured MySQL database if DB_ENGINE=mysql."""
from pathlib import Path
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "legacy-django"))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

if os.getenv("DB_ENGINE", "sqlite").strip().lower() != "mysql":
    print("SQLite selected; no external database server is needed.")
    raise SystemExit(0)

import pymysql

name = os.getenv("DB_NAME", "TalentBridgeAI").strip()
if not re.fullmatch(r"[A-Za-z0-9_]+", name):
    raise SystemExit("DB_NAME may contain only letters, numbers and underscores.")
connection = pymysql.connect(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    charset="utf8mb4",
    autocommit=True,
)
try:
    with connection.cursor() as cursor:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{name}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
finally:
    connection.close()
print(f"MySQL database '{name}' is ready. Django migrations will create its tables.")
