import requests
from typing import Optional, Dict, Any


class APIClient:
    """HTTP client for backend API communication"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
    
    def set_token(self, token: str):
        """Set JWT token for authentication"""
        self.token = token
    
    def clear_token(self):
        """Clear JWT token"""
        self.token = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication if token exists"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST request to API"""
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET request to API"""
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def patch(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """PATCH request to API"""
        url = f"{self.base_url}{endpoint}"
        response = requests.patch(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()


# Global API client instance
api_client = APIClient()
