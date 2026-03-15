import argparse
from getpass import getpass

from sqlalchemy.orm import Session

from apps.auth.models import UserRole
from apps.auth.services import create_user
from db.session import SessionLocal


def main() -> None:
    """Parse CLI arguments and create a user through the service layer."""
    parser = argparse.ArgumentParser(description="Create a new user")

    parser.add_argument(
        "--matricule",
        required=True,
        help="Matricule of the user",
    )
    parser.add_argument(
        "--role",
        default="user",
        choices=["user", "superuser"],
        help="Role of the user (default: user)",
    )
    parser.add_argument(
        "--password",
        help="Password of the user (if not provided, you will be prompted)",
    )

    args = parser.parse_args()
    db: Session = SessionLocal()

    try:
        password = args.password or getpass("Enter password: ")
        role = UserRole(args.role)
        user = create_user(
            db=db,
            matricule=args.matricule,
            password=password,
            role=role,
        )
        print(f"User '{user.matricule}' created successfully with role {user.role.value}.")
    except ValueError as exc:
        print(f"Error: {exc}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
