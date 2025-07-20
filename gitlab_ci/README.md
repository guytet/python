# GitLab Pipeline Trigger Script

This is a standalone Python script to trigger a GitLab CI pipeline using the GitLab API. It accepts a trigger token, project ID, reference (branch or tag), and optional CI variables. It is useful for manually triggering jobs, integrating pipeline execution into external systems, or automating environment-specific deployments.

## Requirements

- Python 3.6 or higher
- `requests` library

You can install the required dependency with:

```bash
pip install requests
```

### Usage
```
python trigger_pipeline.py \
  --url https://gitlab.example.com \
  --project-id 123 \
  --ref main \
  --token your_trigger_token \
  --variable ENV=prod \
  --variable FORCE_DEPLOY=true
```

Example:
```
python trigger_pipeline.py \
  --url https://gitlab.internal \
  --project-id 456 \
  --ref develop \
  --token abcdef123456 \
  --variable DEPLOY_ENV=staging \
  --variable RUN_MIGRATIONS=yes
```

Behavior:
- On success, the script prints a confirmation message and the response JSON from the GitLab API.

- On failure, it prints the HTTP status code and the response text for troubleshooting.


