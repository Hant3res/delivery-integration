import logging
import json
from datetime import datetime
import os

# Custom JSON formatter
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'props'):
            log_entry.update(record.props)
        
        return json.dumps(log_entry, ensure_ascii=False)

# Console formatter (human-readable)
class ConsoleFormatter(logging.Formatter):
    def format(self, record):
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] {record.levelname:8} | {record.name:20} | {record.getMessage()}"

def setup_logger(name, log_to_file=True, log_to_console=True):
    """Setup logger with file and console handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # File handler (JSON format)
    if log_to_file:
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler(f"logs/{name}.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
    
    # Console handler (human-readable)
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ConsoleFormatter())
        logger.addHandler(console_handler)
    
    return logger

def log_with_props(logger, level, message, **kwargs):
    """Log message with additional properties"""
    if kwargs:
        # Create a log record with extra properties
        logger.log(level, message, extra={'props': kwargs})
    else:
        logger.log(level, message)

# Create main application logger
app_logger = setup_logger("delivery_app")

# Create API call logger
api_logger = setup_logger("delivery_api")
