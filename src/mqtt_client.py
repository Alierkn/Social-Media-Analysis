import paho.mqtt.client as mqtt
import json
import time
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self, broker_address="localhost", broker_port=1883, client_id="python_client"):
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.client_id = client_id
        self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.topics = []
        
    def connect(self):
        try:
            logger.info(f"Connecting to MQTT broker at {self.broker_address}:{self.broker_port}")
            self.client.connect(self.broker_address, self.broker_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("Disconnected from MQTT broker")
    
    def subscribe(self, topic):
        self.topics.append(topic)
        self.client.subscribe(topic)
        logger.info(f"Subscribed to topic: {topic}")
    
    def publish(self, topic, message):
        if isinstance(message, dict):
            message = json.dumps(message)
        self.client.publish(topic, message)
        logger.info(f"Published message to topic {topic}")
    
    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback function"""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            # Re-subscribe to all topics on reconnection
            for topic in self.topics:
                self.client.subscribe(topic)
        else:
            logger.error(f"Failed to connect to MQTT broker with result code {rc}")
    
    def on_message(self, client, userdata, msg):
        """MQTT message callback function"""
        try:
            payload = msg.payload.decode("utf-8")
            logger.info(f"Received message on topic {msg.topic}: {payload}")
            
            # Convert message to JSON
            try:
                payload_json = json.loads(payload)
                # Add data processing logic here
                # For example: self.process_data(msg.topic, payload_json)
            except json.JSONDecodeError:
                logger.warning(f"Received message is not valid JSON: {payload}")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")

# Test usage
if __name__ == "__main__":
    client = MQTTClient()
    if client.connect():
        client.subscribe("sensors/temperature")
        client.subscribe("sensors/humidity")
        client.subscribe("social/twitter")
        
        try:
            # Send test message
            for i in range(5):
                client.publish("sensors/temperature", 
                               json.dumps({"sensor_id": "temp1", "value": 22.5 + i, "unit": "C"}))
                time.sleep(2)
                
            # Keep the program running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            client.disconnect()
