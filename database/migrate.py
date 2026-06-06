from models import init_db, Base
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'mssql+pyodbc://sa:YourStrong!Passw0rd@localhost:1433/delivery_db?driver=ODBC+Driver+18+for+SQL+Server&trustservercertificate=yes')

def run_migration():
    print("Running database migrations...")
    engine = init_db(DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Insert initial data
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Check if couriers exist
    from models import Courier
    existing = session.query(Courier).count()
    
    if existing == 0:
        print("Seeding initial couriers...")
        couriers = [
            Courier(courier_id="courier_1", name="Ivan", available=True, location="Moscow, Tverskaya"),
            Courier(courier_id="courier_2", name="Petr", available=True, location="Moscow, Arbat"),
            Courier(courier_id="courier_3", name="Sidor", available=True, location="Moscow, Kutuzovsky")
        ]
        for c in couriers:
            session.add(c)
        session.commit()
        print(f"Added {len(couriers)} couriers")
    
    session.close()
    print("Migrations completed successfully!")

if __name__ == "__main__":
    run_migration()
