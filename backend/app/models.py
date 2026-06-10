from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Float, Boolean, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Pet(Base):
    __tablename__ = "petsLost"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50)) 
    status = Column(String(20), default="lost") 
    description = Column(Text)
    date = Column(String(50))
    city = Column(String(25))
    lat = Column(Float)
    long = Column(Float)
    image = Column(String(500), nullable=True)
    contact_phone = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="lost_pets")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String)
    phone = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    pet_profiles = relationship("PetProfile", back_populates="owner", cascade="all, delete-orphan")
    lost_pets = relationship("Pet", back_populates="user")

class PetProfile(Base):
    __tablename__ = "pet_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    name = Column(String, nullable=False)           
    type = Column(String, nullable=False)       
    breed = Column(String, nullable=True)      
    birth_date = Column(String, nullable=True)   
    color = Column(String, nullable=True)          
    avatar = Column(String, nullable=True)         
    notes = Column(String, nullable=True)          
    is_chipped = Column(Boolean, default=False)   
    chip_number = Column(String, nullable=True)    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    owner = relationship("User", back_populates="pet_profiles")

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)         
    image_url = Column(String, nullable=True)      
    category = Column(String(50), nullable=True)    
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)  
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    author = relationship("User")
    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan")
    
class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    article = relationship("Article", back_populates="comments")
    user = relationship("User")