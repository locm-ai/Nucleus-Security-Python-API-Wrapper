# Nucleus Python SDK

A Python SDK for interacting with the Nucleus API. This SDK provides a simple and intuitive interface to access Nucleus's vulnerability management platform, with support for both synchronous and asynchronous operations.

## Features

- Full support for Nucleus API endpoints
- Async support for high-performance operations
- Built-in caching to reduce API calls
- Rate limiting to prevent API throttling
- Comprehensive error handling
- Type hints and data validation using Pydantic
- Detailed logging for debugging
- Retry mechanism with exponential backoff
- Interactive Jupyter notebook tutorial

## Installation

```bash
pip install nucleus-sdk
```

## Quick Start

### Synchronous Usage

```python
from nucleus import NucleusClient
from nucleus.models import Severity, AssetType

# Initialize the client
client = NucleusClient(api_key="your-api-key")

# Get list of projects
projects = client.get_projects()

# Get specific project
project = client.get_project(project_id=123)

# Get assets in a project
assets = client.get_project_assets(project_id=123)
```

### Asynchronous Usage

```python
import asyncio
from nucleus.async_client import AsyncNucleusClient

async def main():
    async with AsyncNucleusClient(api_key="your-api-key") as client:
        # Fetch multiple resources concurrently
        projects, findings = await asyncio.gather(
            client.get_projects(),
            client.search_findings(
                project_id=123,
                filters=[{
                    "property": "finding_severity",
                    "value": "Critical",
                    "exact_match": True
                }]
            )
        )

asyncio.run(main())
```

## Interactive Tutorial

We provide a Jupyter notebook tutorial that walks you through all the features of the SDK. To use it:

1. Install Jupyter if you haven't already:
```bash
pip install jupyter
```

2. Navigate to the examples directory and start Jupyter:
```bash
cd examples
jupyter notebook
```

3. Open `nucleus_sdk_tutorial.ipynb` in your browser

The tutorial covers:
- Basic SDK operations
- Working with projects, assets, and findings
- Async operations for improved performance
- Bulk operations and parallel processing
- Error handling and best practices
- Real-world usage examples

## Advanced Features

### Caching

The SDK includes built-in caching to reduce API calls:

```python
from nucleus.async_client import AsyncNucleusClient

async with AsyncNucleusClient(
    api_key="your-api-key",
    cache_ttl=300  # Cache TTL in seconds
) as client:
    # First call hits the API
    projects = await client.get_projects()
    
    # Second call uses cached data
    projects_cached = await client.get_projects()
```

### Rate Limiting

Built-in rate limiting prevents API throttling:

```python
from nucleus.async_client import AsyncNucleusClient

async with AsyncNucleusClient(
    api_key="your-api-key",
    rate_limit_calls=100,  # Number of calls allowed
    rate_limit_period=60   # Period in seconds
) as client:
    # SDK automatically handles rate limiting
    for i in range(200):
        await client.get_projects()  # Will pause if rate limit is reached
```

### Logging

Enable detailed logging for debugging:

```python
import logging
from nucleus.utils import logger

# Set logging level
logger.setLevel(logging.DEBUG)

# Add custom handler if needed
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
```

### Error Handling

Comprehensive error handling with custom exceptions:

```python
from nucleus import NucleusClient
from nucleus.exceptions import (
    NucleusAPIError,
    NucleusAuthError,
    NucleusNotFoundError,
    NucleusPermissionError
)

client = NucleusClient(api_key="your-api-key")

try:
    project = client.get_project(project_id=999999)
except NucleusNotFoundError:
    print("Project not found")
except NucleusAuthError:
    print("Authentication failed")
except NucleusPermissionError:
    print("Permission denied")
except NucleusAPIError as e:
    print(f"API error: {e}")
```

### Bulk Operations

Efficiently handle multiple operations:

```python
async with AsyncNucleusClient(api_key="your-api-key") as client:
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
    
    result = await client.bulk_update_findings(project_id, updates)
```

## Examples

The SDK comes with several examples:
- `examples/basic_usage.py`: Basic synchronous operations
- `examples/advanced_usage.py`: Advanced features including async operations
- `examples/nucleus_sdk_tutorial.ipynb`: Interactive Jupyter notebook tutorial

## API Documentation

For detailed API documentation, please visit the [Nucleus API Documentation](https://api-docs.nucleussec.com/nucleus/docs/).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This SDK is released under the MIT License. See the LICENSE file for details.
