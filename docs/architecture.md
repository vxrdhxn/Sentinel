# Architecture

## Overview

Sentinel is an cloud-native secret discovery, governance, and lifecycle management platform.

It is a cloud-native cybersecurity platform designed to continuously discover, classify, analyze, and govern secrets across modern cloud-native environments.

Unlike traditional secret scanners that simply report exposed credentials, Sentinel correlates findings across Git repositories, cloud providers, Kubernetes clusters, and CI/CD pipelines to provide context, ownership, risk assessment, lifecycle tracking, and remediation guidance.

Sentinel is being developed collaboratively using issue-driven workflow, code reviews, and modern software engineering practices to build a scalable, production-quality security platform.

---


## Database Layer

Database access goes through `backend/app/database.py`:
- `engine` / `SessionLocal` are configured from `settings.database_url` (backend/app/config.py)
- Use the `get_db()` generator as a FastAPI dependency to get a request-scoped session
- `check_database_connection()` is used by the `/health` endpoint to verify connectivity

### Local development
Start Postgres via Docker:
    docker compose up -d
Copy `.env.example` to `.env` and set `DATABASE_URL` to match your Postgres port
(default container port 5432, but check for local Postgres conflicts — see below)

**Note:** if you have a local Postgres installation also running on port 5432,
the Docker container will conflict. Either stop the local service or remap the
container port (e.g. `5433:5432` in docker-compose.yml) and update `DATABASE_URL` accordingly.


## Design Principles

The architecture of Sentinel is guided by a set of core design principles that prioritize maintainability, extensibility, security, and scalability. These principles influence every major architectural and implementation decision throughout the project.

### Modular Architecture

Sentinel is designed as a collection of independent modules, each responsible for a single area of functionality, such as scanning, analysis, risk assessment, or reporting. Clear separation of responsibilities simplifies development, testing, and future enhancements while allowing individual components to evolve independently.

### Security by Design

As a cybersecurity platform, security is treated as a fundamental design requirement rather than an afterthought. Sensitive information is handled using secure development practices, least-privilege access, strong authentication and authorization mechanisms, encrypted communication, and secure secret management.

### Extensibility

The platform is designed to support new scanners, cloud providers, analysis engines, and integrations with minimal changes to the existing codebase. New capabilities should integrate through well-defined interfaces rather than requiring modifications to core components.

### Separation of Concerns

Each component has a clearly defined responsibility and avoids overlapping functionality. Scanning, analysis, risk evaluation, storage, and presentation remain independent, reducing coupling and improving maintainability.

### API-First Design

All core functionality is exposed through well-defined REST APIs. This enables multiple clients including web applications, command-line tools, and future third-party integrations-to interact with Sentinel through a consistent interface.

### Cloud-Native Architecture

Sentinel is designed with cloud-native environments in mind. The architecture supports modern infrastructure such as Kubernetes, containerized applications, CI/CD pipelines, and cloud platforms while remaining portable across deployment environments.

### Scalability

The architecture should support increasing workloads by allowing components to scale independently. Resource-intensive operations such as scanning and analysis should be designed to execute concurrently and, where appropriate, asynchronously.

### Observability

The system should provide comprehensive logging, metrics, and health information to simplify monitoring, debugging, auditing, and operational troubleshooting. Every significant operation should be traceable throughout the system.

### Reliability

Sentinel should continue operating reliably even when individual integrations or external services become unavailable. Components should fail gracefully, isolate errors where possible, and provide meaningful feedback for recovery and troubleshooting.

### Maintainability

Code should be written with readability, consistency, and long-term maintenance in mind. Common conventions, documentation, testing practices, and clear architectural boundaries help ensure that contributors can understand and evolve the project efficiently.

### Open Source Collaboration

The project should be approachable for contributors with varying levels of experience. Clear documentation, consistent coding standards, transparent decision-making, and predictable project organization encourage community participation and long-term sustainability.

---

## Problem Statement

Modern cloud-native applications depend on a large number of credentials, API keys, access tokens, certificates, and other secrets to communicate with applications, cloud services, databases, CI/CD systems, and infrastructure.

As development environments become distributed across Git repositories, cloud platforms, Kubernetes clusters, and CI/CD pipelines, secrets can become scattered across multiple systems. This makes it difficult to maintain a centralized understanding of where secrets exist, who owns them, how they are being used, and what impact their exposure may have.

Existing secret scanning tools are effective at detecting many types of exposed credentials, but detection alone does not provide the complete context required for effective secret governance. Security teams need to understand the severity, ownership, relationships, lifecycle state, and potential impact of a finding.

Sentinel addresses this gap by combining secret discovery with contextual analysis, risk assessment, ownership information, and lifecycle-oriented governance across cloud-native environments.

---

## Goals

Sentinel aims to:

- Discover exposed secrets across multiple development and
  cloud-native environments.
- Normalize findings from different sources into a common format.
- Classify discovered secrets based on their type and context.
- Assess the risk associated with individual findings.
- Provide ownership and contextual information for discovered secrets.
- Track the lifecycle of secrets and security findings.
- Provide remediation guidance for security findings.
- Provide a centralized interface for security teams to review
  and manage findings.
- Support the addition of new scanners and integrations without
  requiring major changes to the core platform.

---

## MVP Scope

