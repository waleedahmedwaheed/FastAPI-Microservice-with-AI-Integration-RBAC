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

## Running the Microservice

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
  