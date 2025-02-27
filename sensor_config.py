"""
Configuration for IoT sensors including types, ranges, and validation rules
"""

SENSOR_TYPES = {
    "air_quality": {
        "units": "AQI",
        "valid_range": (0, 500),
        "thresholds": {
            "good": (0, 50),
            "moderate": (51, 100),
            "unhealthy_sensitive": (101, 150),
            "unhealthy": (151, 200),
            "very_unhealthy": (201, 300),
            "hazardous": (301, 500)
        }
    },
    "temperature": {
        "units": "°C",
        "valid_range": (-50, 100),
        "thresholds": {
            "very_cold": (-50, 0),
            "cold": (0, 15),
            "moderate": (15, 25),
            "warm": (25, 35),
            "hot": (35, 100)
        }
    },
    "humidity": {
        "units": "%",
        "valid_range": (0, 100),
        "thresholds": {
            "very_dry": (0, 20),
            "dry": (20, 40),
            "moderate": (40, 60),
            "humid": (60, 80),
            "very_humid": (80, 100)
        }
    },
    "noise": {
        "units": "dB",
        "valid_range": (0, 200),
        "thresholds": {
            "quiet": (0, 30),
            "moderate": (30, 60),
            "loud": (60, 90),
            "very_loud": (90, 120),
            "dangerous": (120, 200)
        }
    },
    "traffic": {
        "units": "%",
        "valid_range": (0, 100),
        "thresholds": {
            "light": (0, 20),
            "moderate": (20, 40),
            "heavy": (40, 70),
            "congested": (70, 90),
            "gridlock": (90, 100)
        }
    },
    "flood": {
        "units": "mm",
        "valid_range": (0, 1000),
        "thresholds": {
            "normal": (0, 30),
            "attention": (31, 50),
            "alert": (51, 100),
            "danger": (101, 200),
            "critical": (201, 1000)
        },
        "alert_levels": {
            "attention": "Possibilidade de alagamentos pontuais",
            "alert": "Risco de alagamentos em áreas baixas",
            "danger": "Alto risco de enchentes e deslizamentos",
            "critical": "Situação crítica - Evacuação necessária"
        }
    },
    "accidents": {
        "units": "ocorrências/dia",
        "valid_range": (0, 100),
        "thresholds": {
            "baixo": (0, 5),
            "moderado": (6, 15),
            "alto": (16, 30),
            "critico": (31, 100)
        }
    },
    "crime_rate": {
        "units": "ocorrências/dia",
        "valid_range": (0, 1000),
        "thresholds": {
            "baixo": (0, 10),
            "moderado": (11, 30),
            "alto": (31, 50),
            "critico": (51, 1000)
        }
    },
    "energy_consumption": {
        "units": "MW",
        "valid_range": (0, 1000),
        "thresholds": {
            "baixo": (0, 100),
            "normal": (101, 300),
            "alto": (301, 600),
            "critico": (601, 1000)
        }
    },
    "waste_collection": {
        "units": "ton/dia",
        "valid_range": (0, 1000),
        "thresholds": {
            "baixo": (0, 50),
            "normal": (51, 200),
            "alto": (201, 500),
            "critico": (501, 1000)
        }
    },
    "smart_camera": {
        "units": "status",
        "valid_range": (0, 1),
        "thresholds": {
            "offline": (0, 0),
            "online": (1, 1)
        },
        "capabilities": [
            "facial_recognition",
            "motion_detection",
            "license_plate_recognition",
            "crowd_analysis"
        ]
    },
    "drone": {
        "units": "status",
        "valid_range": (0, 1),
        "thresholds": {
            "grounded": (0, 0),
            "patrolling": (1, 1)
        },
        "capabilities": [
            "thermal_imaging",
            "night_vision",
            "aerial_surveillance",
            "incident_tracking"
        ]
    }
}

