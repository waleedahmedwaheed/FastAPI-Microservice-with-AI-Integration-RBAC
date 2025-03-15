from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional, List
from datetime import datetime, timedelta
from oso import Oso
import uvicorn
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import openai

# FastAPI app instance
app = FastAPI()

# JWT Configuration
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Dummy Database
users_db = {}
roles_db = {"admin": {"can_read": True, "can_write": True}, "user": {"can_read": True, "can_write": False}}

# OSO for RBAC
oso = Oso()
oso.load_str("""
    allow(user: User, "read", resource) if user.role = "admin";
    allow(user: User, "write", resource) if user.role = "admin";
    allow(user: User, "read", resource) if user.role = "user";
""")

# User Model
class User(BaseModel):
    username: str
    password: str
    role: str = "user"

# Token Model
class TokenData(BaseModel):
    username: Optional[str] = None

# Helper Functions
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user(username: str):
    return users_db.get(username)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not verify_password(password, user["password"]):
        return False
    return user

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return get_user(username)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

# RAG Components
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")  # HuggingFace model
VECTOR_DIM = 384  # Output dimension of the embedding model
faiss_index = faiss.IndexFlatL2(VECTOR_DIM)  # FAISS Index
corpus = []  # Store document texts

# Function to add documents to FAISS index
def add_documents(docs: List[str]):
    global corpus
    embeddings = EMBEDDING_MODEL.encode(docs)
    faiss_index.add(np.array(embeddings).astype("float32"))
    corpus.extend(docs)

# Function to query FAISS and retrieve context
def retrieve_context(query: str, top_k: int = 3):
    query_embedding = EMBEDDING_MODEL.encode([query])
    distances, indices = faiss_index.search(np.array(query_embedding).astype("float32"), top_k)
    return [corpus[idx] for idx in indices[0] if idx < len(corpus)]

# OpenAI GPT Integration
def generate_response(query: str, context: List[str]):
    openai.api_key = "your_openai_api_key"
    prompt = f"Context: {' '.join(context)}\n\nUser Query: {query}\n\nAI Response:"
    response = openai.ChatCompletion.create(
        model="gpt-4", messages=[{"role": "system", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# Routes
@app.post("/register")
def register(user: User):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    users_db[user.username] = {"password": hash_password(user.password), "role": user.role}
    return {"message": "User registered successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    return {"username": current_user['username'], "role": current_user['role']}

@app.get("/admin")
def admin_panel(current_user: dict = Depends(get_current_user)):
    if not oso.is_allowed(current_user, "read", "admin_panel"):
        raise HTTPException(status_code=403, detail="Access denied")
    return {"message": "Welcome to the admin panel"}

@app.post("/add_docs")
def add_docs(docs: List[str]):
    add_documents(docs)
    return {"message": "Documents added to RAG pipeline"}

@app.post("/rag")
def rag_query(query: str, current_user: dict = Depends(get_current_user)):
    context = retrieve_context(query)
    response = generate_response(query, context)
    return {"query": query, "response": response}

# Run Server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)