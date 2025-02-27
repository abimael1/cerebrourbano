from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import logging
from sensor_config import SENSOR_TYPES, ZONES, VALIDATION_RULES

logger = logging.getLogger(__name__)

class SensorDataProcessor:
    @staticmethod
    def validate_sensor_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validação aprimorada de dados dos sensores
        Retorna (is_valid, error_message)
        """
        try:
            # Verificar campos obrigatórios
            for field in VALIDATION_RULES["required_fields"]:
                if field not in data:
                    return False, f"Campo obrigatório ausente: {field}"

            # Validar tipo de sensor
            sensor_type = data.get("sensor_type")
            if sensor_type not in SENSOR_TYPES:
                return False, f"Tipo de sensor inválido: {sensor_type}"

            # Validar valor e unidade
            try:
                value = float(data["value"])
                valid_range = SENSOR_TYPES[sensor_type]["valid_range"]
                if not (valid_range[0] <= value <= valid_range[1]):
                    return False, f"Valor {value} fora do range válido {valid_range}"
            except (ValueError, TypeError):
                return False, "Valor do sensor inválido"

            # Validar timestamp
            try:
                datetime.strptime(data["timestamp"], VALIDATION_RULES["timestamp_format"])
            except ValueError:
                return False, "Formato de timestamp inválido"

            # Validar localização
            location = data.get("location", {})
            if not all(field in location for field in VALIDATION_RULES["location_fields"]):
                return False, "Formato de localização inválido"

            # Validar coordenadas
            coords = location.get("coordinates", {})
            lat_range = VALIDATION_RULES["coordinate_ranges"]["lat"]
            lon_range = VALIDATION_RULES["coordinate_ranges"]["lon"]

            lat = coords.get("lat")
            lon = coords.get("lon")

            if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
                return False, "Coordenadas inválidas"

            if not (lat_range[0] <= lat <= lat_range[1] and 
                    lon_range[0] <= lon <= lon_range[1]):
                return False, "Coordenadas fora do range válido para Mossoró"

            # Validar zona
            if location["zone"] not in ZONES:
                return False, f"Zona inválida: {location['zone']}"

            return True, None

        except Exception as e:
            return False, f"Erro de validação: {str(e)}"

    @staticmethod
    def process_sensor_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa e enriquece dados dos sensores com informações adicionais
        """
        try:
            sensor_type = data["sensor_type"]
            value = float(data["value"])

            # Determinar categoria baseada nos thresholds
            thresholds = SENSOR_TYPES[sensor_type]["thresholds"]
            category = next(
                (cat for cat, (min_val, max_val) in thresholds.items()
                 if min_val <= value <= max_val),
                "unknown"
            )

            # Calcular tendência se houver dados históricos
            trend = "stable"  # Implementar cálculo de tendência se necessário

            # Adicionar informações processadas
            processed_data = {
                **data,
                "processed_timestamp": datetime.now().isoformat(),
                "status_category": category,
                "trend": trend,
                "unit": SENSOR_TYPES[sensor_type]["units"]
            }

            return processed_data

        except Exception as e:
            logger.error(f"Erro ao processar dados do sensor: {e}")
            return data

    @staticmethod
    def get_zone_summary(zone: str) -> Dict[str, Any]:
        """
        Obtém resumo de todos os tipos de sensores para uma zona específica
        """
        try:
            if zone not in ZONES:
                raise ValueError(f"Zona inválida: {zone}")

            return {
                "zone": zone,
                "coordinates": ZONES[zone]["coordinates"],
                "available_sensors": ZONES[zone]["sensor_types"],
                "summary_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao obter resumo da zona: {e}")
            return {}

    @staticmethod
    def get_sensor_thresholds(sensor_type: str) -> Dict[str, Tuple[int, int]]:
        """
        Obtém valores de threshold para um tipo específico de sensor
        """
        try:
            if sensor_type not in SENSOR_TYPES:
                raise ValueError(f"Tipo de sensor inválido: {sensor_type}")

            return SENSOR_TYPES[sensor_type]["thresholds"]
        except Exception as e:
            logger.error(f"Erro ao obter thresholds do sensor: {e}")
            return {}

    @staticmethod
    def validate_zone_sensors(zone: str, sensor_data: Dict[str, Any]) -> bool:
        """
        Valida se os sensores em uma zona estão funcionando corretamente
        """
        try:
            if zone not in ZONES:
                return False

            expected_sensors = set(ZONES[zone]["sensor_types"])
            actual_sensors = set(sensor_data.keys())

            return expected_sensors.issubset(actual_sensors)
        except Exception as e:
            logger.error(f"Erro ao validar sensores da zona: {e}")
            return False