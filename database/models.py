from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class Courier(Base):
    __tablename__ = 'couriers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    courier_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    available = Column(Boolean, default=True)
    location = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    deliveries = relationship("Delivery", back_populates="courier")

class Delivery(Base):
    __tablename__ = 'deliveries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(50), unique=True, nullable=False)
    order_id = Column(String(50), nullable=False)
    address = Column(String(500), nullable=False)
    recipient_phone = Column(String(20), nullable=False)
    courier_id = Column(Integer, ForeignKey('couriers.id'))
    status = Column(String(50), default='assigned')
    proof = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    courier = relationship("Courier", back_populates="deliveries")

class TrackingHistory(Base):
    __tablename__ = 'tracking_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(50), nullable=False)
    lat = Column(Float)
    lng = Column(Float)
    status = Column(String(50))
    updated_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipient = Column(String(50), nullable=False)
    type = Column(String(20), default='sms')
    message = Column(Text)
    order_id = Column(String(50))
    status = Column(String(20), default='queued')
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db(database_url):
    engine = create_engine(database_url, echo=True)
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
