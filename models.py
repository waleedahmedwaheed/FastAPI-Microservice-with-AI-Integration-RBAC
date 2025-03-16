from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

# ✅ User Table Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # Unique User ID
    username = Column(String(50), unique=True, index=True, nullable=False)  # Unique Username
    email = Column(String(100), unique=True, index=True, nullable=False)  # Unique Email
    hashed_password = Column(String(255), nullable=False)  # Secure Hashed Password
    is_admin = Column(Boolean, default=False)  # Boolean Flag for Admin Privileges
    role = Column(String(50), default="user")  # Role-Based Access Control (RBAC)

# ✅ Profile Table Model (One-to-One Relationship with User)
class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)  # User ID (Foreign Key)
    bio = Column(String(255), default=None)  # Optional Bio

    # Relationship with User Table
    user = relationship("User", back_populates="profile")

# ✅ Establish One-to-One Relationship (User <--> Profile)
User.profile = relationship("Profile", back_populates="user", uselist=False)

# ✅ Documents Table Model
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)  # Document Title
    content = Column(Text, nullable=False)  # Document Content
    created_at = Column(String(50), default="CURRENT_TIMESTAMP")  # Timestamp
