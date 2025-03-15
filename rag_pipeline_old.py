import os
import faiss
import tempfile
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import FaissIndex
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_user
from pydantic import BaseModel
from langchain.schema import Document
from langchain.storage import InMemoryStore
import json

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("Missing OpenAI API Key. Set OPENAI_API_KEY in .env")

# Initialize Router
router = APIRouter()

# async def store_faiss_index():
    # """Creates and stores the FAISS index in MySQL without Pickle"""
    # async for db in get_db():
        # # Check if FAISS index already exists
        # result = await db.execute(select(FaissIndex).where(FaissIndex.name == "default_index"))
        # record = result.scalars().first()

        # if record:
            # print("✅ FAISS index already exists in MySQL.")
            # return

        # print("🔹 Creating a new FAISS index...")

        # # Sample documents (replace with real data)
        # documents = [
            # "Blockchain is a decentralized ledger technology...",
            # "Machine learning allows models to learn from data...",
            # "Quantum computing leverages the principles of quantum mechanics..."
        # ]

        # # Create FAISS index
        # embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        # faiss_index = FAISS.from_texts(documents, embeddings)

        # # Extract FAISS native index
        # faiss_index_obj = faiss_index.index  

        # # Use FAISS `write_index()` instead of `write_index_binary()`
        # with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # faiss.write_index(faiss_index_obj, temp_file.name)  # ✅ Correct FAISS function
            # with open(temp_file.name, "rb") as f:
                # index_data = f.read()

        # # Store in MySQL
        # new_record = FaissIndex(name="default_index", index_data=index_data)
        # db.add(new_record)
        # await db.commit()

        # print("✅ FAISS index created and saved in MySQL.")

# async def load_faiss_from_db(db: AsyncSession):
    # """ Load FAISS index from MySQL using FAISS's native format """
    # result = await db.execute(select(FaissIndex).where(FaissIndex.name == "default_index"))
    # record = result.scalars().first()

    # if record:
        # print("🔹 Loading FAISS index from MySQL...")

        # # Restore FAISS index from binary data
        # with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # temp_file.write(record.index_data)
            # temp_file.close()
            # faiss_index_obj = faiss.read_index(temp_file.name)  # ✅ Correct FAISS function

        # return FAISS(index=faiss_index_obj, embeddings=OpenAIEmbeddings(openai_api_key=openai_api_key))

    # else:
        # print("🔹 FAISS index not found. Creating a new one...")
        # await store_faiss_index()
        # return await load_faiss_from_db(db)

async def store_faiss_index():
    async for db in get_db():
        try:
            # Delete any old FAISS index
            await db.execute("DELETE FROM faiss_index WHERE name = 'default_index'")
            await db.commit()

            documents = [
                ("Blockchain is a decentralized ledger technology...", "doc_1"),
                ("Machine learning allows models to learn from data...", "doc_2"),
                ("Quantum computing leverages the principles of quantum mechanics...", "doc_3"),
            ]

            embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            texts = [doc[0] for doc in documents]
            metadatas = [{"id": doc[1]} for doc in documents]

            # Create FAISS index
            vector_store = FAISS.from_texts(texts, embeddings, metadatas=metadatas)
            faiss_index_obj = vector_store.index

            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                faiss.write_index(faiss_index_obj, temp_file.name)
                with open(temp_file.name, "rb") as f:
                    index_data = f.read()

            print(f"✅ FAISS index created. Embedding data: {len(index_data)} bytes")

            # Check OpenAI API response data
            openai_response = await embeddings.create_embeddings(texts)
            print(f"🔹 OpenAI Embedding Response: {json.dumps(openai_response)}")  # Debug log to see the response

            if 'data' not in openai_response or len(openai_response['data']) == 0:
                print("❌ No embeddings data received")
                raise HTTPException(status_code=500, detail="No embeddings returned from OpenAI API.")

            new_record = FaissIndex(name="default_index", index_data=index_data)
            db.add(new_record)

            # Commit to the database
            await db.commit()
            print("✅ FAISS index successfully stored and committed to the database.")

        except Exception as e:
            await db.rollback()  # Ensure rollback on error
            print(f"❌ FAISS Store Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to store FAISS index: {str(e)}")



async def load_faiss_from_db(db: AsyncSession):
    try:
        result = await db.execute(select(FaissIndex).where(FaissIndex.name == "default_index"))
        record = result.scalars().first()

        if not record:
            print("🔹 FAISS index not found. Creating a new one...")
            await store_faiss_index()
            return await load_faiss_from_db(db)

        print(f"🔹 FAISS index size: {len(record.index_data)} bytes")  

        # Restore FAISS index from binary data
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(record.index_data)
            temp_file.close()

            faiss_index_obj = faiss.read_index(temp_file.name)  
            print("✅ FAISS index loaded successfully!")

        # Ensure OpenAI Embeddings are loaded correctly
        embedding_model = OpenAIEmbeddings(openai_api_key=openai_api_key)

        # ✅ Fix: Initialize FAISS with proper arguments
        docstore = InMemoryStore()  # Required by FAISS in LangChain
        index_to_docstore_id = {}   # Empty mapping for now

        # ✅ Correct FAISS initialization
        vector_store = FAISS(
            index=faiss_index_obj,
            embedding_function=embedding_model,
            docstore=docstore,  # ✅ Required for LangChain FAISS
            index_to_docstore_id=index_to_docstore_id  # ✅ Required for LangChain FAISS
        )

        print(f"🔹 FAISS Number of Vectors: {faiss_index_obj.ntotal}")  

        return vector_store

    except Exception as e:
        print(f"❌ FAISS Load Error: {str(e)}")  
        raise HTTPException(status_code=500, detail=f"FAISS index loading failed: {str(e)}")



class QueryRequest(BaseModel):
    query: str

@router.post("/query")
async def query_rag(request: QueryRequest, db: AsyncSession = Depends(get_db), user: dict = Depends(get_current_user)):
    faiss_index = await load_faiss_from_db(db)
    if not faiss_index:
        raise HTTPException(status_code=404, detail="FAISS index not found")
    docs = faiss_index.similarity_search(request.query, k=3)
    if not docs:
        raise HTTPException(status_code=404, detail="No relevant documents found")
    context = "\n".join([doc.page_content for doc in docs])
    return {"query": request.query, "context": context}

 
  