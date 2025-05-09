#!/usr/bin/env python3

import os
import logging
import argparse
import signal
import sys
from pathlib import Path
from dotenv import load_dotenv

# Proje modüllerini içe aktar
from src.data_processor import DataProcessor

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global değişkenler
processor = None

def signal_handler(sig, frame):
    """Signal handler (for catching Ctrl+C)"""
    logger.info("Shutting down...")
    if processor:
        processor.stop()
    sys.exit(0)

def main():
    global processor
    
    # Argument parser
    parser = argparse.ArgumentParser(description="MQTT Social Big Data Application")
    parser.add_argument("--env", type=str, default=".env", help="Path to .env file")
    parser.add_argument("--log-level", type=str, default="INFO", 
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Set the logging level")
    
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Create log directory
    Path("logs").mkdir(exist_ok=True)
    
    # Create data directory
    Path("data/reports").mkdir(parents=True, exist_ok=True)
    
    # Load .env file
    load_dotenv(args.env)
    
    # Configuration dictionary
    config = {key: os.getenv(key) for key in os.environ}
    
    try:
        # SIGINT (Ctrl+C) sinyalini ele al
        signal.signal(signal.SIGINT, signal_handler)
        
        # Create and start data processor
        processor = DataProcessor(config)
        processor.start()
        
        logger.info("Application started. Press Ctrl+C to exit.")
        
        # Keep main thread running
        signal.pause()
    except Exception as e:
        logger.error(f"Error in main application: {e}")
        if processor:
            processor.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
