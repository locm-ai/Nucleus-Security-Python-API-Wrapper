from typing import List, Optional, Dict, Any, Union
from .models import Project, Asset, Finding, Scan, PaginationParams, ProjectMetrics

class ProjectsAPI:
    """Handles all project-related API endpoints."""
    
    def __init__(self, client):
        self.client = client

    def list_projects(self) -> List[Project]:
        """Get a list of all projects."""
        response = self.client.get("/projects")
        return [Project(**project) for project in response]

    def get_project(self, project_id: Union[int, str]) -> Project:
        """Get information about a specific project."""
        response = self.client.get(f"/projects/{project_id}")
        return Project(**response)

    def get_project_assets(
        self,
        project_id: Union[int, str],
        start: Optional[int] = None,
        limit: Optional[int] = None,
        ip_address: Optional[str] = None,
        asset_name: Optional[str] = None,
        asset_groups: Optional[str] = None,
        asset_type: Optional[str] = None,
        inactive_assets: Optional[bool] = None
    ) -> List[Asset]:
        """Get a list of assets in a project."""
        params = {
            "start": start,
            "limit": limit,
            "ip_address": ip_address,
            "asset_name": asset_name,
            "asset_groups": asset_groups,
            "asset_type": asset_type,
            "inactive_assets": inactive_assets
        }
        params = {k: v for k, v in params.items() if v is not None}
        
        response = self.client.get(f"/projects/{project_id}/assets", params=params)
        return [Asset(**asset) for asset in response]

    def get_project_findings(
        self,
        project_id: Union[int, str],
        start: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[Finding]:
        """Get a list of findings in a project."""
        params = PaginationParams(start=start, limit=limit).dict(exclude_none=True)
        response = self.client.get(f"/projects/{project_id}/findings", params=params)
        return [Finding(**finding) for finding in response]

    def get_project_scans(
        self,
        project_id: Union[int, str],
        start: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[Scan]:
        """Get a list of scans in a project."""
        params = PaginationParams(start=start, limit=limit).dict(exclude_none=True)
        response = self.client.get(f"/projects/{project_id}/scans", params=params)
        return [Scan(**scan) for scan in response]

    def get_project_metrics(self, project_id: Union[int, str]) -> ProjectMetrics:
        """Get metrics for a project."""
        response = self.client.get(f"/projects/{project_id}/findings/overview")
        return ProjectMetrics(**response)

    def get_project_risk_score(self, project_id: Union[int, str]) -> int:
        """Get the risk score for a project."""
        response = self.client.get(f"/projects/{project_id}/riskscore")
        return response["score"]

    def upload_scan(
        self,
        project_id: Union[int, str],
        file_path: str,
        scan_description: Optional[str] = None,
        scan_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload a scan file to a project."""
        files = {'file': open(file_path, 'rb')}
        data = {}
        if scan_description:
            data['scan_description'] = scan_description
        if scan_type:
            data['scan_type'] = scan_type
            
        return self.client.post(
            f"/projects/{project_id}/scans",
            data=data,
            files=files
        )

    def create_asset(
        self,
        project_id: Union[int, str],
        asset: Asset
    ) -> Dict[str, Any]:
        """Create a new asset in a project."""
        return self.client.post(
            f"/projects/{project_id}/assets",
            data=asset.dict(exclude_none=True)
        )

    def update_asset(
        self,
        project_id: Union[int, str],
        asset_id: Union[int, str],
        asset: Asset
    ) -> Dict[str, Any]:
        """Update an existing asset in a project."""
        return self.client.put(
            f"/projects/{project_id}/assets/{asset_id}",
            data=asset.dict(exclude_none=True)
        )

    def delete_asset(
        self,
        project_id: Union[int, str],
        asset_id: Union[int, str]
    ) -> Dict[str, Any]:
        """Delete an asset from a project."""
        return self.client.delete(f"/projects/{project_id}/assets/{asset_id}")
