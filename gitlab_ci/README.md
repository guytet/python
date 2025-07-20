# GitLab Pipeline Trigger Script

This is a standalone Python script to trigger a GitLab CI pipeline using the GitLab API. It accepts a trigger token, project ID, reference (branch or tag), and optional CI variables. It is useful for manually triggering jobs, integrating pipeline execution into external systems, or automating environment-specific deployments.

## Requirements

- Python 3.6 or higher
- `requests` library

You can install the required dependency with:

```bash
pip install requests

