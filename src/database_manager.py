from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from neo4j import GraphDatabase
import datetime
import logging
import os

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

Base = declarative_base()

# Model definitions for SQL tables
class SensorData(Base):
    __tablename__ = 'sensor_data'
    
    id = Column(Integer, primary_key=True)
    topic = Column(String)
    sensor_id = Column(String)
    value = Column(Float)
    unit = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<SensorData(sensor_id='{self.sensor_id}', value={self.value}, unit='{self.unit}')>"

class SocialMediaPost(Base):
    __tablename__ = 'social_media_posts'
    
    id = Column(Integer, primary_key=True)
    platform = Column(String)
    post_id = Column(String)
    user_id = Column(String)
    content = Column(String)
    sentiment = Column(Float)
    timestamp = Column(DateTime)
    
    def __repr__(self):
        return f"<SocialMediaPost(platform='{self.platform}', user_id='{self.user_id}')>"

class DatabaseManager:
    def __init__(self, sql_conn_string="sqlite:///iot_social_data.db", 
                 mongo_conn_string="mongodb://localhost:27017/", 
                 neo4j_uri="bolt://localhost:7687", 
                 neo4j_user="neo4j", 
                 neo4j_password="password"):
        
        # Create database connections
        if sql_conn_string.startswith("sqlite"):
            db_path = sql_conn_string.replace("sqlite:///", "")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # SQLite connection
        try:
            self.sql_engine = create_engine(sql_conn_string)
            Base.metadata.create_all(self.sql_engine)
            Session = sessionmaker(bind=self.sql_engine)
            self.sql_session = Session()
            logger.info("SQL database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to SQL database: {e}")
            self.sql_session = None
        
        # MongoDB connection
        try:
            self.mongo_client = MongoClient(mongo_conn_string)
            self.mongo_db = self.mongo_client["iot_social_data"]
            logger.info("MongoDB connection established")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.mongo_db = None
        
        # Neo4j connection
        try:
            self.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            logger.info("Neo4j connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self.neo4j_driver = None
    
    def close_connections(self):
        """Close all database connections"""
        if self.sql_session:
            self.sql_session.close()
        
        if self.mongo_client:
            self.mongo_client.close()
        
        if self.neo4j_driver:
            self.neo4j_driver.close()
        
        logger.info("All database connections closed")
    
    def save_sensor_data(self, topic, data):
        """Save sensor data to all databases"""
        try:
            sensor_data = SensorData(
                topic=topic,
                sensor_id=data.get('sensor_id'),
                value=data.get('value'),
                unit=data.get('unit')
            )
            self.sql_session.add(sensor_data)
            self.sql_session.commit()
            logger.info(f"Sensor data saved to SQL database: {sensor_data}")
            return True
        except Exception as e:
            self.sql_session.rollback()
            logger.error(f"Error saving sensor data to SQL: {e}")
            return False
    
    def save_social_data(self, topic, data):
        """Save social media data to all databases"""
        try:
            # Convert date to suitable format
            timestamp = data.get('created_at')
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except ValueError:
                    timestamp = datetime.datetime.now()
            
            social_post = SocialMediaPost(
                platform=topic,
                post_id=data.get('id'),
                user_id=data.get('user_id'),
                content=data.get('content'),
                sentiment=data.get('sentiment'),
                timestamp=timestamp
            )
            self.sql_session.add(social_post)
            self.sql_session.commit()
            logger.info(f"Social media post saved to SQL database: {social_post}")
            return True
        except Exception as e:
            self.sql_session.rollback()
            logger.error(f"Error saving social post to SQL: {e}")
            return False
    
    def save_data_to_mongodb(self, collection_name, data):
        """Save data to MongoDB"""
        try:
            collection = self.mongo_db[collection_name]
            if isinstance(data, list):
                result = collection.insert_many(data)
                logger.info(f"Multiple documents saved to MongoDB collection {collection_name}")
            else:
                result = collection.insert_one(data)
                logger.info(f"Document saved to MongoDB collection {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error saving data to MongoDB: {e}")
            return False
    
    def save_social_relationship_to_neo4j(self, user1, user2, relationship_type, properties=None):
        """Sosyal ilişkileri Neo4j'ye kaydet"""
        if properties is None:
            properties = {}
            
        query = (
            f"MERGE (a:User {{id: $user1_id}}) "
            f"MERGE (b:User {{id: $user2_id}}) "
            f"MERGE (a)-[r:{relationship_type} $properties]->(b) "
            f"RETURN a, r, b"
        )
        
        try:
            with self.neo4j_driver.session() as session:
                result = session.run(
                    query,
                    user1_id=user1,
                    user2_id=user2,
                    properties=properties
                )
                logger.info(f"Social relationship saved to Neo4j: {user1}-[{relationship_type}]->{user2}")
                return True
        except Exception as e:
            logger.error(f"Error saving relationship to Neo4j: {e}")
            return False

# Test amaçlı kullanım
if __name__ == "__main__":
    # Test database connection
    db_manager = DatabaseManager(sql_conn_string="sqlite:///data/test_db.db")
    
    # Test sensör verisi
    db_manager.save_sensor_data_to_sql("sensors/temperature", {
        "sensor_id": "temp1",
        "value": 25.5,
        "unit": "C"
    })
    
    # Test MongoDB
    db_manager.save_data_to_mongodb("test_collection", {"name": "Test Document", "value": 42})
    
    # Test Neo4j ilişkisi
    db_manager.save_social_relationship_to_neo4j("user1", "user2", "FOLLOWS", {"since": "2023-01-01"})
    
    # Close connections
    db_manager.close_connections()