The MVP will demonstrate an end-to-end secret discovery and
governance workflow.

### Included

- User authentication.
- Local repository/directory scanning.
- Secret detection using configurable detection rules.
- Finding normalization.
- Basic secret classification.
- Risk assessment.
- Persistent storage of scan results and findings.
- REST API for accessing scan and finding information.
- Web dashboard for viewing and filtering findings.

### Planned Extensions

- GitHub repository scanning.
- Cloud provider integrations.
- Kubernetes scanning.
- CI/CD integrations.
- Advanced contextual classification.
- Ownership inference.
- Blast radius analysis.
- Secret lifecycle tracking.
- Remediation workflows.

---

## High-Level Architecture

Sentinel follows a modular architecture in which source-specific
scanners collect potential secrets, analysis components process and
enrich the resulting findings, and the backend provides a unified
interface for storage and presentation.

At a high level, the system consists of:

1. Client Layer
2. API Layer
3. Scanning Layer
4. Analysis Layer
5. Governance Layer
6. Persistence Layer

                    ┌──────────────┐
                    │     User     │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Next.js    │
                    │  Dashboard   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   FastAPI    │
                    │     API      │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         ┌─────────┐ ┌───────────┐ ┌──────────┐
         │Scanner  │ │ Analysis  │ │Governance│
         │ Engine  │ │  Engine   │ │  Engine  │
         └────┬────┘ └─────┬─────┘ └────┬─────┘
              │            │             │
              └────────────┼─────────────┘
                           ▼
                    ┌──────────────┐
                    │ PostgreSQL   │
                    └──────────────┘

---

## Core Components

## Continuous Integration

Every pull request targeting `main` runs automated checks via GitHub Actions
(`.github/workflows/backend-ci.yml`):
- `ruff check` — lint
- `ruff format --check` — formatting
- `pytest` — test suite

All checks must pass before a PR can be merged. Run them locally before pushing:

    uv run ruff check .
    uv run ruff format --check .
    uv run pytest -v

If `ruff format --check` fails, auto-fix with:

    uv run ruff format .

## API Routing

Versioned API routes live under `backend/app/api/`:
- `backend/app/api/router.py` — central router, mounts versioned sub-routers
- `backend/app/api/v1/router.py` — v1 endpoints, mounted at `/api/v1`

New v1 endpoints go in `backend/app/api/v1/router.py`. Future versions (v2, etc.)
get their own package under `backend/app/api/`, registered in `api/router.py`.

### Client Layer

The client layer provides the web interface through which users
authenticate, initiate scans, view findings, and interact with
Sentinel.

### API Layer

The API layer exposes Sentinel's functionality through REST APIs
and acts as the boundary between clients and backend services.

## Classification & Normalization

Converts raw scanner output into Sentinel's internal representation:
`backend/app/classification/`
- `taxonomy.py` — deterministic mapping from RawSecretType (scanner) to SecretType (domain model);
  unrecognized raw types fall back to GENERIC_CREDENTIAL rather than failing
- `models.py` — `NormalizedFinding`, the output shape compatible with Secret/Finding
- `normalizer.py` — `normalize_scan_result()`, converts a ScanResult into a NormalizedFinding,
  including splitting a "file.py:42" location string into file_path + line_number

This layer is pure transformation — no persistence, no risk scoring, no API concerns.

### Scanner Engine

The scanner engine is responsible for collecting data from
supported sources and identifying content that should be analyzed.

The scanner architecture is designed around a common interface so
that additional sources can be integrated independently.

Initial sources will focus on local repositories and directories,
with GitHub, cloud providers, Kubernetes, and CI/CD systems planned
as extensions.

### Analysis Engine

The analysis layer processes scanner output and enriches findings
with information such as secret type, confidence, and contextual
metadata.

### Risk Engine

The risk engine evaluates findings using contextual information and
assigns a risk level to help prioritize security findings.

## Repository Layer

Persistence logic lives in `backend/app/repositories/`:
- `base.py` — `BaseRepository[ModelT]` with shared CRUD (get_by_id, list_all, add, delete)
- `secret_repository.py` — `SecretRepository`, adds `get_by_fingerprint`
- `finding_repository.py` — `FindingRepository`, adds `list_by_secret`, `list_by_status`

Repositories take an existing `Session` (never create their own engine/session)
and don't commit — the caller owns the transaction boundary. Business rules
(e.g. risk decisions) belong in a service layer above this, not here.

### Governance Layer

The governance layer maintains ownership, lifecycle information,
remediation status, and other management metadata associated with
findings.

### Persistence Layer

The persistence layer stores users, scan information, findings,
metadata, and governance information in PostgreSQL.

---

## Data Flow

A typical scanning workflow follows these stages:

1. A user initiates a scan through the web interface.
2. The frontend sends the scan request to the backend API.
3. The API validates the request and starts the appropriate scanner.
4. The scanner collects data from the selected source.
5. The detection engine identifies potential secrets.
6. Detected secrets are converted into normalized findings.
7. The analysis layer classifies and enriches the findings.
8. The risk engine evaluates the findings.
9. Governance metadata is associated with the findings where available.
10. The resulting scan and finding information is persisted.
11. The API exposes the results to the frontend.
12. The dashboard presents the findings to the user.

---

