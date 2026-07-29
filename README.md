# Sentinel

> An AI-assisted cloud-native secret discovery, governance, and lifecycle management platform.

Sentinel continuously discovers, classifies, analyzes, and governs secrets across modern cloud-native environments. Unlike traditional secret scanners that simply report exposed credentials, Sentinel correlates findings across Git repositories, cloud providers, Kubernetes clusters, and CI/CD pipelines to provide context, ownership, risk assessment, lifecycle tracking, and remediation guidance.

Sentinel is being developed collaboratively using an issue-driven workflow, code reviews, and modern software engineering practices to build a scalable, production-quality security platform.

---

## Table of Contents

- [Core Features](#core-features)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Technology Stack](#technology-stack)
- [Documentation](#documentation)
- [Evaluation Metrics](#evaluation-metrics)
- [Project Tracking](#project-tracking)
- [License](#license)

---

## Core Features

### Secret Discovery
- Git repository scanning
- Kubernetes scanning
- AWS resource scanning
- CI/CD pipeline scanning
- Local filesystem scanning

### Secret Detection
- Regex detection
- Entropy analysis
- Context-aware validation
- Duplicate detection
- Confidence scoring

### AI-Assisted Classification
- Secret type identification
- False positive reduction
- Context analysis
- Severity prediction

### Governance
- Secret lifecycle tracking
- Ownership mapping
- Secret aging
- Rotation monitoring
- Compliance reporting

### Risk Analysis
- Blast radius analysis
- Resource relationship mapping
- Privilege impact analysis
- Risk scoring

### Incident Management
- Finding correlation
- Incident grouping
- Historical tracking
- Audit logs

### Security
- JWT authentication
- RBAC
- Audit logging
- TLS
- Secure API design

---

## Architecture

**Data sources** — Git repositories, AWS accounts, Kubernetes clusters, CI/CD pipelines
→ **Scan Engine** (queue & background workers)
→ **Secret Detection Pipeline**
→ **Context Analysis** + **AI Classification** (parallel)
→ **Risk & Blast Radius Engine**
→ **Secret Lifecycle Management**
→ **PostgreSQL Database**
→ **FastAPI REST APIs**
→ **Next.js Dashboard**

---

## Repository Structure

```text
Sentinel/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── scanners/
│   │   ├── workers/
│   │   ├── utils/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│
├── infrastructure/
│   ├── docker/
│   ├── kubernetes/
│   └── terraform/
│
├── docs/
│   ├── architecture.md
│   ├── roadmap.md
│   ├── api.md
│   ├── database.md
│   ├── scanners.md
│   ├── deployment.md
│   └── decisions.md
│
├── .github/
│
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

---

## Technology Stack

| Category | Tools |
|---|---|
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| Frontend | Next.js, React, Tailwind CSS |
| Cloud | AWS |
| Infrastructure | Docker, Kubernetes, Terraform |
| Security | JWT Authentication, RBAC |
| Monitoring | Prometheus, Grafana |
| CI/CD | GitHub Actions |

---

## Documentation

Full documentation lives in the `docs/` directory:

| Document | Description |
|----------|-------------|
| `architecture.md` | Overall system architecture and component interactions |
| `roadmap.md` | Development roadmap, milestones, and project progress |
| `api.md` | Backend API overview and endpoints |
| `database.md` | Database schema and relationships |
| `scanners.md` | Scanner architecture and supported integrations |
| `deployment.md` | Local development and deployment guide |
| `decisions.md` | Important architectural and design decisions |

---

## Evaluation Metrics

| Metric | Description |
|----------|-------------|
| Precision | Correctly identified secrets |
| Recall | Coverage of exposed secrets |
| F1 Score | Precision/Recall balance |
| False Positive Rate | Incorrect detections |
| Scan Duration | Total scan execution time |
| Detection Accuracy | Overall detection quality |
| MTTD | Mean Time To Detect |
| MTTR | Mean Time To Respond |
| Blast Radius Coverage | Resource impact coverage |

---

## Project Tracking

Progress is tracked through:

- GitHub Issues
- Pull Requests
- Project Board
- `docs/roadmap.md`

---

## License

This project is licensed under the **Apache License 2.0**. You are free to use, modify, and distribute this software in accordance with the terms of the license. See the [LICENSE](LICENSE) file for the full license text.
