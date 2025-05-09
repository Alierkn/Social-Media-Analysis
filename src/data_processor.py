import json
import time
import logging
import threading
import schedule
import datetime
import os
import pandas as pd
from pathlib import Path

# Import other modules from our project
from src.mqtt_client import MQTTClient
from src.database_manager import DatabaseManager
from src.social_media_connector import SocialMediaConnector

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, config=None):
        if config is None:
            config = {}
        
        # Start MQTT client setup
        self.mqtt_client = MQTTClient(
            broker_address=config.get("MQTT_BROKER_ADDRESS", "localhost"),
            broker_port=int(config.get("MQTT_BROKER_PORT", 1883))
        )
        
        # Start database manager setup
        self.db_manager = DatabaseManager(
            sql_conn_string=config.get("SQL_CONN_STRING", "sqlite:///data/iot_social_data.db"),
            mongo_conn_string=config.get("MONGO_CONN_STRING", "mongodb://localhost:27017/"),
            neo4j_uri=config.get("NEO4J_URI", "bolt://localhost:7687"),
            neo4j_user=config.get("NEO4J_USER", "neo4j"),
            neo4j_password=config.get("NEO4J_PASSWORD", "password")
        )
        
        # Start social media connector setup
        twitter_credentials = {
            "consumer_key": config.get("TWITTER_API_KEY"),
            "consumer_secret": config.get("TWITTER_API_SECRET"),
            "access_token": config.get("TWITTER_ACCESS_TOKEN"),
            "access_token_secret": config.get("TWITTER_ACCESS_SECRET")
        }
        
        reddit_credentials = {
            "client_id": config.get("REDDIT_CLIENT_ID"),
            "client_secret": config.get("REDDIT_CLIENT_SECRET"),
            "user_agent": config.get("REDDIT_USER_AGENT"),
            "username": config.get("REDDIT_USERNAME"),
            "password": config.get("REDDIT_PASSWORD")
        }
        
        self.social_connector = SocialMediaConnector(
            twitter_credentials=twitter_credentials,
            reddit_credentials=reddit_credentials
        )
        
        # Customize MQTT callback
        self.mqtt_client.client.on_message = self.on_mqtt_message
        
        # Create directory for reports
        reports_dir = Path("data/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
    
    def start(self):
        """Start all services"""
        # Establish MQTT connection
        if self.mqtt_client.connect():
            # Subscribe to relevant MQTT topics
            self.mqtt_client.subscribe("sensors/+")  # All sensor data
            self.mqtt_client.subscribe("social/+")   # All social media data
        
        # Schedule tasks
        schedule.every(1).hours.do(self.collect_twitter_data, query="#IoT", count=100)
        schedule.every(2).hours.do(self.collect_reddit_data, subreddit="IoT", limit=50)
        schedule.every(1).days.at("00:00").do(self.generate_daily_report)
        
        # Start a thread to run scheduled tasks
        scheduler_thread = threading.Thread(target=self.run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        # Start initial data collection immediately
        self.collect_twitter_data(query="#IoT", count=50)
        self.collect_reddit_data(subreddit="IoT", limit=20)
        
        logger.info("Data processor started successfully")
    
    def run_scheduler(self):
        """Run scheduled tasks"""
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def on_mqtt_message(self, client, userdata, msg):
        """Process MQTT messages"""
        try:
            topic = msg.topic
            payload = msg.payload.decode("utf-8")
            logger.info(f"Received message on topic {topic}: {payload}")
            
            # Convert message to JSON
            try:
                data = json.loads(payload)
                
                # Route data to appropriate database based on topic
                if topic.startswith("sensors/"):
                    self.process_sensor_data(topic, data)
                elif topic.startswith("social/"):
                    self.process_social_data(topic, data)
                
            except json.JSONDecodeError:
                logger.warning(f"Received message is not valid JSON: {payload}")
                
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def process_sensor_data(self, topic, data):
        """Process sensor data and route to appropriate database"""
        sensor_type = topic.split("/")[1]
        
        if sensor_type in ["temperature", "humidity", "pressure"]:
            # Structured data for SQL
            self.db_manager.save_sensor_data_to_sql(topic, data)
        else:
            # Other sensor data for MongoDB
            self.db_manager.save_data_to_mongodb("sensor_data", {
                "topic": topic,
                "data": data,
                "timestamp": datetime.datetime.now()
            })
    
    def process_social_data(self, topic, data):
        """Process social media data and route to appropriate databases"""
        platform = topic.split("/")[1]
        
        # Save all data to MongoDB (semi-structured)
        self.db_manager.save_data_to_mongodb(f"{platform}_data", data)
        
        # Platform-specific processing
        if platform == "twitter":
            # Save tweet content and sentiment analysis to SQL
            if "user_id" in data and "content" in data:
                self.db_manager.save_social_post_to_sql(platform, data)
            
            # Save interactions to Neo4j
            if "user_id" in data and "mentions" in data:
                for mentioned_user in data["mentions"]:
                    self.db_manager.save_social_relationship_to_neo4j(
                        data["user_id"],
                        mentioned_user,
                        "MENTIONS",
                        {"timestamp": datetime.datetime.now().isoformat()}
                    )
        
        elif platform == "reddit":
            # Save Reddit posts to SQL
            if "user_id" in data and "content" in data:
                self.db_manager.save_social_post_to_sql(platform, data)
            
            # Save comment relationships to Neo4j
            if "user_id" in data and "post_id" in data and "parent_id" in data:
                self.db_manager.save_social_relationship_to_neo4j(
                    data["user_id"],
                    data["parent_id"],
                    "COMMENTED_ON",
                    {"timestamp": datetime.datetime.now().isoformat()}
                )
    
    def collect_twitter_data(self, query, count=100):
        """Collect Twitter data and publish to MQTT"""
        try:
            logger.info(f"Collecting Twitter data for query: {query}")
            tweets = self.social_connector.search_twitter(query, count)
            
            if tweets:
                logger.info(f"Collected {len(tweets)} tweets")
                
                # Publish each tweet as an MQTT message
                for tweet in tweets:
                    self.mqtt_client.publish("social/twitter", json.dumps(tweet))
                
                # Identify influential users
                influencers = self.social_connector.identify_influencers(tweets, "twitter")
                if influencers:
                    self.db_manager.save_data_to_mongodb("twitter_influencers", {
                        "query": query,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "influencers": influencers
                    })
                
                # Perform trend analysis
                trends = self.social_connector.analyze_trends(tweets, "twitter")
                if trends:
                    self.db_manager.save_data_to_mongodb("twitter_trends", {
                        "query": query,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "trends": trends
                    })
                
                return True
            else:
                logger.warning(f"No tweets found for query: {query}")
                return False
        except Exception as e:
            logger.error(f"Error collecting Twitter data: {e}")
            return False
    
    def collect_reddit_data(self, subreddit, limit=100, time_filter="week"):
        """Collect Reddit data and publish to MQTT"""
        try:
            logger.info(f"Collecting Reddit data for subreddit: {subreddit}")
            posts = self.social_connector.search_reddit(subreddit, limit, time_filter)
            
            if posts:
                logger.info(f"Collected {len(posts)} posts from r/{subreddit}")
                
                # Publish each post as an MQTT message
                for post in posts:
                    self.mqtt_client.publish("social/reddit", json.dumps({
                        **post,
                        "created_at": post["created_at"].isoformat() if isinstance(post["created_at"], datetime.datetime) else post["created_at"]
                    }))
                    
                    # Collect comments for popular posts
                    if post["num_comments"] > 10 and post["score"] > 50:
                        comments = self.social_connector.get_reddit_comments(post["id"], limit=100)
                        
                        for comment in comments:
                            self.mqtt_client.publish("social/reddit_comment", json.dumps({
                                **comment,
                                "created_at": comment["created_at"].isoformat() if isinstance(comment["created_at"], datetime.datetime) else comment["created_at"]
                            }))
                
                # Identify influential users
                influencers = self.social_connector.identify_influencers(posts, "reddit")
                if influencers:
                    self.db_manager.save_data_to_mongodb("reddit_influencers", {
                        "subreddit": subreddit,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "influencers": influencers
                    })
                
                # Perform trend analysis
                trends = self.social_connector.analyze_trends(posts, "reddit")
                if trends:
                    self.db_manager.save_data_to_mongodb("reddit_trends", {
                        "subreddit": subreddit,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "trends": trends
                    })
                
                return True
            else:
                logger.warning(f"No posts found for subreddit: {subreddit}")
                return False
        except Exception as e:
            logger.error(f"Error collecting Reddit data: {e}")
            return False
    
    def generate_daily_report(self):
        """Generate daily report"""
        try:
            now = datetime.datetime.now()
            report_date = now.strftime("%Y-%m-%d")
            logger.info(f"Generating daily report for {report_date}")
            
            report = {
                "date": report_date,
                "generated_at": now.isoformat(),
                "twitter_stats": {},
                "reddit_stats": {},
                "sensor_stats": {}
            }
            
            # Determine report file name
            report_filename = f"data/reports/daily_report_{report_date}.json"
            
            # Save report to JSON file
            with open(report_filename, "w") as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Daily report saved to {report_filename}")
            return True
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
            return False
    
    def stop(self):
        """Stop all services"""
        # Close MQTT connection
        self.mqtt_client.disconnect()
        
        # Close database connections
        self.db_manager.close_connections()
        
        logger.info("Data processor stopped")

# Test usage
if __name__ == "__main__":
    # Load environment variables from .env file (requires dotenv library)
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get environment variables as a dictionary
    config = {key: os.getenv(key) for key in os.environ}
    
    # Start data processor
    processor = DataProcessor(config)
    processor.start()
    
    try:
        # Keep main thread running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        processor.stop()
