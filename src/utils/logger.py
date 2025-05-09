import logging
import os
from pathlib import Path

def setup_logger(name, log_level=logging.INFO, log_file=None):
    """
    Helper function to create logging configuration
    
    Args:
        name (str): Logger name
        log_level (int): Log level
        log_file (str, optional): Log file path. If not specified, logs only to console.
    
    Returns:
        logging.Logger: Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # If log file is specified, add file handler
    if log_file:
        # Create log directory
        log_dir = os.path.dirname(log_file)
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # Dosya handler'ı ekle
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Usage example
if __name__ == "__main__":
    # Create main logger
    main_logger = setup_logger("mqtt_social_bigdata", log_file="logs/app.log")
    
    # Create loggers for submodules
    mqtt_logger = setup_logger("mqtt_social_bigdata.mqtt", log_file="logs/mqtt.log")
    db_logger = setup_logger("mqtt_social_bigdata.database", log_file="logs/database.log")
    social_logger = setup_logger("mqtt_social_bigdata.social", log_file="logs/social.log")
    
    # Test log messages
    main_logger.info("Main application started")
    mqtt_logger.info("MQTT connection established")
    db_logger.error("Database connection error")
    social_logger.warning("Approaching API limits")
