#!/usr/bin/env python3

import os
import sys
import logging
from pathlib import Path
import subprocess
import argparse

# Add project root directory
sys.path.append(str(Path(__file__).parent.parent))

# Import dotenv
from dotenv import load_dotenv

# Load configuration
load_dotenv()

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_sqlite():
    """Set up SQLite database and create tables"""
    try:
        from src.database_manager import Base, SensorData, SocialMediaPost
        from sqlalchemy import create_engine
        
        db_path = os.getenv("SQL_CONN_STRING", "sqlite:///data/iot_social_data.db")
        
        # Create the directory for the SQLite database file
        if db_path.startswith("sqlite:///"):
            db_file = db_path.replace("sqlite:///", "")
            os.makedirs(os.path.dirname(db_file), exist_ok=True)
        
        engine = create_engine(db_path)
        Base.metadata.create_all(engine)
        logger.info(f"SQLite tables created successfully at {db_path}")
        return True
    except Exception as e:
        logger.error(f"Error setting up SQLite: {e}")
        return False

def setup_mongodb():
    """Set up MongoDB database and create collections"""
    try:
        from pymongo import MongoClient
        
        mongo_conn_string = os.getenv("MONGO_CONN_STRING", "mongodb://localhost:27017/")
        client = MongoClient(mongo_conn_string)
        db = client["iot_social_data"]
        
        # Create the necessary collections
        collections = [
            "sensor_data", 
            "twitter_data", 
            "reddit_data", 
            "twitter_trends", 
            "reddit_trends", 
            "twitter_influencers", 
            "reddit_influencers"
        ]
        
        for collection_name in collections:
            db.create_collection(collection_name)
        
        logger.info(f"MongoDB collections created successfully at {mongo_conn_string}")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Error setting up MongoDB: {e}")
        return False

def setup_neo4j():
    """Set up Neo4j database and create constraints"""
    try:
        from neo4j import GraphDatabase
        
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        # Create constraints
        with driver.session() as session:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")
        
        logger.info(f"Neo4j constraints created successfully at {neo4j_uri}")
        driver.close()
        return True
    except Exception as e:
        logger.error(f"Error setting up Neo4j: {e}")
        return False

def setup_docker_containers():
    """Create and start Docker containers"""
    try:
        # Start containers using Docker Compose
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("Docker containers started successfully")
        logger.info(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error starting Docker containers: {e}")
        logger.error(e.stderr)
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Setup databases for MQTT Social Big Data project")
    parser.add_argument("--sqlite", action="store_true", help="Setup SQLite database")
    parser.add_argument("--mongodb", action="store_true", help="Setup MongoDB database")
    parser.add_argument("--neo4j", action="store_true", help="Setup Neo4j database")
    parser.add_argument("--docker", action="store_true", help="Setup Docker containers")
    parser.add_argument("--all", action="store_true", help="Setup all databases and containers")
    
    args = parser.parse_args()
    
    # Eğer hiçbir argüman verilmemişse, --all argümanını kullan
    if not (args.sqlite or args.mongodb or args.neo4j or args.docker or args.all):
        args.all = True
    
    if args.all or args.docker:
        setup_docker_containers()
    
    if args.all or args.sqlite:
        setup_sqlite()
    
    if args.all or args.mongodb:
        setup_mongodb()
    
    if args.all or args.neo4j:
        setup_neo4j()
    
    logger.info("Database setup completed")

if __name__ == "__main__":
    main()
