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

#### Register a New User
Endpoint: POST /register
Payload:

```json
{
    "username": "johndoe",
    "email": "johndoe@example.com",
    "password": "securepassword"
}
```
✅ Response: 
```json
{"id": 1, "username": "johndoe", "email": "johndoe@example.com"}
```

#### Login & Get JWT Token
Endpoint: POST /login
Payload:

```json
{
    "username": "johndoe",
    "password": "securepassword"
}
```

✅ Response:
```json{
    "access_token": "your_jwt_token",
    "token_type": "bearer"
}
```

#### Get User Profile
Endpoint: GET /profile
🔐 Requires JWT Authentication (Authorization: Bearer <token>)
✅ Response:

```json
{
    "id": 1,
    "user_id": 1,
    "bio": "This is a new profile."
}
```

#### Update Profile
Endpoint: PUT /profile
Payload:

```json
{
    "bio": "Updated bio information"
}
```
✅ Response:

```
{"message": "Profile updated successfully", "bio": "Updated bio information"}
```

#### Delete Profile
Endpoint: DELETE /profile
🔐 Requires JWT Authentication
✅ Response:

```
{"message": "Profile deleted successfully"}
```

#### Query AI-Powered RAG Pipeline
Endpoint: POST /rag/query
Payload:

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