import paho.mqtt.client as mqtt
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from sensor_processor import SensorDataProcessor

class IoTManager:
    def __init__(self):
        """Inicializa o gerenciador IoT"""
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.sensor_data = {}
        self.callbacks = {}
        self.processor = SensorDataProcessor()

        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Buffer para dados dos sensores
        self.data_buffer = {
            'temperature': [],
            'humidity': [],
            'air_quality': [],
            'noise': [],
            'traffic': []
        }
        self.buffer_size = 1000  # Aumentado para mais histórico
        self.connected = False
        self.reconnect_delay = 5  # segundos
        self.max_reconnect_attempts = 5

    def connect(self, broker: str = "test.mosquitto.org", port: int = 1883, keepalive: int = 60) -> None:
        """Conecta ao broker MQTT com reconexão automática"""
        self.broker = broker
        self.port = port
        self.keepalive = keepalive

        try:
            if self.client.is_connected():
                self.logger.info("Já conectado ao broker MQTT")
                return

            self.logger.info(f"Conectando ao broker MQTT: {broker}:{port}")
            self.client.connect(broker, port, keepalive)
            self.client.loop_start()
            self.connected = True
        except Exception as e:
            self.logger.error(f"Erro ao conectar ao broker MQTT: {e}")
            self.connected = False
            self._try_reconnect()

    def _try_reconnect(self):
        """Tenta reconectar com backoff exponencial"""
        attempts = 0
        while not self.connected and attempts < self.max_reconnect_attempts:
            try:
                self.logger.info(f"Tentativa de reconexão {attempts + 1}/{self.max_reconnect_attempts}")
                self.client.reconnect()
                self.connected = True
                self.logger.info("Reconexão bem sucedida")
                return
            except Exception as e:
                attempts += 1
                self.logger.error(f"Falha na reconexão: {e}")
                self.reconnect_delay *= 2  # Backoff exponencial
                if attempts < self.max_reconnect_attempts:
                    self.logger.info(f"Aguardando {self.reconnect_delay}s antes da próxima tentativa")
                    time.sleep(self.reconnect_delay)

        if not self.connected:
            self.logger.error("Máximo de tentativas de reconexão atingido")
            raise ConnectionError("Não foi possível reconectar ao broker MQTT")

    def on_disconnect(self, client, userdata, rc):
        """Handler para desconexões com tentativa de reconexão"""
        self.logger.warning(f"Desconectado do broker MQTT, código: {rc}")
        self.connected = False

        if rc != 0:
            self.logger.error("Desconexão inesperada")
            self._try_reconnect()

    def on_connect(self, client, userdata, flags, rc):
        """Callback quando conectado ao broker com validação do status"""
        if rc == 0:
            self.logger.info("Conectado ao broker MQTT com sucesso")
            self.connected = True
            self._subscribe_to_topics()
        else:
            error_messages = {
                1: "Protocolo incorreto",
                2: "Identificador inválido",
                3: "Servidor indisponível",
                4: "Credenciais inválidas",
                5: "Não autorizado"
            }
            self.logger.error(f"Falha na conexão: {error_messages.get(rc, f'Erro desconhecido: {rc}')}")
            self.connected = False

    def _subscribe_to_topics(self):
        """Inscreve nos tópicos dos sensores com validação"""
        topics = [
            ("mossoro/sensors/+/temperature", 0),
            ("mossoro/sensors/+/humidity", 0),
            ("mossoro/sensors/+/air_quality", 0),
            ("mossoro/sensors/+/noise", 0),
            ("mossoro/sensors/+/traffic", 0)
        ]

        for topic, qos in topics:
            try:
                result, mid = self.client.subscribe(topic, qos)
                if result == mqtt.MQTT_ERR_SUCCESS:
                    self.logger.info(f"Inscrito no tópico: {topic}")
                else:
                    self.logger.error(f"Erro ao inscrever no tópico {topic}: {result}")
            except Exception as e:
                self.logger.error(f"Exceção ao inscrever no tópico {topic}: {e}")

    def validate_sensor_data(self, data: dict, sensor_type: str) -> bool:
        """Validação aprimorada dos dados dos sensores"""
        try:
            # Validação básica de estrutura
            required_fields = {'value', 'unit', 'location', 'timestamp'}
            if not all(field in data for field in required_fields):
                self.logger.warning(f"Dados de sensor faltando campos obrigatórios: {data}")
                return False

            # Validação de localização
            if not isinstance(data['location'], dict) or \
               not all(k in data['location'] for k in ['zone', 'coordinates']):
                self.logger.warning(f"Formato de localização inválido: {data['location']}")
                return False

            # Validação de coordenadas
            coords = data['location']['coordinates']
            if not isinstance(coords, dict) or \
               not all(k in coords for k in ['lat', 'lon']):
                self.logger.warning(f"Coordenadas inválidas: {coords}")
                return False

            # Validação de valores por tipo de sensor
            ranges = {
                'temperature': (-50, 100),
                'humidity': (0, 100),
                'air_quality': (0, 500),
                'noise': (0, 200),
                'traffic': (0, 100)
            }

            if sensor_type in ranges:
                min_val, max_val = ranges[sensor_type]
                value = float(data['value'])
                if not (min_val <= value <= max_val):
                    self.logger.warning(
                        f"Valor fora do range para {sensor_type}: {value} "
                        f"(range: {min_val}-{max_val})"
                    )
                    return False

            return True
        except Exception as e:
            self.logger.error(f"Erro na validação dos dados do sensor: {e}")
            return False

    def on_message(self, client, userdata, msg):
        """Processa mensagens com validação e processamento aprimorados"""
        try:
            payload = json.loads(msg.payload.decode())
            topic_parts = msg.topic.split('/')
            sensor_type = topic_parts[-1]
            sensor_id = topic_parts[-2]

            # Validar dados antes de processar
            if not self.validate_sensor_data(payload, sensor_type):
                return

            # Processar dados com o SensorDataProcessor
            is_valid, error_msg = self.processor.validate_sensor_data(payload)
            if not is_valid:
                self.logger.warning(f"Dados inválidos para sensor {sensor_id}: {error_msg}")
                return

            # Adicionar informações de processamento
            processed_data = self.processor.process_sensor_data(payload)

            # Atualizar buffer e dados atuais
            if sensor_type in self.data_buffer:
                self.data_buffer[sensor_type].append(processed_data)
                if len(self.data_buffer[sensor_type]) > self.buffer_size:
                    self.data_buffer[sensor_type].pop(0)

            if sensor_type not in self.sensor_data:
                self.sensor_data[sensor_type] = {}

            self.sensor_data[sensor_type][sensor_id] = processed_data

            # Executar callbacks registrados
            if sensor_type in self.callbacks:
                for callback in self.callbacks[sensor_type]:
                    try:
                        callback(processed_data)
                    except Exception as e:
                        self.logger.error(f"Erro no callback para {sensor_type}: {e}")

            self.logger.debug(f"Dados processados para sensor {sensor_id} ({sensor_type})")

        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar mensagem JSON: {msg.payload}: {e}")
        except Exception as e:
            self.logger.error(f"Erro ao processar mensagem: {e}")

    def get_latest_data(self, sensor_type: Optional[str] = None) -> Dict[str, Any]:
        """Retorna os dados mais recentes dos sensores com validação"""
        try:
            if sensor_type and sensor_type not in self.data_buffer:
                self.logger.warning(f"Tipo de sensor inválido: {sensor_type}")
                return {}

            if sensor_type:
                return self.sensor_data.get(sensor_type, {})
            return self.sensor_data
        except Exception as e:
            self.logger.error(f"Erro ao obter dados recentes: {e}")
            return {}

    def get_buffer_data(self, sensor_type: str, limit: Optional[int] = None) -> list:
        """Retorna dados do buffer para um tipo específico de sensor"""
        try:
            if sensor_type not in self.data_buffer:
                self.logger.warning(f"Tipo de sensor inválido para buffer: {sensor_type}")
                return []

            data = self.data_buffer[sensor_type]
            if limit and isinstance(limit, int) and limit > 0:
                return data[-limit:]
            return data
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do buffer: {e}")
            return []

    def register_callback(self, sensor_type: str, callback: Callable) -> None:
        """Registra um callback para um tipo específico de sensor"""
        if not callable(callback):
            raise ValueError("Callback deve ser uma função callable")

        if sensor_type not in self.callbacks:
            self.callbacks[sensor_type] = []
        self.callbacks[sensor_type].append(callback)
        self.logger.info(f"Callback registrado para {sensor_type}")

    def is_connected(self) -> bool:
        """Verifica se está conectado ao broker"""
        return self.connected and self.client.is_connected()

    def disconnect(self):
        """Desconecta do broker MQTT com limpeza"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            self.logger.info("Desconectado do broker MQTT")
        except Exception as e:
            self.logger.error(f"Erro ao desconectar: {e}")
        finally:
            self.sensor_data = {}
            self.data_buffer = {k: [] for k in self.data_buffer.keys()}

# Exemplo de formato de mensagem esperado dos sensores:
"""
{
    "value": 25.6,
    "unit": "°C",
    "location": {
        "zone": "Norte",
        "neighborhood": "Santo Antônio",
        "coordinates": {
            "lat": -5.1875,
            "lon": -37.3447
        }
    },
    "status": "active",
    "battery": 85
}
"""