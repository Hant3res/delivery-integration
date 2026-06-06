from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    status = Column(String(20), default='queued')
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_engine():
    db_url = os.getenv('DATABASE_URL', 'mssql+pyodbc://sa:YourStrong!Passw0rd@localhost:1433/master?driver=ODBC+Driver+18+for+SQL+Server&trustservercertificate=yes')
    
    # First connect to master to create database if needed
    master_url = db_url.replace('/delivery_db?', '/master?') if '/delivery_db?' in db_url else db_url
    master_engine = create_engine(master_url, echo=False, isolation_level="AUTOCOMMIT")
    
    with master_engine.connect() as conn:
        # Use text() wrapper for raw SQL
        result = conn.execute(text("SELECT 1 FROM sys.databases WHERE name = 'delivery_db'"))
        exists = result.fetchone()
        if not exists:
            conn.execute(text("CREATE DATABASE delivery_db"))
            logger.info("Database 'delivery_db' created")
            time.sleep(2)  # Wait for database to be ready
    
    master_engine.dispose()
    
    # Now connect to delivery_db
    target_url = db_url.replace('/master?', '/delivery_db?') if '/master?' in db_url else db_url
    if '?driver' not in target_url:
        target_url = target_url + '?driver=ODBC+Driver+18+for+SQL+Server&trustservercertificate=yes'
    
    engine = create_engine(target_url, echo=False)
    return engine

engine = None
SessionLocal = None

def init_db():
    global engine, SessionLocal
    engine = get_engine()
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    
    db = SessionLocal()
    if db.query(Courier).count() == 0:
        couriers = [
            Courier(courier_id="courier_1", name="Ivan", available=True, location="Moscow"),
            Courier(courier_id="courier_2", name="Petr", available=True, location="Moscow"),
            Courier(courier_id="courier_3", name="Sidor", available=True, location="Moscow")
        ]
        for c in couriers:
            db.add(c)
        db.commit()
        logger.info("Seeded 3 couriers")
    db.close()
    return engine

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
