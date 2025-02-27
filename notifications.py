"""
Sistema de notificações e alertas para o Urban Brain
"""
from datetime import datetime
import json
import os

class NotificationSystem:
    def __init__(self):
        self.alerts_history = []
        self.emergency_contacts = {
            "police": "190",
            "ambulance": "192",
            "fire": "193"
        }
        
    def create_alert(self, alert_type, message, severity, location):
        """Criar novo alerta"""
        alert = {
            "id": len(self.alerts_history) + 1,
            "type": alert_type,
            "message": message,
            "severity": severity,
            "location": location,
            "timestamp": datetime.now().isoformat(),
            "status": "active"
        }
        self.alerts_history.append(alert)
        return alert

    def get_active_alerts(self):
        """Retornar alertas ativos"""
        return [alert for alert in self.alerts_history if alert["status"] == "active"]

    def get_alerts_by_type(self, alert_type):
        """Filtrar alertas por tipo"""
        return [alert for alert in self.alerts_history if alert["type"] == alert_type]

    def mark_alert_resolved(self, alert_id):
        """Marcar alerta como resolvido"""
        for alert in self.alerts_history:
            if alert["id"] == alert_id:
                alert["status"] = "resolved"
                alert["resolved_at"] = datetime.now().isoformat()
                return True
        return False

    def get_emergency_contact(self, service):
        """Obter contato de emergência"""
        return self.emergency_contacts.get(service)

class EmergencySystem:
    def __init__(self):
        self.active_units = {}
        self.emergency_history = []
        
    def dispatch_unit(self, unit_type, location, incident_type):
        """Despachar unidade de emergência"""
        dispatch = {
            "unit_id": len(self.active_units) + 1,
            "type": unit_type,
            "location": location,
            "incident_type": incident_type,
            "status": "dispatched",
            "dispatch_time": datetime.now().isoformat()
        }
        self.active_units[dispatch["unit_id"]] = dispatch
        self.emergency_history.append(dispatch)
        return dispatch

    def update_unit_status(self, unit_id, new_status, location=None):
        """Atualizar status da unidade"""
        if unit_id in self.active_units:
            self.active_units[unit_id]["status"] = new_status
            if location:
                self.active_units[unit_id]["location"] = location
            return True
        return False

    def get_active_units(self):
        """Retornar unidades ativas"""
        return self.active_units

    def get_unit_location(self, unit_id):
        """Obter localização da unidade"""
        unit = self.active_units.get(unit_id)
        return unit["location"] if unit else None

class PredictiveAnalysis:
    def __init__(self):
        self.risk_zones = {}
        self.incident_patterns = {}
        
    def update_risk_assessment(self, zone, incidents):
        """Atualizar avaliação de risco para uma zona"""
        risk_score = self._calculate_risk_score(incidents)
        self.risk_zones[zone] = {
            "risk_score": risk_score,
            "last_updated": datetime.now().isoformat(),
            "incident_count": len(incidents)
        }
        return self.risk_zones[zone]

    def _calculate_risk_score(self, incidents):
        """Calcular pontuação de risco baseado em incidentes"""
        # Implementação simplificada - em produção usar modelo ML
        weights = {
            "robbery": 0.4,
            "assault": 0.3,
            "vandalism": 0.2,
            "other": 0.1
        }
        
        score = 0
        for incident in incidents:
            score += weights.get(incident["type"], weights["other"])
        return min(score * 100, 100)  # Normalizar para 0-100

    def get_high_risk_zones(self, threshold=70):
        """Obter zonas de alto risco"""
        return {
            zone: data for zone, data in self.risk_zones.items()
            if data["risk_score"] >= threshold
        }

    def suggest_patrol_route(self, current_location, num_points=5):
        """Sugerir rota de patrulha baseada em riscos"""
        high_risk = self.get_high_risk_zones()
        # Implementação simplificada - em produção usar algoritmo de roteamento
        return list(high_risk.keys())[:num_points]

    def analyze_patterns(self, timeframe="daily"):
        """Analisar padrões de incidentes"""
        # Implementação simplificada - em produção usar análise estatística
        return {
            "peak_hours": ["18:00-22:00", "00:00-02:00"],
            "high_risk_days": ["Friday", "Saturday"],
            "common_types": ["robbery", "vandalism"]
        }
