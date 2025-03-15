# import os
# import faiss
# import tempfile
# from dotenv import load_dotenv
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from database import get_db
# from models import FaissIndex
# from langchain_community.vectorstores import FAISS
# from langchain_openai import OpenAIEmbeddings
# from fastapi import APIRouter, Depends, HTTPException
# from auth import get_current_user
# from pydantic import BaseModel
# from langchain.schema import Document
# from langchain.storage import InMemoryStore
# import json

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Document
import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import get_db
from auth import get_current_user

#from langchain_openai import OpenAIEmbeddings
#import openai
#import numpy as np

from openai import OpenAI

# Load environment variables
# load_dotenv()
# openai_api_key = os.getenv("OPENAI_API_KEY")
# embeddings = OpenAIEmbeddings()

os.environ["OPENAI_API_KEY"] = "sk-zW0ZWvnjoaBeyJQgPshh9OMRaxw2B8c0VsQnYy4Mq2T3BlbkFJYJq4uZ_0Ix5XGesBDfF6rFf1YkzU48wlIoYeSutv8A"
client = OpenAI()

# if not openai_api_key:
    # raise ValueError("Missing OpenAI API Key. Set OPENAI_API_KEY in .env")

# Initialize Router
router = APIRouter()


class QueryRequest(BaseModel):
    query: str

async def generate_response_with_ai(context: str, query: str):
    """Generate an AI-based response from the given context."""
    prompt = f"Based on the following context, answer the query.\n\nContext:\n{context}\n\nQuery: {query}\nAnswer:"
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        return completion.choices[0].message.content
    except Error as e:
        # Handle any errors that occur during the request to OpenAI API
        print(f"Error generating response: {e}")
        return "Sorry, I couldn't generate a response at the moment."
    
@router.post("/query")
async def query_rag(request: QueryRequest, db: AsyncSession = Depends(get_db), user: dict = Depends(get_current_user)):
    # Query the database for relevant documents based on the user's query
    documents = await get_relevant_chunks(db, request.query)
    
    if not documents:
        raise HTTPException(status_code=404, detail="No relevant documents found")
    
    # Combine the relevant document contents into context for the AI model
    context = "\n".join([doc.content for doc in documents])

    #return {"query": request.query, "context": context}
    
    answer = await generate_response_with_ai(context, request.query)

    return {"query": request.query, "context": context, "answer": answer}


async def get_relevant_chunks(db: AsyncSession, query: str, top_k: int = 3):
    """Retrieve the most relevant documents based on the query."""
    
    # Query the Document table to search for relevant documents based on the query
    # Using `contains` to check if the query exists within the content of the document
    result = await db.execute(
        select(Document) 
        .filter(Document.content.contains(query))  # Match the query against the content of the document
        .limit(top_k)  # Limit to top K results
    )
    documents = result.scalars().all()
    
    return documents

 
  