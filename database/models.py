from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
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

class Delivery(Base):
    __tablename__ = 'deliveries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(50), unique=True, nullable=False)
    order_id = Column(String(50), nullable=False)
    address = Column(String(500), nullable=False)
    recipient_phone = Column(String(20), nullable=False)
    courier_id = Column(String(50))
    courier_name = Column(String(100))
    status = Column(String(50), default='assigned')
    proof = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

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
    status = Column(String(20), default='sent')
    sent_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

# MySQL connection
# Format: mysql+pymysql://user:password@host:port/database
DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://delivery_user:delivery_pass@localhost:3306/delivery_db')

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    
    # Check if couriers exist
    if db.query(Courier).count() == 0:
        couriers = [
            Courier(courier_id="courier_1", name="Ivan", available=True, location="Moscow"),
            Courier(courier_id="courier_2", name="Petr", available=True, location="Moscow"),
            Courier(courier_id="courier_3", name="Sidor", available=True, location="Moscow")
        ]
        for c in couriers:
            db.add(c)
        db.commit()
        print("Seeded 3 couriers")
    db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
