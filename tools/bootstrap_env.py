"""Create a private local .env on first run without overwriting user settings."""
from pathlib import Path
import secrets

ROOT = Path(__file__).resolve().parent
env_file = ROOT / ".env"
example = ROOT / ".env.example"

if not env_file.exists():
    env_file.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")

text = env_file.read_text(encoding="utf-8")
if not any(line.strip().startswith("DJANGO_SECRET_KEY=") and line.split("=", 1)[1].strip()
           for line in text.splitlines()):
    with env_file.open("a", encoding="utf-8") as handle:
        handle.write("\n# Generated locally; keep this file private.\n")
        handle.write("DJANGO_SECRET_KEY=" + secrets.token_urlsafe(48) + "\n")
print("Local .env is ready (existing settings preserved).")
