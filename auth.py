from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import or_
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from models import User
from database import get_db

# ✅ Secret Key & JWT Settings (Ensure to use environment variables in production)
SECRET_KEY = "supersecretkey"  # 🔹 Change this for production (Use `.env`)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 🔹 Token expiration time

# ✅ Initialize Security Modules
http_bearer = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ FastAPI Router
router = APIRouter()

# --------------------------------------------
# 🔹 User Authentication Helper Functions
# --------------------------------------------

class TokenData(BaseModel):
    """Schema for decoding JWT Token"""
    username: str = None


async def authenticate_user(db: AsyncSession, username: str, password: str):
    """Authenticates a user by checking their credentials"""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()

    if not user or not pwd_context.verify(password, user.hashed_password):
        return False  # Invalid credentials
    return user

# --------------------------------------------
# 🔹 User Registration Route
# --------------------------------------------

class UserRegister(BaseModel):
    """Schema for user registration"""
    username: str
    email: str
    password: str

@router.post("/register")
async def register_user(user: UserRegister, db: AsyncSession = Depends(get_db)):
    """Registers a new user with unique username & email"""
    try:
        print(f"🔹 Checking for existing user: {user.username}, {user.email}")  # ✅ Debugging

        # ✅ Check if username or email already exists
        result = await db.execute(
            select(User).where(or_(User.email == user.email, User.username == user.username))
        )
        existing_user = result.scalars().first()

        if existing_user:
            print(f"❌ User already exists: {existing_user.username}")  # ✅ Debugging
            raise HTTPException(status_code=400, detail="Username or Email already registered")

        print("🔹 Creating new user...")  # ✅ Debugging

        # ✅ Hash password and create user
        hashed_password = pwd_context.hash(user.password)
        new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)  # ✅ Ensure user is fully saved

        print(f"✅ User Created: {new_user.username}")  # ✅ Debugging
        return {"id": new_user.id, "username": new_user.username, "email": new_user.email}
    
    except SQLAlchemyError as e:
        await db.rollback()  # ✅ Rollback on error
        print(f"❌ Database Error: {str(e)}")  # ✅ Debugging
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")  # ✅ Debugging
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# --------------------------------------------
# 🔹 User Login Route & JWT Token Generation
# --------------------------------------------

class Token(BaseModel):
    """Schema for JWT Token response"""
    access_token: str
    token_type: str

class LoginRequest(BaseModel):  
    """Schema for user login"""
    username: str
    password: str

async def create_access_token(data: dict, expires_delta: timedelta = None):
    """Generates a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login", response_model=Token)
async def login_user(user: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticates user & returns JWT token"""
    try:
        result = await db.execute(select(User).where(User.username == user.username))
        user_obj = result.scalars().first()

        if not user_obj or not pwd_context.verify(user.password, user_obj.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = await create_access_token(data={"sub": user_obj.username})

        return {"access_token": access_token, "token_type": "bearer"}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# --------------------------------------------
# 🔹 Get Current User from JWT Token
# --------------------------------------------

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(http_bearer), db: AsyncSession = Depends(get_db)):
    """Extracts user info from JWT and fetches full user details from DB"""
    token = credentials.credentials  # Extract token from Authorization header
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
