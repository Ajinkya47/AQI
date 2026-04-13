"""
Route optimization engine.
"""

import math
from typing import Dict, List, Tuple
import random

from backend.models.schemas import (
    Coordinates,
    OptimizedRoute,
    RouteWaypoint,
    RouteSavings,
    RouteComparison,
    RouteComparisonItem,
    CongestionLevel,
    RoutePreference
)


class RouteOptimizer:
    """Optimize routes based on pollution and traffic data."""
    
    def __init__(self):
        # Scoring weights
        self.weights = {
            "fastest": {"time": 0.8, "aqi": 0.1, "distance": 0.1},
            "cleanest": {"time": 0.1, "aqi": 0.8, "distance": 0.1},
            "balanced": {"time": 0.4, "aqi": 0.4, "distance": 0.2}
        }
    
    def optimize(
        self,
        origin: Coordinates,
        destination: Coordinates,
        aqi_data: List[Dict],
        traffic_data: Dict,
        preference: RoutePreference = RoutePreference.BALANCED
    ) -> Dict:
        """
        Find the optimal route based on AQI and traffic.
        
        Generates multiple route alternatives and scores them.
        """
        # Generate route alternatives
        routes = self._generate_routes(origin, destination, aqi_data, traffic_data)
        
        # Score routes based on preference
        weights = self.weights[preference.value]
        scored_routes = []
        
        for route in routes:
            score = self._calculate_score(route, weights)
            scored_routes.append((score, route))
        
        # Sort by score (higher is better)
        scored_routes.sort(key=lambda x: x[0], reverse=True)
        
        recommended = scored_routes[0][1]
        alternatives = [r[1] for r in scored_routes[1:]]
        
        # Calculate savings compared to fastest route
        fastest = min(routes, key=lambda r: r.estimated_time_minutes)
        savings = RouteSavings(
            time_saved_minutes=fastest.estimated_time_minutes - recommended.estimated_time_minutes,
            pollution_reduction_percent=self._calc_pollution_reduction(
                fastest.average_aqi, recommended.average_aqi
            ),
            distance_difference_km=round(
                recommended.total_distance_km - fastest.total_distance_km, 2
            )
        )
        
        return {
            "recommended": recommended,
            "alternatives": alternatives,
            "savings": savings
        }
    
    def compare_routes(
        self,
        origin: Coordinates,
        destination: Coordinates,
        aqi_data: List[Dict],
        traffic_data: Dict
    ) -> RouteComparison:
        """Compare all available routes."""
        routes = self._generate_routes(origin, destination, aqi_data, traffic_data)
        
        # Score with balanced weights
        scored_routes = []
        for route in routes:
            score = self._calculate_score(route, self.weights["balanced"])
            scored_routes.append((score, route))
        
        scored_routes.sort(key=lambda x: x[0], reverse=True)
        
        comparison_items = []
        for rank, (score, route) in enumerate(scored_routes, 1):
            pros, cons = self._get_pros_cons(route, routes)
            comparison_items.append(RouteComparisonItem(
                route=route,
                rank=rank,
                pros=pros,
                cons=cons
            ))
        
        # Generate recommendation
        best_route = scored_routes[0][1]
        recommendation = self._generate_recommendation(best_route)
        
        return RouteComparison(
            origin=origin,
            destination=destination,
            routes=comparison_items,
            recommendation=recommendation
        )
    
    def get_city_suggestions(self, city: str, zone_aqi: Dict) -> Dict:
        """Get general suggestions for avoiding pollution in a city."""
        avoid_zones = []
        recommended_zones = []
        
        for zone, data in zone_aqi.items():
            if data["aqi"] > 150:
                avoid_zones.append({
                    "zone": zone,
                    "aqi": data["aqi"],
                    "reason": "High pollution levels"
                })
            elif data["aqi"] < 80:
                recommended_zones.append({
                    "zone": zone,
                    "aqi": data["aqi"],
                    "reason": "Good air quality"
                })
        
        return {
            "city": city,
            "avoid_zones": avoid_zones,
            "recommended_zones": recommended_zones,
            "general_advice": self._get_general_advice(zone_aqi)
        }
    
    def _generate_routes(
        self,
        origin: Coordinates,
        destination: Coordinates,
        aqi_data: List[Dict],
        traffic_data: Dict
    ) -> List[OptimizedRoute]:
        """Generate multiple route alternatives."""
        routes = []
        
        # Direct route
        routes.append(self._create_route(
            name="Direct Route",
            origin=origin,
            destination=destination,
            aqi_data=aqi_data,
            traffic_data=traffic_data,
            detour_factor=1.0,
            reason="Shortest distance"
        ))
        
        # Low pollution route (avoids high AQI areas)
        routes.append(self._create_route(
            name="Low Pollution Route",
            origin=origin,
            destination=destination,
            aqi_data=aqi_data,
            traffic_data=traffic_data,
            detour_factor=1.2,
            prefer_low_aqi=True,
            reason="Minimizes pollution exposure"
        ))
        
        # Fast route (prioritizes speed)
        routes.append(self._create_route(
            name="Fastest Route",
            origin=origin,
            destination=destination,
            aqi_data=aqi_data,
            traffic_data=traffic_data,
            detour_factor=1.1,
            prefer_low_traffic=True,
            reason="Minimizes travel time"
        ))
        
        return routes
    
    def _create_route(
        self,
        name: str,
        origin: Coordinates,
        destination: Coordinates,
        aqi_data: List[Dict],
        traffic_data: Dict,
        detour_factor: float = 1.0,
        prefer_low_aqi: bool = False,
        prefer_low_traffic: bool = False,
        reason: str = ""
    ) -> OptimizedRoute:
        """Create a route with waypoints."""
        # Calculate base distance
        distance = self._haversine_distance(
            (origin.latitude, origin.longitude),
            (destination.latitude, destination.longitude)
        ) * detour_factor
        
        # Generate waypoints
        waypoints = []
        num_waypoints = 5
        
        for i in range(num_waypoints):
            fraction = i / (num_waypoints - 1)
            lat = origin.latitude + (destination.latitude - origin.latitude) * fraction
            lon = origin.longitude + (destination.longitude - origin.longitude) * fraction
            
            # Adjust waypoints based on preference
            if prefer_low_aqi:
                # Slight deviation to avoid high AQI
                lat += random.uniform(-0.01, 0.01)
                lon += random.uniform(-0.01, 0.01)
            
            # Get AQI for this point
            if aqi_data and i < len(aqi_data):
                point_aqi = aqi_data[i].get("aqi", random.randint(50, 150))
            else:
                point_aqi = random.randint(50, 150)
            
            # Reduce AQI if we're preferring low AQI routes
            if prefer_low_aqi:
                point_aqi = max(30, point_aqi - 30)
            
            # Traffic level
            base_traffic = traffic_data.get("duration_in_traffic_minutes", 30)
            if prefer_low_traffic:
                traffic_level = CongestionLevel.LOW
            elif base_traffic > 45:
                traffic_level = CongestionLevel.HIGH
            elif base_traffic > 30:
                traffic_level = CongestionLevel.MODERATE
            else:
                traffic_level = CongestionLevel.LOW
            
            waypoints.append(RouteWaypoint(
                coordinates=Coordinates(latitude=lat, longitude=lon),
                aqi=point_aqi,
                traffic_level=traffic_level
            ))
        
        # Calculate metrics
        aqi_values = [wp.aqi for wp in waypoints]
        avg_aqi = sum(aqi_values) / len(aqi_values)
        max_aqi = max(aqi_values)
        
        # Estimate time based on distance and traffic
        base_time = (distance / 40) * 60  # 40 km/h average
        traffic_multiplier = traffic_data.get("duration_in_traffic_minutes", base_time) / max(1, traffic_data.get("duration_minutes", base_time))
        estimated_time = base_time * traffic_multiplier
        
        if prefer_low_traffic:
            estimated_time *= 0.85
        if prefer_low_aqi:
            estimated_time *= 1.1  # Slightly longer for cleaner route
        
        # Pollution exposure score (lower is better)
        exposure_score = avg_aqi * estimated_time / 100
        
        return OptimizedRoute(
            name=name,
            waypoints=waypoints,
            total_distance_km=round(distance, 2),
            estimated_time_minutes=int(estimated_time),
            average_aqi=round(avg_aqi, 1),
            max_aqi=max_aqi,
            pollution_exposure_score=round(exposure_score, 2),
            recommendation_reason=reason
        )
    
    def _calculate_score(self, route: OptimizedRoute, weights: Dict) -> float:
        """Calculate overall score for a route."""
        # Normalize metrics (lower is better for all)
        time_score = 100 / max(1, route.estimated_time_minutes)
        aqi_score = 100 / max(1, route.average_aqi)
        distance_score = 100 / max(1, route.total_distance_km)
        
        # Weighted sum
        score = (
            weights["time"] * time_score +
            weights["aqi"] * aqi_score +
            weights["distance"] * distance_score
        )
        
        return score
    
    def _calc_pollution_reduction(self, baseline_aqi: float, route_aqi: float) -> float:
        """Calculate percentage reduction in pollution exposure."""
        if baseline_aqi == 0:
            return 0.0
        reduction = ((baseline_aqi - route_aqi) / baseline_aqi) * 100
        return round(max(0, reduction), 1)
    
    def _get_pros_cons(
        self,
        route: OptimizedRoute,
        all_routes: List[OptimizedRoute]
    ) -> Tuple[List[str], List[str]]:
        """Generate pros and cons for a route."""
        pros = []
        cons = []
        
        # Compare with other routes
        avg_time = sum(r.estimated_time_minutes for r in all_routes) / len(all_routes)
        avg_aqi = sum(r.average_aqi for r in all_routes) / len(all_routes)
        avg_dist = sum(r.total_distance_km for r in all_routes) / len(all_routes)
        
        # Time
        if route.estimated_time_minutes < avg_time * 0.9:
            pros.append("Faster than average")
        elif route.estimated_time_minutes > avg_time * 1.1:
            cons.append("Slower than average")
        
        # AQI
        if route.average_aqi < avg_aqi * 0.9:
            pros.append("Lower pollution exposure")
        elif route.average_aqi > avg_aqi * 1.1:
            cons.append("Higher pollution exposure")
        
        # Distance
        if route.total_distance_km < avg_dist * 0.95:
            pros.append("Shorter distance")
        elif route.total_distance_km > avg_dist * 1.05:
            cons.append("Longer distance")
        
        # Add specific observations
        if route.max_aqi < 100:
            pros.append("No high-pollution zones")
        if route.max_aqi > 150:
            cons.append(f"Passes through area with AQI {route.max_aqi}")
        
        return pros or ["Balanced option"], cons or ["No significant drawbacks"]
    
    def _generate_recommendation(self, best_route: OptimizedRoute) -> str:
        """Generate a recommendation string."""
        if best_route.average_aqi < 80:
            return f"Take the {best_route.name} for the healthiest journey with an average AQI of {best_route.average_aqi:.0f}"
        elif best_route.estimated_time_minutes < 20:
            return f"The {best_route.name} is quick at {best_route.estimated_time_minutes} minutes with acceptable air quality"
        else:
            return f"The {best_route.name} offers the best balance of speed and air quality"
    
    def _get_general_advice(self, zone_aqi: Dict) -> List[str]:
        """Generate general travel advice based on city conditions."""
        advice = []
        
        avg_aqi = sum(d["aqi"] for d in zone_aqi.values()) / len(zone_aqi)
        
        if avg_aqi < 80:
            advice.append("Overall air quality is good - outdoor activities are recommended")
        elif avg_aqi < 120:
            advice.append("Moderate air quality - consider shorter outdoor exposure")
        else:
            advice.append("Air quality is concerning - minimize outdoor activities")
        
        # Find best and worst zones
        best_zone = min(zone_aqi.items(), key=lambda x: x[1]["aqi"])
        worst_zone = max(zone_aqi.items(), key=lambda x: x[1]["aqi"])
        
        advice.append(f"Best area: {best_zone[0]} with AQI {best_zone[1]['aqi']}")
        advice.append(f"Avoid: {worst_zone[0]} with AQI {worst_zone[1]['aqi']}")
        
        return advice
    
    def _haversine_distance(
        self,
        point1: Tuple[float, float],
        point2: Tuple[float, float]
    ) -> float:
        """Calculate distance between two points in km."""
        R = 6371  # Earth's radius in km
        
        lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
        lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
