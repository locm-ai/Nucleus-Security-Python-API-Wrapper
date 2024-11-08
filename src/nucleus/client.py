import requests
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin

from .exceptions import (
    NucleusAPIError,
    NucleusAuthError,
    NucleusNotFoundError,
    NucleusPermissionError
)
from .projects import ProjectsAPI
from .findings import FindingsAPI
from .assets import AssetsAPI

class NucleusClient:
    """
    Main client class for interacting with the Nucleus API.
    
    Args:
        api_key (str): Your Nucleus API key
        base_url (str, optional): The base URL for the Nucleus API. Defaults to the standard API endpoint.
        timeout (int, optional): Request timeout in seconds. Defaults to 30.
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.nucleussec.com/nucleus/api",
        timeout: int = 30
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

        # Initialize API modules
        self.projects = ProjectsAPI(self)
        self.findings = FindingsAPI(self)
        self.assets = AssetsAPI(self)

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response and raise appropriate exceptions."""
        try:
            response_json = response.json()
        except ValueError:
            response_json = response.text

        if response.status_code >= 400:
            if response.status_code == 401:
                raise NucleusAuthError("Authentication failed", status_code=401, response=response_json)
            elif response.status_code == 403:
                raise NucleusPermissionError("Permission denied", status_code=403, response=response_json)
            elif response.status_code == 404:
                raise NucleusNotFoundError("Resource not found", status_code=404, response=response_json)
            elif response.status_code == 422:
                raise NucleusAPIError("Invalid request", status_code=422, response=response_json)
            else:
                raise NucleusAPIError(
                    f"API request failed: {response.text}",
                    status_code=response.status_code,
                    response=response_json
                )

        return response_json

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """Make an HTTP request to the API."""
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                files=files,
                timeout=self.timeout,
                **kwargs
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise NucleusAPIError(f"Request failed: {str(e)}")

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """Send GET request to the API."""
        return self._request("GET", endpoint, params=params, **kwargs)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """Send POST request to the API."""
        return self._request("POST", endpoint, data=data, files=files, **kwargs)

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """Send PUT request to the API."""
        return self._request("PUT", endpoint, json=data, **kwargs)

    def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """Send DELETE request to the API."""
        return self._request("DELETE", endpoint, params=params, **kwargs)

    # Convenience methods that delegate to the appropriate API module

    def get_projects(self):
        """Get list of all projects."""
        return self.projects.list_projects()

    def get_project(self, project_id: Union[int, str]):
        """Get information on a specific project."""
        return self.projects.get_project(project_id)

    def get_project_assets(self, project_id: Union[int, str], **kwargs):
        """Get list of assets in a project."""
        return self.projects.get_project_assets(project_id, **kwargs)

    def get_project_findings(self, project_id: Union[int, str], **kwargs):
        """Get list of findings in a project."""
        return self.projects.get_project_findings(project_id, **kwargs)

    def get_project_scans(self, project_id: Union[int, str], **kwargs):
        """Get list of scans in a project."""
        return self.projects.get_project_scans(project_id, **kwargs)

    def get_project_metrics(self, project_id: Union[int, str]):
        """Get metrics for a project."""
        return self.projects.get_project_metrics(project_id)

    def search_findings(self, project_id: Union[int, str], **kwargs):
        """Search for findings using various filters."""
        return self.findings.search_findings(project_id, **kwargs)

    def update_finding(self, project_id: Union[int, str], finding_number: str, **kwargs):
        """Update a finding's status, severity, or other attributes."""
        return self.findings.update_finding(project_id, finding_number, **kwargs)

    def create_asset(self, project_id: Union[int, str], **kwargs):
        """Create a new asset in a project."""
        return self.assets.create_asset(project_id, **kwargs)

    def update_asset(self, project_id: Union[int, str], asset_id: Union[int, str], **kwargs):
        """Update an existing asset."""
        return self.assets.update_asset(project_id, asset_id, **kwargs)

    def get_asset_findings(self, project_id: Union[int, str], asset_id: Union[int, str]):
        """Get findings for a specific asset."""
        return self.assets.get_asset_findings(project_id, asset_id)
