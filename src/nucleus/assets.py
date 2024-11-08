from typing import List, Optional, Dict, Any, Union
from .models import Asset, Finding, AssetType

class AssetsAPI:
    """Handles all asset-related API endpoints."""
    
    def __init__(self, client):
        self.client = client

    def get_asset(
        self,
        project_id: Union[int, str],
        asset_id: Union[int, str]
    ) -> Asset:
        """Get information about a specific asset."""
        response = self.client.get(f"/projects/{project_id}/assets/{asset_id}")
        return Asset(**response)

    def create_asset(
        self,
        project_id: Union[int, str],
        asset_name: str,
        asset_type: AssetType,
        ip_address: Optional[str] = None,
        domain_name: Optional[str] = None,
        operating_system_name: Optional[str] = None,
        operating_system_version: Optional[str] = None,
        asset_criticality: Optional[str] = None,
        asset_groups: Optional[List[str]] = None,
        asset_location: Optional[str] = None,
        asset_notes: Optional[str] = None,
        asset_data_sensitivity_score: Optional[int] = None,
        asset_public: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Create a new asset in a project."""
        data = {
            "asset_name": asset_name,
            "asset_type": asset_type,
            "ip_address": ip_address,
            "domain_name": domain_name,
            "operating_system_name": operating_system_name,
            "operating_system_version": operating_system_version,
            "asset_criticality": asset_criticality,
            "asset_groups": asset_groups or [],
            "asset_location": asset_location,
            "asset_notes": asset_notes,
            "asset_data_sensitivity_score": asset_data_sensitivity_score,
            "asset_public": asset_public,
            "active": True
        }
        data = {k: v for k, v in data.items() if v is not None}
        
        return self.client.post(f"/projects/{project_id}/assets", data=data)

    def update_asset(
        self,
        project_id: Union[int, str],
        asset_id: Union[int, str],
        **kwargs
    ) -> Dict[str, Any]:
        """Update an existing asset."""
        valid_fields = {
            "asset_name", "asset_type", "ip_address", "domain_name",
            "operating_system_name", "operating_system_version",
            "asset_criticality", "asset_groups", "asset_location",
            "asset_notes", "asset_data_sensitivity_score", "asset_public",
            "active", "decommed"
        }
        
        data = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}
        return self.client.put(f"/projects/{project_id}/assets/{asset_id}", data=data)

    def list_assets(
        self,
        project_id: Union[int, str],
        start: Optional[int] = None,
        limit: Optional[int] = None,
        ip_address: Optional[str] = None,
        asset_name: Optional[str] = None,
        asset_name_ip: Optional[str] = None,
        asset_groups: Optional[str] = None,
        asset_type: Optional[str] = None,
        inactive_assets: Optional[bool] = None,
        unscanned_assets: Optional[bool] = None,
        assets_with_findings: Optional[bool] = None
    ) -> List[Asset]:
        """Get a list of assets with optional filtering."""
        params = {
            "start": start,
            "limit": limit,
            "ip_address": ip_address,
            "asset_name": asset_name,
            "asset_name_ip": asset_name_ip,
            "asset_groups": asset_groups,
            "asset_type": asset_type,
            "inactive_assets": inactive_assets,
            "unscanned_assets": unscanned_assets,
            "assets_with_findings": assets_with_findings
        }
        params = {k: v for k, v in params.items() if v is not None}
        
        response = self.client.get(f"/projects/{project_id}/assets", params=params)
        return [Asset(**asset) for asset in response]

    def get_asset_findings(
        self,
        project_id: Union[int, str],
        asset_id: Union[int, str]
    ) -> List[Finding]:
        """Get findings for a specific asset."""
        response = self.client.get(f"/projects/{project_id}/assets/{asset_id}/findings")
        return [Finding(**finding) for finding in response]

    def create_asset_group(
        self,
        project_id: Union[int, str],
        asset_group: str
    ) -> Dict[str, Any]:
        """Create a new asset group."""
        data = {"asset_group": asset_group}
        return self.client.post(f"/projects/{project_id}/assets/groups", data=data)

    def delete_asset_group(
        self,
        project_id: Union[int, str],
        asset_group: str
    ) -> Dict[str, Any]:
        """Delete an asset group."""
        params = {"asset_group": asset_group}
        return self.client.delete(f"/projects/{project_id}/assets/groups", params=params)

    def get_asset_groups(
        self,
        project_id: Union[int, str]
    ) -> List[Dict[str, Any]]:
        """Get all asset groups for a project."""
        return self.client.get(f"/projects/{project_id}/assets/groups")

    def get_asset_group_metrics(
        self,
        project_id: Union[int, str],
        asset_groups: List[str],
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get metrics for specified asset groups."""
        params = {
            "asset_groups": ",".join(asset_groups),
            "metrics": metrics and ",".join(metrics)
        }
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get(f"/projects/{project_id}/assets/groups/metrics", params=params)
