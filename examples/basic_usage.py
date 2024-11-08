"""
Basic usage examples for the Nucleus SDK.
"""

from nucleus import NucleusClient
from nucleus.models import Severity, AssetType
from nucleus.exceptions import NucleusAPIError

def main():
    # Initialize the client with your API key
    client = NucleusClient(api_key="your-api-key-here")

    try:
        # List all projects
        print("Fetching projects...")
        projects = client.get_projects()
        for project in projects:
            print(f"Project: {project.project_name} (ID: {project.project_id})")

        # For this example, we'll use the first project
        if projects:
            project = projects[0]
            project_id = project.project_id

            # Get project metrics
            print(f"\nFetching metrics for project {project.project_name}...")
            metrics = client.get_project_metrics(project_id)
            print(f"Critical findings: {metrics.finding_count_critical}")
            print(f"High findings: {metrics.finding_count_high}")
            print(f"Medium findings: {metrics.finding_count_medium}")
            print(f"Low findings: {metrics.finding_count_low}")

            # List assets in the project
            print("\nFetching assets...")
            assets = client.get_project_assets(project_id)
            for asset in assets:
                print(f"Asset: {asset.asset_name} ({asset.asset_type})")

            # Create a new asset
            print("\nCreating a new asset...")
            new_asset = client.create_asset(
                project_id=project_id,
                asset_name="example-server-01",
                asset_type=AssetType.HOST,
                ip_address="192.168.1.100",
                operating_system_name="Ubuntu",
                operating_system_version="20.04",
                asset_groups=["example-group"]
            )
            print(f"Created asset with ID: {new_asset['asset_id']}")

            # Search for critical findings
            print("\nSearching for critical findings...")
            findings = client.search_findings(
                project_id=project_id,
                filters=[{
                    "property": "finding_severity",
                    "value": Severity.CRITICAL,
                    "exact_match": True
                }]
            )
            for finding in findings:
                print(f"Critical finding: {finding.finding_name}")
                print(f"  Severity: {finding.finding_severity}")
                print(f"  Status: {finding.finding_status}")
                print(f"  Discovered: {finding.finding_discovered}")

            # Get project risk score
            print("\nFetching project risk score...")
            risk_score = client.projects.get_project_risk_score(project_id)
            print(f"Project risk score: {risk_score}")

    except NucleusAPIError as e:
        print(f"Error: {e}")
        if hasattr(e, 'status_code'):
            print(f"Status code: {e.status_code}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response}")

if __name__ == "__main__":
    main()
