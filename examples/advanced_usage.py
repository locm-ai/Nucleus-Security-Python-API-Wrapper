"""
Advanced usage examples for the Nucleus SDK demonstrating async operations,
caching, rate limiting, and error handling.
"""

import asyncio
import logging
from datetime import datetime
from nucleus import NucleusClient
from nucleus.async_client import AsyncNucleusClient
from nucleus.models import Severity, AssetType
from nucleus.exceptions import NucleusAPIError
from nucleus.utils import logger

# Enable debug logging
logger.setLevel(logging.DEBUG)

async def demonstrate_async_operations():
    """Demonstrate async operations with multiple concurrent requests."""
    async with AsyncNucleusClient(
        api_key="your-api-key-here",
        cache_ttl=300,  # 5 minutes cache
        rate_limit_calls=100,  # 100 calls per minute
        rate_limit_period=60
    ) as client:
        # Fetch multiple resources concurrently
        print("Fetching data concurrently...")
        start_time = datetime.now()
        
        projects, findings = await asyncio.gather(
            client.get_projects(),
            client.search_findings(
                project_id=123,
                filters=[{
                    "property": "finding_severity",
                    "value": Severity.CRITICAL,
                    "exact_match": True
                }]
            )
        )

        end_time = datetime.now()
        print(f"Concurrent fetching completed in {(end_time - start_time).total_seconds():.2f} seconds")
        
        # Demonstrate caching
        print("\nDemonstrating caching...")
        print("First request (will hit API):")
        start_time = datetime.now()
        await client.get_projects()
        end_time = datetime.now()
        print(f"Time taken: {(end_time - start_time).total_seconds():.2f} seconds")

        print("\nSecond request (should hit cache):")
        start_time = datetime.now()
        await client.get_projects()
        end_time = datetime.now()
        print(f"Time taken: {(end_time - start_time).total_seconds():.2f} seconds")

        # Demonstrate bulk operations
        if projects:
            project_id = projects[0].project_id
            print(f"\nPerforming bulk operations on project {project_id}...")
            
            # Bulk update findings
            updates = [
                {
                    "finding_number": "VULN-001",
                    "finding_status": "In Progress",
                    "comment": "Working on fix"
                },
                {
                    "finding_number": "VULN-002",
                    "finding_status": "In Progress",
                    "comment": "Under review"
                }
            ]
            
            try:
                result = await client.bulk_update_findings(project_id, updates)
                print(f"Bulk update completed: {result}")
            except NucleusAPIError as e:
                print(f"Bulk update failed: {e}")

async def demonstrate_parallel_scans():
    """Demonstrate parallel scanning of multiple assets."""
    async with AsyncNucleusClient(api_key="your-api-key-here") as client:
        try:
            # Get all projects
            projects = await client.get_projects()
            if not projects:
                print("No projects found")
                return

            project_id = projects[0].project_id

            # Get all assets in parallel
            print(f"\nFetching all assets for project {project_id}...")
            assets = await client.get_project_assets(project_id)

            # Get findings for each asset in parallel
            print("\nFetching findings for all assets in parallel...")
            start_time = datetime.now()
            
            asset_findings = await asyncio.gather(
                *[
                    client.get_asset_findings(project_id, asset.asset_id)
                    for asset in assets[:5]  # Limit to 5 assets for example
                ],
                return_exceptions=True
            )

            end_time = datetime.now()
            print(f"Fetched findings for {len(assets)} assets in "
                  f"{(end_time - start_time).total_seconds():.2f} seconds")

            # Process results
            for asset, findings in zip(assets[:5], asset_findings):
                if isinstance(findings, Exception):
                    print(f"Error fetching findings for asset {asset.asset_name}: {findings}")
                else:
                    print(f"\nFindings for asset {asset.asset_name}:")
                    for finding in findings[:3]:  # Show first 3 findings
                        print(f"- {finding.finding_name} ({finding.finding_severity})")

        except NucleusAPIError as e:
            print(f"Error: {e}")
            if hasattr(e, 'status_code'):
                print(f"Status code: {e.status_code}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response}")

def demonstrate_sync_operations():
    """Demonstrate synchronous operations with caching and rate limiting."""
    client = NucleusClient(api_key="your-api-key-here")

    try:
        # Regular synchronous operations
        print("\nPerforming synchronous operations...")
        projects = client.get_projects()
        
        if projects:
            project_id = projects[0].project_id
            
            # Create a new asset
            new_asset = client.create_asset(
                project_id=project_id,
                asset_name=f"test-server-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                asset_type=AssetType.HOST,
                ip_address="192.168.1.100",
                operating_system_name="Ubuntu",
                operating_system_version="20.04",
                asset_groups=["test-group"]
            )
            print(f"Created new asset: {new_asset}")

            # Update the asset
            client.update_asset(
                project_id=project_id,
                asset_id=new_asset['asset_id'],
                asset_notes="Updated via SDK example"
            )
            print("Asset updated successfully")

    except NucleusAPIError as e:
        print(f"Error: {e}")

async def main():
    print("Demonstrating async operations...")
    await demonstrate_async_operations()
    
    print("\nDemonstrating parallel scans...")
    await demonstrate_parallel_scans()
    
    print("\nDemonstrating sync operations...")
    demonstrate_sync_operations()

if __name__ == "__main__":
    asyncio.run(main())
