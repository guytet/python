# EasyDNS ACME Solver

## Overview

This project provides a simple ACME DNS-01 challenge solver for EasyDNS, implemented as a Flask application and packaged in a Docker container. It exposes a Kubernetes-style webhook API to create and update TXT records for `_acme-challenge` under a given DNS zone.

## Repository Contents

- **easydns_acme_solver.py** - Flask application implementing two endpoints:
  - `POST /apis/acme.easydns.com/v1alpha1/challenges`  
    Accepts ACME challenge requests and creates or updates the corresponding TXT record.
  - `GET  /apis/acme.easydns.com/v1alpha1`  
    API discovery endpoint returning the resource list.
- **Dockerfile** – Builds a minimal Docker image (Python 3.12 slim) and runs the app under Gunicorn with TLS.
- **requirements.txt** – Python dependencies (Flask, Requests, etc.).

## Prerequisites

- Python 3.12 (for local development)
- Docker 20.10+ (for containerized deployment)
- An EasyDNS API token with write access to the target zone
- A DNS zone managed in EasyDNS (e.g. `example.com`)

## Installation & Usage

**Clone the repository...**  
```
   git clone https://github.com/your-org/easydns-acme-solver.git
   cd easydns-acme-solver
```
Run locally for testing, or consult `example_helm_template` on how to deploy into k8s after building the image.

**Required  environment variables**

```
EASYDNS_API_TOKEN_NAME="my-token-name"
EASYDNS_API_TOKEN="my-super-secret-token"
```
