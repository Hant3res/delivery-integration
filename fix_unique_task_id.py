import uuid
from database.models import get_db, Delivery

def generate_unique_task_id(db):
    """Generate unique task_id with collision check"""
    max_attempts = 5
    for attempt in range(max_attempts):
        task_id = str(uuid.uuid4())[:8]
        existing = db.query(Delivery).filter(Delivery.task_id == task_id).first()
        if not existing:
            return task_id
    raise Exception(f"Failed to generate unique task_id after {max_attempts} attempts")
