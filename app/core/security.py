from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:

    """Хэширование пароля."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str ) -> bool:
    """Проверка пароля."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token ( data: dict )-> str:
    """Создание JWT токена."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )   

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        raise ValueError("Invalid token")


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_error
        return int(user_id)
    except ValueError:
        raise credentials_error