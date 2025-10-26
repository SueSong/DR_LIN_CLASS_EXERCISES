from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .database import Base

class User(Base):
    """Agent/Supervisor/Admin users"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(20), default="agent")  # agent, supervisor, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Customer(Base):
    """Customer records"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True)
    phone = Column(String(50), index=True)
    account_number = Column(String(50), unique=True, index=True)
    tier = Column(String(20), default="standard")  # standard, gold, platinum
    status = Column(String(20), default="active")  # active, inactive
    lifetime_value = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    calls = relationship("Call", back_populates="customer")
    orders = relationship("Order", back_populates="customer")
    tickets = relationship("Ticket", back_populates="customer")

class Call(Base):
    """Call records"""
    __tablename__ = "calls"
    
    id = Column(Integer, primary_key=True)
    call_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    agent_name = Column(String(255))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    status = Column(String(20), default="active")  # active, completed, abandoned
    sentiment = Column(String(20), default="neutral")  # positive, neutral, negative
    summary = Column(Text, nullable=True)
    recording_url = Column(Text, nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="calls")
    transcripts = relationship("Transcript", back_populates="call", cascade="all, delete-orphan")
    suggestions = relationship("AISuggestion", back_populates="call", cascade="all, delete-orphan")

class Transcript(Base):
    """Transcription segments"""
    __tablename__ = "transcripts"
    
    id = Column(Integer, primary_key=True)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.call_id"), index=True)
    speaker = Column(String(20))  # customer, agent
    text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    confidence = Column(Float, default=1.0)
    
    # Relationships
    call = relationship("Call", back_populates="transcripts")

class AISuggestion(Base):
    """AI-generated suggestions"""
    __tablename__ = "ai_suggestions"
    
    id = Column(Integer, primary_key=True)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.call_id"), index=True)
    suggestion_type = Column(String(50))  # tip, alert, action, info
    message = Column(Text)
    used = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    call = relationship("Call", back_populates="suggestions")

class Order(Base):
    """Customer orders"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), index=True)
    order_number = Column(String(50), unique=True, index=True)
    product_name = Column(String(255))
    amount = Column(Float)
    status = Column(String(50))  # pending, shipped, delivered, cancelled
    order_date = Column(DateTime)
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")

class Ticket(Base):
    """Support tickets"""
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), index=True)
    ticket_number = Column(String(50), unique=True, index=True)
    subject = Column(String(255))
    description = Column(Text, nullable=True)
    status = Column(String(50))  # open, in_progress, resolved, closed
    priority = Column(String(20))  # low, medium, high, urgent
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="tickets")

