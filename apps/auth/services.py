from sqlalchemy.orm import Session
from passlib.context import CryptContext

# =====================================================
# Authentication Services
# Encapsulates user creation, lookup, and password handling.
# =====================================================

# import the User and UserRole models
from .models import User,UserRole

# Password hashing context used across the authentication layer.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_users_by_role(db: Session, role: UserRole):
    """Return all users assigned to the given role."""
    users = db.query(User).filter(User.role == role).all() 
    return users

def get_password_hash(password)-> str:
    """Hash a plain-text password before storing it."""
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    """Compare a plain-text password against its stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_user(
        db : Session,
        matricule: str,
        password: str,
        role: UserRole = UserRole.USER
        ):
    """Create a user account after validating uniqueness rules."""
    
    if role == UserRole.SUPERUSER:
        if db.query(User.id).filter(User.role == UserRole.SUPERUSER).first():
            raise ValueError("A superuser already exists.")
    if db.query(User.id).filter(User.matricule == matricule).first():
        raise ValueError("A user with this matricule already exists.")
    hashed_password = get_password_hash(password)
    db_user = User(
        matricule=matricule,
        hashed_password=hashed_password,
        role=role,
        is_active=True,
        first_login=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, matricule: str, password: str):
    """Authenticate a user by matricule and password."""
    db_user = db.query(User).filter(User.matricule == matricule).first()
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user

def get_user_by_matricule(db: Session, matricule: str):
    """Fetch a user account by its matricule."""
    return db.query(User).filter(User.matricule == matricule).first()
