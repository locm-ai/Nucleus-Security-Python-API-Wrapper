from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from .models import Finding, FindingFilter, Severity

class FindingsAPI:
    """Handles all finding-related API endpoints."""
    
    def __init__(self, client):
        self.client = client

    def get_finding_details(
        self,
        project_id: Union[int, str],
        finding_number: str,
        finding_id: Optional[int] = None
    ) -> Finding:
        """Get detailed information about a specific finding."""
        endpoint = f"/projects/{project_id}/findings/details/{finding_number}"
        if finding_id is not None:
            endpoint = f"{endpoint}/{finding_id}"
        response = self.client.get(endpoint)
        return Finding(**response)

    def update_finding(
        self,
        project_id: Union[int, str],
        finding_number: str,
        status: Optional[str] = None,
        severity: Optional[Severity] = None,
        comment: Optional[str] = None,
        due_date: Optional[str] = None,
        team_id: Optional[int] = None,
        asset_id: Optional[int] = None,
        finding_justification_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a finding's status, severity, or other attributes."""
        data = {
            "finding_status": status,
            "finding_severity": severity,
            "comment": comment,
            "due_date": due_date,
            "team_id": team_id
        }
        data = {k: v for k, v in data.items() if v is not None}

        params = {
            "finding_number": finding_number,
            "asset_id": asset_id,
            "finding_justification_key": finding_justification_key
        }
        params = {k: v for k, v in params.items() if v is not None}

        return self.client.put(
            f"/projects/{project_id}/findings",
            data=data,
            params=params
        )

    def search_findings(
        self,
        project_id: Union[int, str],
        start: Optional[int] = None,
        limit: Optional[int] = None,
        filters: Optional[List[FindingFilter]] = None
    ) -> List[Finding]:
        """Search for findings using various filters."""
        params = {
            "start": start,
            "limit": limit
        }
        params = {k: v for k, v in params.items() if v is not None}

        data = {"finding_filters": [f.dict() for f in filters]} if filters else {}
        
        response = self.client.post(
            f"/projects/{project_id}/findings/search",
            params=params,
            data=data
        )
        return [Finding(**finding) for finding in response]

    def get_finding_trend(
        self,
        project_id: Union[int, str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        asset_groups: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get trend information for findings."""
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "asset_groups": asset_groups and ",".join(asset_groups)
        }
        params = {k: v for k, v in params.items() if v is not None}
        
        return self.client.get(f"/projects/{project_id}/findings/trend", params=params)

    def get_finding_metrics(
        self,
        project_id: Union[int, str]
    ) -> Dict[str, Any]:
        """Get metrics information for findings."""
        return self.client.get(f"/projects/{project_id}/findings/metrics")

    def add_custom_finding(
        self,
        project_id: Union[int, str],
        host_id: int,
        name: str,
        severity: Severity,
        finding_type: str,
        description: str,
        discovered: Optional[str] = None,
        recommendation: Optional[str] = None,
        cve: Optional[str] = None,
        exploitable: Optional[int] = None,
        references: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Add a custom finding to an asset."""
        data = {
            "host_id": host_id,
            "custom_finding_name": name,
            "custom_finding_severity": severity,
            "custom_finding_type": finding_type,
            "custom_finding_description": description,
            "finding_discovered": discovered or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "custom_finding_recommendation": recommendation,
            "custom_finding_cve": cve,
            "custom_finding_exploitable": exploitable,
            "custom_finding_references": references and str(references)
        }
        data = {k: v for k, v in data.items() if v is not None}

        return self.client.post(f"/projects/{project_id}/findings", data=data)

    def bulk_update_findings(
        self,
        project_id: Union[int, str],
        updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update multiple findings in bulk."""
        return self.client.put(f"/projects/{project_id}/findings/bulk", data=updates)

    def get_mitigated_findings(
        self,
        project_id: Union[int, str],
        start: Optional[int] = None,
        limit: Optional[int] = None,
        start_date: Optional[str] = None
    ) -> List[Finding]:
        """Get information on mitigated findings."""
        params = {
            "start": start,
            "limit": limit,
            "start_date": start_date
        }
        params = {k: v for k, v in params.items() if v is not None}
        
        response = self.client.get(f"/projects/{project_id}/findings/mitigated", params=params)
        return [Finding(**finding) for finding in response]

    def get_finding_frameworks(
        self,
        project_id: Union[int, str]
    ) -> List[str]:
        """Get list of compliance frameworks associated with findings."""
        response = self.client.get(f"/projects/{project_id}/findings/frameworks")
        return [framework["framework_name"] for framework in response]
