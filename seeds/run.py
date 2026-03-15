from db.session import SessionLocal
from seeds.permissions_seed import seed_permissions
from seeds.superuser_seed import seed_superuser


def run() -> None:
    """Execute all idempotent database seed routines."""
    db = SessionLocal()

    try:
        permissions_created = seed_permissions(db)
        seed_superuser(db)
        print(f"Database seed run completed; created {permissions_created} permission(s).")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
