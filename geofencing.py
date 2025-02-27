"""
Geofencing module for managing smart camera coverage areas and virtual perimeters
"""
import numpy as np
from shapely.geometry import Polygon, Point, mapping
from shapely.ops import unary_union
import json
from datetime import datetime

class GeofencingManager:
    def __init__(self):
        self.geofences = {}
        self.camera_coverage = {}
        
    def create_geofence(self, fence_id: str, coordinates: list, name: str = None):
        """Create a new geofence area"""
        try:
            polygon = Polygon(coordinates)
            self.geofences[fence_id] = {
                "polygon": polygon,
                "name": name or fence_id,
                "created_at": datetime.now().isoformat(),
                "coverage_status": "uncovered"
            }
            return True
        except Exception as e:
            print(f"Error creating geofence: {str(e)}")
            return False
            
    def calculate_camera_coverage(self, camera_id: str, location: dict, range_meters: float):
        """Calculate coverage area for a camera"""
        try:
            # Create circular coverage area
            point = Point(location['lon'], location['lat'])
            coverage = point.buffer(range_meters * 0.00001)  # Rough conversion to degrees
            
            self.camera_coverage[camera_id] = {
                "area": coverage,
                "location": location,
                "range": range_meters,
                "updated_at": datetime.now().isoformat()
            }
            return True
        except Exception as e:
            print(f"Error calculating camera coverage: {str(e)}")
            return False
            
    def find_coverage_gaps(self):
        """Find areas within geofences that aren't covered by cameras"""
        try:
            # Combine all camera coverage areas
            all_coverage = unary_union([
                coverage["area"] for coverage in self.camera_coverage.values()
            ])
            
            gaps = []
            for fence_id, fence in self.geofences.items():
                # Find uncovered areas
                uncovered = fence["polygon"].difference(all_coverage)
                if not uncovered.is_empty:
                    gaps.append({
                        "fence_id": fence_id,
                        "fence_name": fence["name"],
                        "uncovered_area": mapping(uncovered),
                        "coverage_percentage": (
                            1 - (uncovered.area / fence["polygon"].area)
                        ) * 100
                    })
                    
            return gaps
        except Exception as e:
            print(f"Error finding coverage gaps: {str(e)}")
            return []
            
    def get_coverage_status(self):
        """Get current coverage status for all geofences"""
        coverage_status = []
        gaps = self.find_coverage_gaps()
        
        for fence_id, fence in self.geofences.items():
            gap = next((g for g in gaps if g["fence_id"] == fence_id), None)
            
            status = {
                "fence_id": fence_id,
                "name": fence["name"],
                "coverage": "complete" if not gap else "partial",
                "coverage_percentage": 100 if not gap else gap["coverage_percentage"]
            }
            coverage_status.append(status)
            
        return coverage_status
        
    def generate_optimization_suggestions(self):
        """Generate suggestions for optimal camera placement"""
        gaps = self.find_coverage_gaps()
        suggestions = []
        
        for gap in gaps:
            if gap["coverage_percentage"] < 80:  # Threshold for suggesting new cameras
                suggestions.append({
                    "fence_name": gap["fence_name"],
                    "current_coverage": gap["coverage_percentage"],
                    "suggestion": "Additional camera coverage needed",
                    "priority": "high" if gap["coverage_percentage"] < 50 else "medium"
                })
                
        return suggestions
