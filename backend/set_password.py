"""Set (or change) the admin password.

    python set_password.py

Writes ADMIN_PASSWORD_HASH and a SECRET_KEY into backend/.env, keeping any
other settings already in that file. Changing the password also logs out
every existing session. Restart the server afterwards.
"""

import getpass
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.security import hash_password  # noqa: E402

ENV_FILE = Path(__file__).resolve().parent / ".env"
MIN_LENGTH = 12


def main() -> None:
    password = getpass.getpass(f"New admin password (at least {MIN_LENGTH} characters): ")
    if len(password) < MIN_LENGTH:
        sys.exit(f"Too short. Use at least {MIN_LENGTH} characters.")
    if getpass.getpass("Type it again: ") != password:
        sys.exit("Passwords don't match.")

    new_values = {
        "ADMIN_PASSWORD_HASH": hash_password(password),
        "SECRET_KEY": secrets.token_urlsafe(48),
    }
    lines = ENV_FILE.read_text().splitlines() if ENV_FILE.exists() else []
    lines = [line for line in lines if line.split("=", 1)[0].strip() not in new_values]
    lines += [f"{key}={value}" for key, value in new_values.items()]
    ENV_FILE.write_text("\n".join(lines) + "\n")
    print(f"Saved to {ENV_FILE}. Restart the backend to use the new password.")


if __name__ == "__main__":
    main()
