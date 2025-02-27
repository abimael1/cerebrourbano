"""
Advanced AI analysis module for urban monitoring using Anthropic's Claude model
"""
import os
import logging
from datetime import datetime
import anthropic
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        try:
            self.client = anthropic.Anthropic()
            # Note: claude-3-sonnet-20240229 is used as it's the most recent model as of deployment
            self.model = "claude-3-sonnet-20240229"
            logger.info("AI Analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI Analyzer: {e}")
            raise

    def analyze_incident_patterns(self, incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in urban incidents using AI"""
        try:
            prompt = f"""
            Analyze the following urban incidents and identify patterns:
            {incidents}
            
            Provide insights about:
            1. Common patterns
            2. Risk factors
            3. Preventive measures
            4. Predicted hotspots
            
            Format the response as JSON with these keys:
            patterns, risk_factors, preventive_measures, hotspots
            """

            response = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return response.content

        except Exception as e:
            logger.error(f"Error analyzing incidents: {e}")
            return {
                "patterns": [],
                "risk_factors": [],
                "preventive_measures": [],
                "hotspots": []
            }

    def generate_threat_assessment(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered threat assessment"""
        try:
            prompt = f"""
            Analyze this urban sensor data and assess potential threats:
            {sensor_data}
            
            Consider:
            1. Immediate threats
            2. Emerging risks
            3. Priority levels
            4. Recommended actions
            
            Format as JSON with keys:
            immediate_threats, emerging_risks, priority_levels, recommended_actions
            """

            response = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return response.content

        except Exception as e:
            logger.error(f"Error generating threat assessment: {e}")
            return {
                "immediate_threats": [],
                "emerging_risks": [],
                "priority_levels": [],
                "recommended_actions": []
            }

    def generate_smart_report(self, data: Dict[str, Any]) -> str:
        """Generate natural language report from urban data"""
        try:
            prompt = f"""
            Create a detailed but concise report from this urban monitoring data:
            {data}
            
            Include:
            1. Key findings
            2. Notable trends
            3. Areas of concern
            4. Recommendations
            
            Format as a clear, professional report in Brazilian Portuguese.
            """

            response = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return "Não foi possível gerar o relatório devido a um erro técnico."

    def predict_incidents(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict potential incidents based on historical data"""
        try:
            prompt = f"""
            Based on this historical urban data, predict potential incidents:
            {historical_data}
            
            Analyze:
            1. Likely incident types
            2. Probable locations
            3. Time patterns
            4. Risk levels
            
            Format as JSON with keys:
            predicted_incidents, locations, time_patterns, risk_levels
            """

            response = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return response.content

        except Exception as e:
            logger.error(f"Error predicting incidents: {e}")
            return {
                "predicted_incidents": [],
                "locations": [],
                "time_patterns": [],
                "risk_levels": []
            }
