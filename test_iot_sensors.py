import time
import json
import paho.mqtt.client as mqtt
from datetime import datetime
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IoTSensorSimulator:
    def __init__(self):
        """Initialize the IoT sensor simulator"""
        self.client = mqtt.Client()
        self.connected = False
        
        # Sensor configurations
        self.sensors = {
            'temperature': {
                'range': (20, 35),
                'unit': '°C',
                'locations': ['Centro', 'Zona Norte', 'Zona Sul', 'Zona Leste', 'Zona Oeste']
            },
            'humidity': {
                'range': (40, 80),
                'unit': '%',
                'locations': ['Centro', 'Zona Norte', 'Zona Sul', 'Zona Leste', 'Zona Oeste']
            },
            'air_quality': {
                'range': (0, 200),
                'unit': 'AQI',
                'locations': ['Centro', 'Zona Norte', 'Zona Sul', 'Zona Leste', 'Zona Oeste']
            },
            'noise': {
                'range': (30, 90),
                'unit': 'dB',
                'locations': ['Centro', 'Zona Norte', 'Zona Sul', 'Zona Leste', 'Zona Oeste']
            },
            'traffic': {
                'range': (0, 100),
                'unit': '%',
                'locations': ['Centro', 'Zona Norte', 'Zona Sul', 'Zona Leste', 'Zona Oeste']
            }
        }

    def connect(self, broker="test.mosquitto.org", port=1883):
        """Connect to MQTT broker"""
        try:
            self.client.connect(broker, port, 60)
            self.client.loop_start()
            self.connected = True
            logger.info(f"Connected to MQTT broker: {broker}:{port}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            self.connected = False

    def generate_sensor_data(self, sensor_type, location):
        """Generate realistic sensor data"""
        min_val, max_val = self.sensors[sensor_type]['range']
        value = random.uniform(min_val, max_val)
        
        # Add time-based variations
        hour = datetime.now().hour
        if sensor_type == 'traffic':
            # Increase traffic during rush hours
            if hour in [8, 9, 17, 18]:
                value = min(value * 1.5, max_val)
        elif sensor_type == 'noise':
            # Increase noise during business hours
            if 8 <= hour <= 18:
                value = min(value * 1.2, max_val)
        elif sensor_type == 'air_quality':
            # Worse air quality during peak hours
            if 9 <= hour <= 18:
                value = min(value * 1.3, max_val)

        return {
            'value': round(value, 2),
            'unit': self.sensors[sensor_type]['unit'],
            'location': {
                'zone': location,
                'coordinates': {
                    'lat': -5.1875 + random.uniform(-0.01, 0.01),
                    'lon': -37.3447 + random.uniform(-0.01, 0.01)
                }
            },
            'status': 'active',
            'battery': random.randint(60, 100)
        }

    def publish_sensor_data(self):
        """Publish sensor data to MQTT topics"""
        if not self.connected:
            logger.warning("Not connected to MQTT broker")
            return

        for sensor_type in self.sensors:
            for location in self.sensors[sensor_type]['locations']:
                sensor_id = f"{location.lower().replace(' ', '_')}_{sensor_type}"
                topic = f"mossoro/sensors/{sensor_id}/{sensor_type}"
                data = self.generate_sensor_data(sensor_type, location)
                
                try:
                    self.client.publish(topic, json.dumps(data))
                    logger.info(f"Published data to {topic}: {data}")
                except Exception as e:
                    logger.error(f"Failed to publish to {topic}: {e}")

    def run(self, interval=5):
        """Run the simulator with specified interval"""
        logger.info(f"Starting IoT sensor simulator with {interval}s interval")
        try:
            while True:
                self.publish_sensor_data()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Stopping simulator...")
            self.stop()

    def stop(self):
        """Stop the simulator"""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        logger.info("Simulator stopped")

if __name__ == "__main__":
    simulator = IoTSensorSimulator()
    simulator.connect()
    simulator.run()
