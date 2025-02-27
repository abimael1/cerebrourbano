import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from iot_manager import IoTManager

class UrbanMonitor:
    def __init__(self):
        """Initialize the Urban Monitor with IoT integration"""
        self.metrics = {
            'air_quality': {
                'PM2.5': (0, 500),
                'CO2': (300, 2000),
                'NO2': (0, 200),
                'temperature': (15, 40),
                'humidity': (0, 100),
                'air_quality_index': (0, 500)
            },
            'traffic': {
                'congestion_level': (0, 100),
                'average_speed': (0, 80),
                'vehicle_count': (100, 1000)
            },
            'waste': {
                'daily_collection': (1000, 5000),
                'recycling_rate': (0, 100),
                'bin_capacity': (0, 100)
            },
            'noise': {
                'decibel_level': (30, 120),
                'peak_noise': (40, 130),
                'ambient_noise': (20, 100)
            }
        }

        # Initialize IoT Manager
        self.iot_manager = IoTManager()
        try:
            self.iot_manager.connect()
            self.using_real_data = True
        except Exception as e:
            print(f"Failed to connect to IoT network: {e}")
            self.using_real_data = False

    def get_real_time_data(self):
        """Get real-time data from IoT sensors with fallback to simulation"""
        if self.using_real_data:
            iot_data = self.iot_manager.get_latest_data()
            if iot_data:
                return self._process_iot_data(iot_data)

        # Fallback to simulated data if no real data available
        return self.generate_simulated_data()

    def _process_iot_data(self, iot_data):
        """Process raw IoT data into the expected format"""
        current_time = datetime.now()
        processed_data = {
            'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'metrics': {
                'air_quality': {},
                'traffic': {},
                'waste': {},
                'noise': {}
            }
        }

        # Map IoT data to our metrics structure
        for category in processed_data['metrics']:
            if category in iot_data:
                for sensor_id, sensor_data in iot_data[category].items():
                    metric_name = sensor_data.get('type', 'unknown')
                    if metric_name in self.metrics[category]:
                        processed_data['metrics'][category][metric_name] = sensor_data['value']

        # Fill missing metrics with simulated data
        return self._fill_missing_metrics(processed_data)

    def _fill_missing_metrics(self, data):
        """Fill any missing metrics with simulated data"""
        simulated = self.generate_simulated_data()

        for category in self.metrics:
            if category not in data['metrics']:
                data['metrics'][category] = {}

            for metric in self.metrics[category]:
                if metric not in data['metrics'][category]:
                    data['metrics'][category][metric] = simulated['metrics'][category][metric]

        return data

    def generate_simulated_data(self):
        """Generate simulated urban data with realistic patterns"""
        current_time = datetime.now()
        data = {
            'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'metrics': {}
        }

        for category, metrics in self.metrics.items():
            data['metrics'][category] = {}
            for metric, (min_val, max_val) in metrics.items():
                # Add time-based variations
                hour_factor = np.sin(current_time.hour * np.pi / 12) * 0.3 + 1
                base_value = np.random.uniform(min_val, max_val)
                value = base_value * hour_factor

                # Add realistic patterns based on time of day
                if category == 'traffic':
                    # Higher traffic during rush hours
                    if current_time.hour in [8, 9, 17, 18]:
                        value *= 1.5
                elif category == 'air_quality':
                    # Worse air quality during peak hours
                    if 9 <= current_time.hour <= 18:
                        value *= 1.2
                elif category == 'noise':
                    # Higher noise during business hours
                    if 8 <= current_time.hour <= 18:
                        value *= 1.3

                data['metrics'][category][metric] = round(value, 2)

        return data

    def get_historical_data(self, hours=24):
        """Get historical data combining real and simulated data"""
        data = []
        current_time = datetime.now()

        for i in range(hours):
            timestamp = current_time - timedelta(hours=i)
            metrics = self.get_real_time_data()
            metrics['timestamp'] = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            data.append(metrics)

        return data

    def get_alerts(self, current_data):
        """Generate alerts based on thresholds with priority levels"""
        alerts = []
        thresholds = {
            'air_quality': {
                'PM2.5': 150,
                'CO2': 1000,
                'NO2': 100,
                'air_quality_index': 150
            },
            'traffic': {
                'congestion_level': 80,
                'average_speed': 20
            },
            'noise': {
                'decibel_level': 85,
                'peak_noise': 100
            }
        }

        priority_levels = {
            'air_quality': 'Alta',
            'traffic': 'Média',
            'noise': 'Média'
        }

        for category, metrics in current_data['metrics'].items():
            if category in thresholds:
                for metric, value in metrics.items():
                    if metric in thresholds[category]:
                        threshold = thresholds[category][metric]
                        if value > threshold:
                            alerts.append({
                                'category': category,
                                'metric': metric,
                                'value': value,
                                'threshold': threshold,
                                'priority': priority_levels[category],
                                'timestamp': datetime.now().strftime('%H:%M:%S'),
                                'message': f'Alto nível de {metric} em {category}: {value:.2f}'
                            })

        return alerts

    def __del__(self):
        """Cleanup IoT connection on object destruction"""
        if hasattr(self, 'iot_manager'):
            self.iot_manager.disconnect()