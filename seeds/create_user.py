import argparse
from getpass import getpass


import sys
from pathlib import Path

# Add backend root to Python path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session
from db.session import SessionLocal
from apps.auth.models import UserRole
from apps.auth.services import create_user

# =====================================================
# User Seed Script
# Creates a user from the command line for bootstrapping.
# =====================================================

def main():
    """Parse CLI arguments and create a user through the service layer."""
    # 1️⃣ Create argument parser
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
        help="Role of the user (default: USER)",
    )

    parser.add_argument(
        "--password",
        help="Password of the user (if not provided, you will be prompted)",
    )

    args = parser.parse_args()

    
    # 3️⃣ Open DB session
    db: Session = SessionLocal()

    try:
        # 4️⃣ Handle password
        password = args.password
        if not password:
            password = getpass("Enter password: ")

        # 5️⃣ Convert role string to Enum
        role = UserRole(args.role)

        # 6️⃣ Create user using service layer
        user = create_user(
            db=db,
            matricule=args.matricule,
            password=password,
            role=role,
        )

        print(f"✅ User '{user.matricule}' created successfully with role {user.role.value}")

    except ValueError as e:
        print(f"❌ Error: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
