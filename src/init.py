#!/usr/bin/env python3

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Proje modüllerini içe aktar
from .utils.init import initialize_project
from .utils.logger import setup_logger
from .database_manager import DatabaseManager
from .mqtt_client import MQTTClient
from .social_media_connector import SocialMediaConnector
from .data_processor import DataProcessor

logger = logging.getLogger(__name__)

def init_app(config=None):
    """Initialize the application and configure necessary components."""
    try:
        # Load basic configuration
        if not config:
            load_dotenv()
            config = {key: os.getenv(key) for key in os.environ}
        
        # Logging configuration
        setup_logger()
        
        # Proje başlangıç ayarlarını yap
        if not initialize_project():
            raise Exception("Project initialization failed")
        
        # Create database connections
        db_manager = DatabaseManager(
            sql_conn_string=config.get('SQL_CONN_STRING'),
            mongo_conn_string=config.get('MONGO_CONN_STRING'),
            neo4j_uri=config.get('NEO4J_URI'),
            neo4j_user=config.get('NEO4J_USER'),
            neo4j_password=config.get('NEO4J_PASSWORD')
        )
        
        # Create MQTT client
        mqtt_client = MQTTClient(
            broker_address=config.get('MQTT_BROKER_ADDRESS', 'localhost'),
            broker_port=int(config.get('MQTT_BROKER_PORT', 1883)),
            client_id="mqtt_social_bigdata"
        )
        
        # Create social media connections
        social_connector = SocialMediaConnector(
            twitter_api_key=config.get('TWITTER_API_KEY'),
            twitter_api_secret=config.get('TWITTER_API_SECRET'),
            twitter_access_token=config.get('TWITTER_ACCESS_TOKEN'),
            twitter_access_secret=config.get('TWITTER_ACCESS_SECRET'),
            reddit_client_id=config.get('REDDIT_CLIENT_ID'),
            reddit_client_secret=config.get('REDDIT_CLIENT_SECRET'),
            reddit_user_agent=config.get('REDDIT_USER_AGENT')
        )
        
        # Create data processor
        data_processor = DataProcessor(
            mqtt_client=mqtt_client,
            db_manager=db_manager,
            social_connector=social_connector
        )
        
        logger.info("Application components initialized successfully")
        
        return {
            'db_manager': db_manager,
            'mqtt_client': mqtt_client,
            'social_connector': social_connector,
            'data_processor': data_processor
        }
        
    except Exception as e:
        logger.error(f"Error initializing application: {e}")
        raise

if __name__ == "__main__":
    try:
        components = init_app()
        logger.info("Application initialized successfully")
    except Exception as e:
        logger.error(f"Application initialization failed: {e}")
        raise
