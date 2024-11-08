import aiohttp
import asyncio
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin

from .exceptions import (
    NucleusAPIError,
    NucleusAuthError,
    NucleusNotFoundError,
    NucleusPermissionError
)
from .utils import Cache, RateLimit, logger

class AsyncNucleusClient:
    """
    Asynchronous client for interacting with the Nucleus API.
    
    Args:
        api_key (str): Your Nucleus API key
        base_url (str, optional): The base URL for the Nucleus API
        timeout (int, optional): Request timeout in seconds
        cache_ttl (int, optional): Cache TTL in seconds
        rate_limit_calls (int, optional): Number of calls allowed per period
        rate_limit_period (int, optional): Period in seconds for rate limiting
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.nucleussec.com/nucleus/api",
        timeout: int = 30,
        cache_ttl: int = 300,
        rate_limit_calls: int = 100,
        rate_limit_period: int = 60
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.cache = Cache(ttl=cache_ttl)
        self.rate_limiter = RateLimit(rate_limit_calls, rate_limit_period)
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Any:
        """Handle API response and raise appropriate exceptions."""
        try:
            response_json = await response.json()
        except ValueError:
            response_json = await response.text()

        if response.status >= 400:
            if response.status == 401:
                raise NucleusAuthError("Authentication failed", status_code=401, response=response_json)
            elif response.status == 403:
                raise NucleusPermissionError("Permission denied", status_code=403, response=response_json)
            elif response.status == 404:
                raise NucleusNotFoundError("Resource not found", status_code=404, response=response_json)
            elif response.status == 422:
                raise NucleusAPIError("Invalid request", status_code=422, response=response_json)
            else:
                raise NucleusAPIError(
                    f"API request failed: {response_json}",
                    status_code=response.status,
                    response=response_json
                )

        return response_json

    @RateLimit(100, 60)  # Rate limit: 100 calls per 60 seconds
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        cache_key: Optional[str] = None
    ) -> Any:
        """Make an HTTP request to the API."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )

        # Check cache for GET requests
        if method == "GET" and cache_key:
            cached_response = self.cache.get(cache_key)
            if cached_response is not None:
                return cached_response

        url = urljoin(self.base_url, endpoint.lstrip('/'))
        
        try:
            async with self.session.request(method, url, params=params, json=json, data=data) as response:
                result = await self._handle_response(response)
                
                # Cache successful GET requests
                if method == "GET" and cache_key:
                    self.cache.set(cache_key, result)
                
                return result
        except aiohttp.ClientError as e:
            raise NucleusAPIError(f"Request failed: {str(e)}")

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> Any:
        """Send GET request to the API."""
        cache_key = f"{endpoint}:{str(params)}" if use_cache else None
        return await self._request("GET", endpoint, params=params, cache_key=cache_key)

    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Send POST request to the API."""
        return await self._request("POST", endpoint, json=json, data=data)

    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Send PUT request to the API."""
        return await self._request("PUT", endpoint, json=data)

    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Send DELETE request to the API."""
        return await self._request("DELETE", endpoint, params=params)

    # Async convenience methods

    async def get_projects(self):
        """Get list of all projects."""
        return await self.get("/projects")

    async def get_project(self, project_id: Union[int, str]):
        """Get information on a specific project."""
        return await self.get(f"/projects/{project_id}")

    async def get_project_assets(
        self,
        project_id: Union[int, str],
        **kwargs
    ):
        """Get list of assets in a project."""
        return await self.get(f"/projects/{project_id}/assets", params=kwargs)

    async def get_project_findings(
        self,
        project_id: Union[int, str],
        **kwargs
    ):
        """Get list of findings in a project."""
        return await self.get(f"/projects/{project_id}/findings", params=kwargs)

    async def bulk_update_findings(
        self,
        project_id: Union[int, str],
        updates: List[Dict[str, Any]]
    ):
        """Update multiple findings in bulk."""
        return await self.put(f"/projects/{project_id}/findings/bulk", data=updates)

    async def search_findings(
        self,
        project_id: Union[int, str],
        filters: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        """Search for findings using various filters."""
        data = {"finding_filters": filters} if filters else {}
        return await self.post(
            f"/projects/{project_id}/findings/search",
            json=data,
            **kwargs
        )
