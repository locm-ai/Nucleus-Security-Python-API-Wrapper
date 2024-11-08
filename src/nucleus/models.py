from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class Severity(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFORMATIONAL = "Informational"

class AssetType(str, Enum):
    APPLICATION = "Application"
    CONTAINER = "Container"
    CONTAINER_IMAGE = "Container Image"
    HOST = "Host"
    DATABASE = "Database"

class TeamData(BaseModel):
    team_id: int
    team_name: str

class Project(BaseModel):
    tracking_method: str
    project_name: str
    project_description: str
    project_id: int
    project_groups: List[str]
    project_org: str

class Asset(BaseModel):
    asset_id: int
    asset_name: str
    asset_type: AssetType
    ip_address: Optional[str] = None
    domain_name: Optional[str] = None
    operating_system_name: Optional[str] = None
    operating_system_version: Optional[str] = None
    asset_criticality: Optional[str] = None
    asset_groups: List[str] = Field(default_factory=list)
    active: bool = True
    asset_location: Optional[str] = None
    support_team: Optional[TeamData] = None
    owner_team: Optional[TeamData] = None
    asset_data_sensitivity_score: Optional[int] = None
    asset_complianced_score: Optional[int] = None
    asset_public: Optional[bool] = None
    decommed: bool = False

class Finding(BaseModel):
    finding_id: int
    finding_number: str
    finding_name: str
    finding_severity: Severity
    finding_status: str
    finding_discovered: str
    scan_type: str
    finding_description: Optional[str] = None
    finding_recommendation: Optional[str] = None
    finding_cve: Optional[str] = None
    finding_exploitable: Optional[int] = None
    finding_port: Optional[str] = None
    finding_path: Optional[str] = None
    finding_output: Optional[str] = None
    due_date: Optional[str] = None
    asset_id: Optional[str] = None
    asset_name: Optional[str] = None
    ip_address: Optional[str] = None

class Scan(BaseModel):
    scan_id: int
    scan_file_name: str
    scan_date: str
    scan_type: str
    scan_description: Optional[str] = None
    finding_count_critical: int = 0
    finding_count_high: int = 0
    finding_count_medium: int = 0
    finding_count_low: int = 0
    finding_count_informational: int = 0
    asset_count: int = 0
    scan_mitigated: int = 0

class Issue(BaseModel):
    issue_key: str
    issue_assignee: Optional[str] = None
    issue_status: str
    issue_type: str
    issue_url: Optional[str] = None
    finding_count: int
    finding_severity: Severity
    finding_name: str
    scan_type: str
    issue_updated: str

class PaginationParams(BaseModel):
    start: Optional[int] = None
    limit: Optional[int] = None

class FindingFilter(BaseModel):
    property: str
    value: Any
    exact_match: bool = False

class AssetFilter(BaseModel):
    asset_groups: Optional[List[int]] = None
    finding_filters: Optional[List[FindingFilter]] = None

class Response(BaseModel):
    """Generic response model"""
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None

class ProjectMetrics(BaseModel):
    finding_count_critical: int = 0
    finding_count_high: int = 0
    finding_count_medium: int = 0
    finding_count_low: int = 0
    finding_count_informational: int = 0
    finding_vulnerability_score: Optional[int] = None
    finding_count_exploitable: int = 0
    finding_count_cve: int = 0
