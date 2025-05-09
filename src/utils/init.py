#!/usr/bin/env python3

import os
import logging
import nltk
from pathlib import Path

logger = logging.getLogger(__name__)

def initialize_project():
    """Initialize required project settings."""
    try:
        # Create directory structure
        directories = [
            "data",
            "data/reports",
            "data/raw",
            "data/processed",
            "logs",
            "models"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        
        # NLTK verilerini indir
        nltk_data = [
            "punkt",
            "averaged_perceptron_tagger",
            "maxent_ne_chunker",
            "words",
            "stopwords",
            "vader_lexicon"
        ]
        
        for data in nltk_data:
            try:
                nltk.download(data, quiet=True)
                logger.info(f"Downloaded NLTK data: {data}")
            except Exception as e:
                logger.warning(f"Could not download NLTK data {data}: {e}")
        
        # Çevre değişkenlerini kontrol et
        required_env_vars = [
            "MQTT_BROKER_ADDRESS",
            "MQTT_BROKER_PORT",
            "MONGO_CONN_STRING",
            "NEO4J_URI",
            "NEO4J_USER",
            "NEO4J_PASSWORD",
            "TWITTER_API_KEY",
            "TWITTER_API_SECRET",
            "TWITTER_ACCESS_TOKEN",
            "TWITTER_ACCESS_SECRET",
            "REDDIT_CLIENT_ID",
            "REDDIT_CLIENT_SECRET",
            "REDDIT_USER_AGENT"
        ]
        
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.warning("Missing environment variables:")
            for var in missing_vars:
                logger.warning(f"- {var}")
        else:
            logger.info("All required environment variables are set")
        
        return True
        
    except Exception as e:
        logger.error(f"Error initializing project: {e}")
        return False

if __name__ == "__main__":
    # Logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start the project
    if initialize_project():
        logger.info("Project initialization completed successfully")
    else:
        logger.error("Project initialization failed")
