import re

def validate_phone(phone):
    """Validate phone number format"""
    if not phone:
        return False, "Phone number is required"
    
    # Simple validation: at least 10 digits
    digits = re.sub(r'\D', '', phone)
    if len(digits) < 10:
        return False, "Phone number must contain at least 10 digits"
    
    return True, "Valid"

def validate_order_data(order_id, address, recipient_phone):
    """Validate all order fields"""
    if not order_id:
        return False, "order_id is required"
    
    if not address:
        return False, "address is required"
    
    is_valid, msg = validate_phone(recipient_phone)
    if not is_valid:
        return False, msg
    
    return True, "Valid"
