from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User
from database import get_db
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import or_
from fastapi.security import OAuth2PasswordBearer

# Secret Key & JWT Settings
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ FIX: Define FastAPI Router
router = APIRouter()

class TokenData(BaseModel):
    username: str = None

async def authenticate_user(db: AsyncSession, username: str, password: str):
    """Authenticate user with username & password"""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str, db: AsyncSession = Depends(get_db)):
    """Extracts user info from JWT and fetches from DB"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # ✅ Fetch full user object from the database
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

# ✅ FIX: Register Route Now Works
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

@router.post("/register")
async def register_user(user: UserRegister, db: AsyncSession = Depends(get_db)):
    """Registers a new user with unique username & email"""
    try:
        # ✅ Fix: Use `or_()` from SQLAlchemy for multiple conditions
        result = await db.execute(
            select(User).where(or_(User.email == user.email, User.username == user.username))
        )
        existing_user = result.scalars().first()

        if existing_user:
            if existing_user.email == user.email:
                raise HTTPException(status_code=400, detail="Email already registered")
            if existing_user.username == user.username:
                raise HTTPException(status_code=400, detail="Username already taken")

        # ✅ Hash password and create user
        hashed_password = pwd_context.hash(user.password)
        new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)  # ✅ Ensure user is fully saved

        return {"id": new_user.id, "username": new_user.username, "email": new_user.email}
    
    except SQLAlchemyError as e:
        await db.rollback()  # ✅ Rollback on error
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}") 

class Token(BaseModel):
    access_token: str
    token_type: str
    
# ✅ FIX: Login Route Added
class LoginRequest(BaseModel): 
    username: str
    password: str

async def create_access_token(data: dict, expires_delta: timedelta = None):
    """Generate JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
@router.post("/login", response_model=Token)
async def login_user(user: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user & return JWT token"""
    try:
        result = await db.execute(select(User).where(User.username == user.username))
        user_obj = result.scalars().first()

        if not user_obj:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not pwd_context.verify(user.password, user_obj.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = await create_access_token(data={"sub": user_obj.username})

        return {"access_token": access_token, "token_type": "bearer"}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
        

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # ✅ FastAPI OAuth2 scheme

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """Extracts user info from JWT and fetches full user details from DB"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # ✅ Fetch full user object from the database
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user 
    