# Add new geofencing configurations
GEOFENCING_CONFIG = {
    "camera_ranges": {
        "standard": 100,  # meters
        "high_res": 150,  # meters
        "ptz": 200,      # meters
    },
    "perimeters": {
        "Centro": {
            "id": "GF001",
            "coordinates": [
                [-5.188004, -37.344033],
                [-5.187500, -37.343500],
                [-5.188500, -37.344500],
                [-5.188004, -37.344033]
            ],
            "required_coverage": 95  # percentage
        },
        "Zona Norte": {
            "id": "GF002",
            "coordinates": [
                [-5.183612, -37.341157],
                [-5.183000, -37.341000],
                [-5.183800, -37.341800],
                [-5.183612, -37.341157]
            ],
            "required_coverage": 90
        }
    },
    "alert_thresholds": {
        "coverage_gap": 20,  # percentage
        "blind_spot_max_size": 50,  # square meters
        "notification_delay": 300  # seconds
    }
}

# Update STRATEGIC_POINTS with camera coverage information
STRATEGIC_POINTS = {
    "cameras": {
        "Centro": [
            {
                "id": "CAM001",
                "location": {"lat": -5.188004, "lon": -37.344033},
                "type": "ptz",
                "range": "ptz",
                "coverage_direction": 360,
                "status": "active"
            },
            {
                "id": "CAM002",
                "location": {"lat": -5.187500, "lon": -37.343500},
                "type": "high_res",
                "range": "high_res",
                "coverage_direction": 180,
                "status": "active"
            },
            {
                "id": "CAM003",
                "location": {"lat": -5.188500, "lon": -37.344500},
                "type": "commercial"
            }
        ],
        "Zona Norte": [
            {
                "id": "CAM004",
                "location": {"lat": -5.183612, "lon": -37.341157},
                "type": "standard",
                "range": "standard",
                "coverage_direction": 270,
                "status": "active"
            },
            {
                "id": "CAM005",
                "location": {"lat": -5.183000, "lon": -37.341000},
                "type": "residential"
            }
        ],
        "Zona Sul": [
            {"id": "CAM006", "location": {"lat": -5.194283, "lon": -37.345749}, "type": "intersection"},
            {"id": "CAM007", "location": {"lat": -5.194000, "lon": -37.345000}, "type": "commercial"}
        ]
    },
    "drone_zones": {
        "high_risk": [
            {"id": "ZONE001", "name": "Centro Comercial", "coordinates": [
                {"lat": -5.188004, "lon": -37.344033},
                {"lat": -5.187500, "lon": -37.343500},
                {"lat": -5.188500, "lon": -37.344500}
            ]},
            {"id": "ZONE002", "name": "Zona Norte Comercial", "coordinates": [
                {"lat": -5.183612, "lon": -37.341157},
                {"lat": -5.183000, "lon": -37.341000},
                {"lat": -5.183800, "lon": -37.341800}
            ]}
        ],
        "patrol_schedule": {
            "morning": "06:00-09:00",
            "evening": "17:00-20:00",
            "night": "22:00-01:00"
        }
    }
}

# Geographic zones in Mossoró
ZONES = {
    "Centro": {
        "coordinates": {
            "lat": -5.188004,
            "lon": -37.344033
        },
        "sensor_types": ["air_quality", "traffic", "noise", "temperature", "humidity", "flood", "smart_camera", "drone"]
    },
    "Zona Norte": {
        "coordinates": {
            "lat": -5.183612,
            "lon": -37.341157
        },
        "sensor_types": ["air_quality", "traffic", "temperature", "humidity", "flood", "smart_camera", "drone"]
    },
    "Zona Sul": {
        "coordinates": {
            "lat": -5.194283,
            "lon": -37.345749
        },
        "sensor_types": ["air_quality", "traffic", "temperature", "humidity", "flood", "smart_camera"]
    },
    "Zona Leste": {
        "coordinates": {
            "lat": -5.190128,
            "lon": -37.337275
        },
        "sensor_types": ["air_quality", "traffic", "noise", "temperature", "humidity", "flood", "smart_camera"]
    },
    "Zona Oeste": {
        "coordinates": {
            "lat": -5.186821,
            "lon": -37.350836
        },
        "sensor_types": ["air_quality", "traffic", "temperature", "humidity", "flood", "smart_camera"]
    }
}

# Validation rules for sensor data
VALIDATION_RULES = {
    "required_fields": ["value", "unit", "timestamp", "sensor_id", "location"],
    "timestamp_format": "%Y-%m-%dT%H:%M:%S.%f",
    "location_fields": ["zone", "coordinates"],
    "coordinate_ranges": {
        "lat": (-5.2, -5.1),  # Approximate bounds for Mossoró
        "lon": (-37.4, -37.3)
    }
}