import paho.mqtt.client as mqtt
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import threading
import queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IoTSensor:
    def __init__(self, sensor_id: str, sensor_type: str, location: Dict[str, Any]):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.location = location
        self.last_reading: Optional[Dict[str, Any]] = None
        self.status = "inactive"
        self.last_update = None

    def update_reading(self, data: Dict[str, Any]) -> None:
        self.last_reading = data
        self.last_update = datetime.now()
        self.status = "active"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sensor_id": self.sensor_id,
            "type": self.sensor_type,
            "location": self.location,
            "last_reading": self.last_reading,
            "status": self.status,
            "last_update": self.last_update.isoformat() if self.last_update else None
        }

class IoTSensorManager:
    def __init__(self):
        self.sensors: Dict[str, IoTSensor] = {}
        self.mqtt_client = mqtt.Client()
        self.data_queue = queue.Queue()
        self.running = False

        # Configure MQTT callbacks
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect

    def add_sensor(self, sensor_id: str, sensor_type: str, location: Dict[str, Any]) -> None:
        """Add a new sensor to the manager"""
        if sensor_id not in self.sensors:
            self.sensors[sensor_id] = IoTSensor(sensor_id, sensor_type, location)
            logger.info(f"Added new sensor: {sensor_id} ({sensor_type})")

    def get_sensor_data(self, sensor_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest data from a specific sensor"""
        if sensor_id in self.sensors:
            return self.sensors[sensor_id].to_dict()
        return None

    def get_all_sensors_data(self) -> List[Dict[str, Any]]:
        """Get data from all sensors"""
        return [sensor.to_dict() for sensor in self.sensors.values()]

    def get_sensors_by_type(self, sensor_type: str) -> List[Dict[str, Any]]:
        """Get all sensors of a specific type"""
        return [sensor.to_dict() for sensor in self.sensors.values() 
                if sensor.sensor_type == sensor_type]

    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            # Subscribe to all sensor topics
            client.subscribe("sensors/#")
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")

    def on_message(self, client, userdata, msg):
        """Callback when message is received"""
        try:
            # Parse topic to get sensor ID and type
            topic_parts = msg.topic.split('/')
            if len(topic_parts) >= 3:
                sensor_id = topic_parts[2]
                payload = json.loads(msg.payload.decode())
                
                # Add to processing queue
                self.data_queue.put((sensor_id, payload))
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON payload received: {msg.payload}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        logger.warning(f"Disconnected from MQTT broker with code: {rc}")
        if rc != 0:
            logger.info("Attempting to reconnect...")
            self.connect()

    def process_data(self) -> None:
        """Process incoming sensor data"""
        while self.running:
            try:
                sensor_id, data = self.data_queue.get(timeout=1.0)
                if sensor_id in self.sensors:
                    self.sensors[sensor_id].update_reading(data)
                    logger.debug(f"Updated sensor {sensor_id} with new data")
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing sensor data: {e}")

    def connect(self, host: str = "localhost", port: int = 1883) -> None:
        """Connect to MQTT broker"""
        try:
            self.mqtt_client.connect(host, port)
            self.running = True
            
            # Start processing thread
            self.process_thread = threading.Thread(target=self.process_data)
            self.process_thread.daemon = True
            self.process_thread.start()
            
            # Start MQTT loop in background
            self.mqtt_client.loop_start()
            
            logger.info(f"Connected to MQTT broker at {host}:{port}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")

    def disconnect(self) -> None:
        """Disconnect from MQTT broker"""
        self.running = False
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        logger.info("Disconnected from MQTT broker")

    def validate_sensor_data(self, data: Dict[str, Any]) -> bool:
        """Validate incoming sensor data"""
        required_fields = ['value', 'unit', 'timestamp']
        return all(field in data for field in required_fields)
