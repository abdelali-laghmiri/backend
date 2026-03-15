from sqlalchemy.orm import Session

from apps.permissions.models import Permission
from apps.permissions.permissions_list import PERMISSIONS
from db.session import SessionLocal


def seed_permissions(db: Session) -> int:
    """Insert predefined permissions that are missing from the database."""
    existing_permissions = {
        name
        for (name,) in db.query(Permission.name)
        .filter(Permission.name.in_(PERMISSIONS))
        .all()
    }
    missing_permissions = [
        Permission(name=permission_name)
        for permission_name in PERMISSIONS
        if permission_name not in existing_permissions
    ]

    if not missing_permissions:
        return 0

    db.add_all(missing_permissions)
    db.commit()
    return len(missing_permissions)


def run() -> None:
    """Open a session and execute the permissions seed routine."""
    db = SessionLocal()

    try:
        created_count = seed_permissions(db)
        print(f"Permissions seed completed; created {created_count} permission(s).")
    finally:
        db.close()


if __name__ == "__main__":
    run()
