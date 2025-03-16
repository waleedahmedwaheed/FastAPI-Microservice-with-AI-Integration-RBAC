# 🚀 FastAPI Microservice with AI Integration & RBAC

## 📖 Overview

This FastAPI microservice provides **secure CRUD operations for user profiles, JWT-based authentication, AI-powered RAG pipeline**, and **Role-Based Access Control (RBAC) using Oso Framework**. The system ensures **admin role management and protected API endpoints**.

---

## 📌 Features

✅ **CRUD Operations** - Users can register, update, delete, and retrieve profiles securely.  
✅ **JWT Authentication** - Secure login and access control using JWT tokens.  
✅ **AI Integration (RAG Pipeline)** - Uses OpenAI to generate intelligent responses based on document search.  
✅ **Role-Based Access Control (RBAC)** - Implemented with **Oso** to restrict access based on user roles.  
✅ **Pytest Coverage** - Automated test cases for authentication, CRUD, and AI-powered queries.  
✅ **Swagger UI Documentation** - Interactive API documentation available at `/docs`.

---

## 🛠️ Installation

## Clone the Repository**
```bash
git clone https://github.com/waleedahmedwaheed/FastAPI-Microservice-with-AI-Integration-RBAC.git
cd fastapi-microservice
```

## Create a Virtual Environment

```
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate      # On Windows
```

## Install Dependencies

```
pip install -r requirements.txt
```

## 🚀 Running the Microservice

### Apply Database Migrations

```
alembic upgrade head
```

### Start the FastAPI Server

```
uvicorn main:app --reload
```

The API will be available at: http://127.0.0.1:8000

### API Documentation

Swagger UI: http://127.0.0.1:8000/docs
  
  
### 🔑 Authentication & Authorization

#### 1️⃣ Register a New User
<p>Endpoint: POST /register </p>
<p>Payload:</p>

```json
{
    "username": "johndoe",
    "email": "johndoe@example.com",
    "password": "securepassword"
}
```
✅ Response: 
```json
{
    "id": 1, 
    "username": "johndoe", 
    "email": "johndoe@example.com"
}
```

#### 2️⃣ Login & Get JWT Token
<p>Endpoint: POST /login </p>
<p>Payload:</p>

```json
{
    "username": "johndoe",
    "password": "securepassword"
}
```

✅ Response:
```json
{
    "access_token": "your_jwt_token",
    "token_type": "bearer"
}
```

#### 3️⃣ Get User Profile
<p>Endpoint: GET /profile </p>
<p>🔐 Requires JWT Authentication (Authorization: Bearer <token>)</p>
✅ Response:

```json
{
    "id": 1,
    "user_id": 1,
    "bio": "This is a new profile."
}
```

#### 4️⃣ Update Profile
<p>Endpoint: PUT /profile </p>
<p>Payload: </p>

```json
{
    "bio": "Updated bio information"
}
```
✅ Response:

```json
{
    "message": "Profile updated successfully", 
    "bio": "Updated bio information"
}
```

#### 5️⃣ Delete Profile
<p>Endpoint: DELETE /profile</p>
<p>🔐 Requires JWT Authentication</p>
✅ Response:

```json
{
    "message": "Profile deleted successfully"
}
```

#### 6️⃣ Query AI-Powered RAG Pipeline
<p>Endpoint: POST /rag/query</p>
<p>Payload:</p>

```json
{
    "query": "What is blockchain?"
}
```

✅ Response:

```json
{
    "query": "What is blockchain?",
    "context": "Blockchain is a decentralized ledger technology...",
    "answer": "Blockchain is a secure digital ledger technology used in cryptocurrencies."
}
```

### ✅ Running Tests with Pytest

```
pytest tests/
```

<p>This will test authentication, CRUD operations, AI queries, and RBAC access.</p>