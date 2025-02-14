# crud/crud_user.py

import uuid
from sqlalchemy.orm import Session
from models.models import User, UserCreate
from core.security import get_password_hash
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

def get_user_by_email(db: Session, email: str) -> User:
    """
    Recherche un utilisateur par son adresse email (en ignorant la casse et les espaces).
    """
    normalized_email = email.strip().lower()  # Normalise l'email (supprime les espaces et met en minuscule)
    return db.exec(select(User).where(User.email == normalized_email)).first()

def get_user_by_id(db: Session, user_id: uuid.UUID) -> User:
    """
    Recherche un utilisateur par son ID.
    """
    if not isinstance(user_id, uuid.UUID):
        raise ValueError(f"L'ID utilisateur '{user_id}' n'est pas un UUID valide.")
    
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_create: UserCreate):
    """
    Crée un nouvel utilisateur dans la base de données.
    """
    user_create.password = get_password_hash(user_create.password)
    user_data = user_create.dict(exclude_unset=True, exclude={'deleted_at'})
    user = User(**user_data)
    
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"L'utilisateur avec cet email existe déjà: {e}")
