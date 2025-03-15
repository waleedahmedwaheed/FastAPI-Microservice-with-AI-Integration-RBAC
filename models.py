from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, LargeBinary
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    is_admin = Column(Boolean, default=False)
    role = Column(String(50), default="user")

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    bio = Column(String(255), default=None)
    user = relationship("User", back_populates="profile")

User.profile = relationship("Profile", back_populates="user", uselist=False)

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(String(50), default="CURRENT_TIMESTAMP")

class FaissIndex(Base):
    __tablename__ = "faiss_index"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)  # Index name
    index_data = Column(LargeBinary, nullable=False)  # Store FAISS binary data
