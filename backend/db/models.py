import time
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(Float, default=time.time)

    documents = relationship("Document", back_populates="owner", cascade="all, delete")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)   # UUID string
    file_name = Column(String, nullable=False)
    uploaded_at = Column(Float, default=time.time)
    status = Column(String, default="processing")        # processing | ready | failed
    chunk_count = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="documents")