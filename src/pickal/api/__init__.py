"""pickal — API Layer.

Atomic Spec: API Layer (CLI, REST, gRPC)
  § 1  — CLI interface
  § 2  — REST API endpoints
  § 3  — gRPC services
  § 4  — Request/response models
  § 5  — API versioning
  § 6  — Rate limiting
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class API:
    """Base API class."""
    
    def __init__(self, config: Any) -> None:
        self.config = config
    
    def handle_request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle API request."""
        raise NotImplementedError("API.handle_request() must be implemented")


class CLI:
    """Command Line Interface."""
    
    def __init__(self, api: Any) -> None:
        self.api = api
    
    def run(self, args: List[str]) -> int:
        """Run CLI command."""
        raise NotImplementedError("CLI.run() must be implemented")


class RESTAPI:
    """REST API implementation."""
    
    def __init__(self, api: Any) -> None:
        self.api = api
    
    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """HTTP GET request."""
        raise NotImplementedError("RESTAPI.get() must be implemented")
    
    def post(self, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """HTTP POST request."""
        raise NotImplementedError("RESTAPI.post() must be implemented")
    
    def put(self, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """HTTP PUT request."""
        raise NotImplementedError("RESTAPI.put() must be implemented")
    
    def delete(self, path: str) -> Dict[str, Any]:
        """HTTP DELETE request."""
        raise NotImplementedError("RESTAPI.delete() must be implemented")
