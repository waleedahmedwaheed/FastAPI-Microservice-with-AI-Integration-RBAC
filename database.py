from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# ✅ SQLAlchemy Base Model (Used for ORM Mappings)
Base = declarative_base()

# ✅ Database Connection URL (Ensure correct credentials & DB exists)
DATABASE_URL = "mysql+asyncmy://root@localhost/fastapi_db"

# ✅ Create an Async Engine (Asynchronous MySQL Connection)
engine = create_async_engine(DATABASE_URL, echo=True)

# ✅ Configure Async Session Maker (For DB Transactions)
SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,  # Prevent auto-expiring objects after commit
    class_=AsyncSession  # Ensure async session is used correctly
)

# ✅ Dependency to Get Database Session (For FastAPI Dependency Injection)
async def get_db():
    async with SessionLocal() as session:
        yield session
