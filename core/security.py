from os import getenv
from datetime import datetime, timedelta, timezone
from typing import Any
from fastapi import HTTPException, status

import jwt
from passlib.context import CryptContext
from core.config import settings



ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def decode_access_token(token: str) -> dict:
    """
    Décode un token JWT et retourne les informations extraites.
    Si le token est invalide ou expiré, une exception HTTP est levée.
    """
    try:
        # Décodage du token avec la clé secrète et l'algorithme de signature
        payload = jwt.decode(token, getenv("JWT_SECRET"), algorithms=[ALGORITHM])
        
        # Vérification si le token a expiré
        if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token expiré",
            )
        
        return payload
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token expiré",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token invalide",
        )

def decode_refresh_token(token: str) -> dict:
    """
    Décode un refresh token et vérifie sa validité.
    Si le token est invalide ou expiré, une exception HTTP est levée.
    """
    try:
        payload = jwt.decode(token, getenv("JWT_SECRET"), algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token invalide : type incorrect",
            )
        if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Refresh token expiré",
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Refresh token expiré",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token invalide",
        )

def create_access_token(subject: str | Any, expires_delta: timedelta = timedelta(hours=1)) -> str:
    """
    Crée un token JWT d'accès.
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, getenv("JWT_SECRET"), algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: str | Any, expires_delta: timedelta = timedelta(days=7)) -> str:
    """
    Crée un token JWT d'actualisation (refresh token).
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, getenv("JWT_SECRET"), algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    print("****************************************************************")
    print(plain_password, hashed_password)
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)