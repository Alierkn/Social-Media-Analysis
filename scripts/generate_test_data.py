#!/usr/bin/env python3

import os
import sys
import logging
import json
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

# Projenin kök dizinini ekle
sys.path.append(str(Path(__file__).parent.parent))

# Dotenv içe aktar
from dotenv import load_dotenv

# Proje modüllerini içe aktar
from src.mqtt_client import MQTTClient

# Load configuration
load_dotenv()

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_sensor_data(client, count=100, interval=1):
    """Generate test data for sensors and send to MQTT"""
    logger.info(f"Generating {count} sensor data points with {interval} second interval")
    
    sensor_types = ["temperature", "humidity", "pressure", "motion", "light"]
    sensor_units = {
        "temperature": "C",
        "humidity": "%",
        "pressure": "hPa",
        "motion": "bool",
        "light": "lux"
    }
    
    sensor_ids = [f"{t}_sensor_{i}" for t in sensor_types for i in range(1, 4)]
    
    for i in range(count):
        for sensor_id in sensor_ids:
            sensor_type = sensor_id.split("_")[0]
            
            # Generate value based on sensor type
            if sensor_type == "temperature":
                value = round(random.uniform(18, 30), 1)
            elif sensor_type == "humidity":
                value = round(random.uniform(30, 80), 1)
            elif sensor_type == "pressure":
                value = round(random.uniform(980, 1030), 1)
            elif sensor_type == "motion":
                value = random.choice([0, 1])
            elif sensor_type == "light":
                value = round(random.uniform(0, 1000), 1)
            else:
                value = random.random()
            
            # Create MQTT message
            message = {
                "sensor_id": sensor_id,
                "value": value,
                "unit": sensor_units.get(sensor_type, ""),
                "timestamp": datetime.now().isoformat()
            }
            
            # Create MQTT topic
            topic = f"sensors/{sensor_type}"
            
            # Send message to MQTT
            client.publish(topic, json.dumps(message))
            logger.info(f"Published to {topic}: {message}")
        
        # Belirtilen aralık kadar bekle
        time.sleep(interval)
    
    logger.info("Finished generating sensor data")

def generate_social_data(client, count=50, interval=2):
    """Generate test data for social media and send to MQTT"""
    logger.info(f"Generating {count} social media data points with {interval} second interval")
    
    platforms = ["twitter", "reddit"]
    
    # Sample users and hashtags for Twitter
    twitter_users = [f"user_{i}" for i in range(1, 21)]
    twitter_hashtags = ["IoT", "BigData", "MQTT", "Python", "DataScience", "AI", "ML"]
    
    # Sample users and subreddits for Reddit
    reddit_users = [f"redditor_{i}" for i in range(1, 21)]
    subreddits = ["IoT", "DataScience", "Python", "MQTT", "Programming"]
    
    for i in range(count):
        platform = random.choice(platforms)
        
        if platform == "twitter":
            # Generate sample data for Twitter
            user_id = random.choice(twitter_users)
            hashtags = random.sample(twitter_hashtags, random.randint(0, 3))
            mentions = random.sample(twitter_users, random.randint(0, 2))
            
            # Create content
            content = f"This is a test tweet about {random.choice(hashtags)} technology."
            for hashtag in hashtags:
                content += f" #{hashtag}"
            for mention in mentions:
                content += f" @{mention}"
            
            # Create tweet data
            tweet_data = {
                "id": f"tweet_{int(time.time())}_{i}",
                "user_id": user_id,
                "user_name": user_id,
                "user_followers": random.randint(10, 10000),
                "content": content,
                "created_at": (datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat(),
                "retweet_count": random.randint(0, 100),
                "favorite_count": random.randint(0, 200),
                "platform": "twitter",
                "hashtags": hashtags,
                "mentions": mentions
            }
            
            # MQTT'ye gönder
            client.publish("social/twitter", json.dumps(tweet_data))
            logger.info(f"Published to social/twitter: {tweet_data}")
        
        elif platform == "reddit":
            # Generate sample data for Reddit
            user_id = random.choice(reddit_users)
            subreddit = random.choice(subreddits)
            
            # Create content
            title = f"Question about {subreddit} implementations"
            content = f"This is a test post in r/{subreddit} subreddit discussing various aspects of the technology."
            
            # Create post data
            post_data = {
                "id": f"post_{int(time.time())}_{i}",
                "user_id": user_id,
                "title": title,
                "content": content,
                "created_at": (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat(),
                "score": random.randint(1, 1000),
                "upvote_ratio": round(random.uniform(0.5, 1.0), 2),
                "num_comments": random.randint(0, 50),
                "url": f"https://reddit.com/r/{subreddit}/comments/{i}",
                "platform": "reddit",
                "subreddit": subreddit
            }
            
            # MQTT'ye gönder
            client.publish("social/reddit", json.dumps(post_data))
            logger.info(f"Published to social/reddit: {post_data}")
            
            # Create comment
            if random.random() < 0.7:  # Create comment with 70% probability
                num_comments = random.randint(1, 5)
                
                for j in range(num_comments):
                    comment_data = {
                        "id": f"comment_{int(time.time())}_{i}_{j}",
                        "post_id": post_data["id"],
                        "user_id": random.choice(reddit_users),
                        "content": f"This is a test comment on the post about {subreddit}.",
                        "created_at": (datetime.now() - timedelta(hours=random.randint(0, 12))).isoformat(),
                        "score": random.randint(1, 100),
                        "platform": "reddit",
                        "parent_id": post_data["id"]
                    }
                    
                    # MQTT'ye gönder
                    client.publish("social/reddit_comment", json.dumps(comment_data))
                    logger.info(f"Published to social/reddit_comment: {comment_data}")
        
        # Belirtilen aralık kadar bekle
        time.sleep(interval)
    
    logger.info("Finished generating social media data")

def main():
    try:
        # Create MQTT client
        client = MQTTClient(
            broker_address=os.getenv("MQTT_BROKER_ADDRESS", "localhost"),
            broker_port=int(os.getenv("MQTT_BROKER_PORT", 1883)),
            client_id="test_data_generator"
        )
        
        # Connect to MQTT
        if client.connect():
            # Generate sensor data
            generate_sensor_data(client, count=50, interval=0.5)
            
            # Generate social media data
            generate_social_data(client, count=30, interval=1)
            
            # Close MQTT connection
            client.disconnect()
        else:
            logger.error("Could not connect to MQTT broker")
    
    except Exception as e:
        logger.error(f"Error generating test data: {e}")
    
    logger.info("Test data generation completed")

if __name__ == "__main__":
    main()
