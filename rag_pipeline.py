from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Document
import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import get_db
from auth import get_current_user
from openai import OpenAI, OpenAIError
from sqlalchemy.sql import text

# ✅ Load environment variables securely
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("❌ Missing OpenAI API Key. Set OPENAI_API_KEY in .env")

# ✅ Initialize OpenAI Client
client = OpenAI(api_key=openai_api_key)

# ✅ Initialize FastAPI Router
router = APIRouter()

# ✅ Define request model
class QueryRequest(BaseModel):
    query: str

async def generate_response_with_ai(context: str, query: str):
    """
    🔹 Generate an AI-powered response based on retrieved document context.
    - context: Extracted relevant document data
    - query: User's input query
    - Returns AI-generated response
    """
    prompt = f"Based on the following context, answer the query.\n\nContext:\n{context}\n\nQuery: {query}\nAnswer:"
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",  # ✅ Ensure correct model is used
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content

    except OpenAIError as e:
        print(f"❌ OpenAI API Error: {e}")  # ✅ Debugging
        return "❌ Sorry, I couldn't generate a response at the moment."

@router.post("/query")
async def query_rag(
    request: QueryRequest, 
    db: AsyncSession = Depends(get_db), 
    user: dict = Depends(get_current_user)
):
    """
    🔹 AI-powered RAG Pipeline Query Handler
    - Searches for relevant documents
    - Extracts relevant content
    - Uses OpenAI to generate AI responses
    """
    try:
        # ✅ Retrieve relevant document chunks
        documents = await get_relevant_chunks(db, request.query)
        
        if not documents:
            raise HTTPException(status_code=404, detail="No relevant documents found")

        # ✅ Combine relevant document contents into a context string
        context = "\n".join([doc.content for doc in documents])

        # ✅ Generate AI response based on retrieved context
        answer = await generate_response_with_ai(context, request.query)

        return {"query": request.query, "context": context, "answer": answer}
    
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")  # ✅ Debugging
        raise HTTPException(status_code=404, detail="No relevant documents found")

# async def get_relevant_chunks(db: AsyncSession, query: str, top_k: int = 3):
    # """
    # 🔹 Retrieve the most relevant documents based on a user query.
    # - Uses SQLAlchemy to fetch data from `documents` table
    # - Matches query against document content
    # - Returns top_k relevant document chunks
    # """
    # try:
        # result = await db.execute(
            # select(Document)
            # .filter(Document.content.contains(query))  # ✅ Search for relevant content
            # .limit(top_k)  # ✅ Limit results
        # )
        # documents = result.scalars().all()
        # return documents

    # except Exception as e:
        # print(f"❌ Database Query Error: {e}")  # ✅ Debugging
        # return []
        
async def get_relevant_chunks(db: AsyncSession, query: str, top_k: int = 3):
    """
    🔹 Retrieve relevant documents using MySQL Full-Text Search.
    ✅ Fix: Ensure the full document (title, content) is retrieved.
    """
    try:
        sql = text("""
            SELECT id, title, content FROM documents 
            WHERE MATCH(content) AGAINST (:query IN BOOLEAN MODE) 
            LIMIT :top_k
        """)

        result = await db.execute(sql, {"query": f'+{query}*', "top_k": top_k})
        documents = result.mappings().all()  # ✅ Fetch full document as dict

        if not documents:
            print(f"❌ No matching documents found for: {query}")  # ✅ Debugging
        
        return documents  # ✅ Returns a list of full document data

    except Exception as e:
        print(f"❌ Database Query Error: {e}")  # ✅ Debugging
        return []
 