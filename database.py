from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# ✅ Correct SQLAlchemy Base Import
Base = declarative_base()

DATABASE_URL = "mysql+asyncmy://root@localhost/fastapi_db"

engine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession  # ✅ Ensure async session is used correctly
)

async def get_db():
    async with SessionLocal() as session:
        yield session
