from sqlalchemy.orm import Session

from apps.auth.models import User, UserRole
from apps.auth.services import create_user, get_user_by_matricule
from core.settings import settings


def seed_superuser(db: Session) -> User | None:
    """Create the configured superuser once and skip duplicates safely."""
    matricule = settings.SUPERUSER_MATRICULE
    password = settings.SUPERUSER_PASSWORD

    if not matricule or not password:
        print("Superuser seed skipped: SUPERUSER_MATRICULE or SUPERUSER_PASSWORD is not set.")
        return None

    existing_user = get_user_by_matricule(db, matricule)
    if existing_user:
        if existing_user.role == UserRole.SUPERUSER:
            print(f"Superuser seed skipped: '{matricule}' already exists.")
        else:
            print(
                f"Superuser seed skipped: '{matricule}' already exists but is not a superuser."
            )
        return existing_user

    existing_superuser = db.query(User).filter(User.role == UserRole.SUPERUSER).first()
    if existing_superuser:
        print(
            f"Superuser seed skipped: another superuser already exists ('{existing_superuser.matricule}')."
        )
        return existing_superuser

    superuser = create_user(
        db=db,
        matricule=matricule,
        password=password,
        role=UserRole.SUPERUSER,
    )
    print(f"Superuser '{superuser.matricule}' created.")
    return superuser
