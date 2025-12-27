"""Google Places API integration service"""
import requests
import math
from typing import Dict, List, Optional


class GooglePlacesService:
    """Service class for interacting with Google Places API"""

    def __init__(self, api_key: str, location: str, radius: int):
        """
        Initialize Google Places service

        Args:
            api_key: Google Places API key
            location: Center point as "lat,lng" string
            radius: Search radius in meters
        """
        self.api_key = api_key
        self.location = location  # "lat,lng"
        self.radius = radius
        self.base_url = "https://maps.googleapis.com/maps/api/place"

        # Parse location
        if location:
            try:
                lat, lng = location.split(',')
                self.center_lat = float(lat)
                self.center_lng = float(lng)
            except (ValueError, AttributeError):
                self.center_lat = None
                self.center_lng = None
        else:
            self.center_lat = None
            self.center_lng = None

    def search_places(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search for places using Google Places Text Search API

        Args:
            query: Search query (restaurant name)
            max_results: Maximum number of results to return

        Returns:
            List of place dictionaries with: place_id, name, address, distance
        """
        if not self.api_key:
            return []

        url = f"{self.base_url}/textsearch/json"

        params = {
            'query': query,
            'key': self.api_key,
            'type': 'restaurant|cafe|food'
        }

        # Add location bias if available
        if self.location:
            params['location'] = self.location
            params['radius'] = self.radius

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 'OK':
                print(f"Google Places API error: {data.get('status')} - {data.get('error_message', '')}")
                return []

            results = []
            for place in data.get('results', []):
                place_data = {
                    'place_id': place.get('place_id'),
                    'name': place.get('name'),
                    'address': place.get('formatted_address', 'N/A'),
                    'distance': None
                }

                # Calculate distance if we have location data
                geometry = place.get('geometry', {})
                place_location = geometry.get('location', {})
                if place_location and self.center_lat and self.center_lng:
                    place_lat = place_location.get('lat')
                    place_lng = place_location.get('lng')
                    if place_lat and place_lng:
                        distance = self.calculate_distance(
                            self.center_lat, self.center_lng,
                            place_lat, place_lng
                        )
                        place_data['distance'] = distance

                        # Filter: Use 1.5x radius since driving distance is longer than straight-line
                        # (This is just for initial filtering; actual distance is calculated on selection)
                        if distance > (self.radius * 1.5):
                            continue  # Skip this place, it's too far
                else:
                    # Skip places without location data
                    continue

                results.append(place_data)

            # Sort by distance (closest first)
            results.sort(key=lambda x: x['distance'] if x['distance'] is not None else float('inf'))

            # Return top max_results
            return results[:max_results]

        except requests.RequestException as e:
            print(f"Error searching Google Places: {e}")
            return []

    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """
        Get detailed information for a specific place using Google Places Details API

        Args:
            place_id: Google Place ID

        Returns:
            Dictionary with: name, phone, address, website, location, distance, eta
        """
        if not self.api_key or not place_id:
            return None

        url = f"{self.base_url}/details/json"

        params = {
            'place_id': place_id,
            'key': self.api_key,
            'fields': 'name,formatted_phone_number,formatted_address,website,geometry,url'
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 'OK':
                print(f"Google Places Details API error: {data.get('status')}")
                return None

            result = data.get('result', {})

            place_details = {
                'place_id': place_id,
                'name': result.get('name', ''),
                'phone': result.get('formatted_phone_number', ''),
                'address': result.get('formatted_address', ''),
                'website': result.get('website', ''),
                'google_maps_url': result.get('url', ''),
                'distance': None,
                'eta': None
            }

            # Get actual driving distance and time using Distance Matrix API
            geometry = result.get('geometry', {})
            place_location = geometry.get('location', {})

            if place_location and self.center_lat and self.center_lng:
                place_lat = place_location.get('lat')
                place_lng = place_location.get('lng')

                if place_lat and place_lng:
                    # Get actual driving distance and ETA from Distance Matrix API
                    driving_data = self.get_driving_distance_and_time(place_lat, place_lng)
                    if driving_data:
                        place_details['distance'] = driving_data['distance']
                        place_details['eta'] = driving_data['duration']
                    else:
                        # Fallback to Haversine calculation if Distance Matrix fails
                        distance = self.calculate_distance(
                            self.center_lat, self.center_lng,
                            place_lat, place_lng
                        )
                        place_details['distance'] = distance
                        # Calculate ETA (rough estimate: average 35 mph in city)
                        distance_miles = distance * 0.000621371
                        avg_speed_mph = 35
                        eta_hours = distance_miles / avg_speed_mph
                        eta_minutes = int(eta_hours * 60)
                        place_details['eta'] = eta_minutes

            return place_details

        except requests.RequestException as e:
            print(f"Error fetching place details: {e}")
            return None

    def get_driving_distance_and_time(self, dest_lat: float, dest_lng: float) -> Optional[Dict]:
        """
        Get actual driving distance and time using Google Distance Matrix API

        Args:
            dest_lat: Destination latitude
            dest_lng: Destination longitude

        Returns:
            Dictionary with distance (meters) and duration (minutes), or None if error
        """
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"

        params = {
            'origins': f"{self.center_lat},{self.center_lng}",
            'destinations': f"{dest_lat},{dest_lng}",
            'key': self.api_key,
            'mode': 'driving',
            'units': 'imperial'
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 'OK':
                print(f"Distance Matrix API error: {data.get('status')}")
                return None

            rows = data.get('rows', [])
            if not rows:
                return None

            elements = rows[0].get('elements', [])
            if not elements:
                return None

            element = elements[0]
            if element.get('status') != 'OK':
                print(f"Distance Matrix element error: {element.get('status')}")
                return None

            # Extract distance (in meters) and duration (in seconds)
            distance_meters = element.get('distance', {}).get('value')
            duration_seconds = element.get('duration', {}).get('value')

            if distance_meters is None or duration_seconds is None:
                return None

            # Convert duration from seconds to minutes
            duration_minutes = int(duration_seconds / 60)

            return {
                'distance': distance_meters,
                'duration': duration_minutes
            }

        except requests.RequestException as e:
            print(f"Error fetching driving distance: {e}")
            return None

    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate distance between two points using Haversine formula

        Args:
            lat1, lng1: First point coordinates
            lat2, lng2: Second point coordinates

        Returns:
            Distance in meters
        """
        # Earth's radius in meters
        R = 6371000

        # Convert to radians
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lng2 - lng1)

        # Haversine formula
        a = math.sin(delta_phi / 2) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c

        return distance
