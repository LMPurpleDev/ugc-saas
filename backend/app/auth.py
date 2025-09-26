from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from app.database import get_database
from app.models import User, TokenData
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    # Passlib's bcrypt handler automatically truncates passwords longer than 72 bytes.
    return pwd_context.hash(password)




def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        token_type_payload: str = payload.get("type")
        
        if email is None or token_type_payload != token_type:
            return None
            
        token_data = TokenData(email=email)
        return token_data
        
    except JWTError as e:
        logger.error(f"JWT Error: {e}")
        return None

async def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email from database"""
    try:
        db = get_database()
        user_data = db.users.find_one({"email": email})
        
        if user_data:
            # Comentário: A instanciação de User a partir de user_data funciona com Pydantic v2.
            return User(**user_data)
        return None
        
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return None

async def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID from database"""
    try:
        db = get_database()
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        
        if user_data:
            # Comentário: A instanciação de User a partir de user_data funciona com Pydantic v2.
            return User(**user_data)
        return None
        
    except Exception as e:
        logger.error(f"Error getting user by ID: {e}")
        return None

async def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    try:
        db = get_database()
        user_data = db.users.find_one({"email": email})
        
        if not user_data:
            return None
            
        if not verify_password(password, user_data["hashed_password"]):
            return None
            
        # Comentário: A instanciação de User a partir de user_data funciona com Pydantic v2.
        return User(**user_data)
        
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        token_data = verify_token(token, "access")
        
        if token_data is None:
            raise credentials_exception
            
        user = await get_user_by_email(email=token_data.email)
        if user is None:
            raise credentials_exception
            
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
            
        return user
        
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise credentials_exception

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def refresh_access_token(refresh_token: str) -> Optional[str]:
    """Generate new access token from refresh token"""
    try:
        token_data = verify_token(refresh_token, "refresh")
        if token_data is None:
            return None
            
        # Create new access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": token_data.email}, 
            expires_delta=access_token_expires
        )
        
        return access_token
        
    except Exception as e:
        logger.error(f"Error refreshing access token: {e}")
        return None


