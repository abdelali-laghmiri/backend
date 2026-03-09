import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session
from db.session import SessionLocal
from apps.permissions.models import Permission
from apps.permissions.permissions_list import PERMISSIONS


def seed_permissions(db: Session):
    """Insert predefined permissions that are missing from the database."""

    for perm_name in PERMISSIONS:

        existing = db.query(Permission).filter(
            Permission.name == perm_name
        ).first()

        if not existing:

            permission = Permission(
                name=perm_name
            )

            db.add(permission)

    db.commit()


def run():
    """Open a session and execute the permissions seed routine."""

    db = SessionLocal()

    try:
        seed_permissions(db)
        print("✅ Permissions seeded")

    finally:
        db.close()


if __name__ == "__main__":
    run()
