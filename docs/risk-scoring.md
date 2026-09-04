# Sentinel Risk Scoring

## Overview

Sentinel uses a deterministic risk scoring component to prioritize normalized secret findings.

The risk scorer is independent of scanners, APIs, authentication, and database persistence. It receives normalized finding attributes and produces a numerical risk score, severity classification, and factor breakdown.

The scoring pipeline is:

Normalized Finding → Risk Scoring → Risk Score → Severity → Governance/Prioritization

## Scoring Model

The total risk score ranges from 0 to 100.

The score is calculated from five factors:

| Factor | Maximum Score |
|---|---:|
| Secret Type | 30 |
| Detection Confidence | 20 |
| Exposure | 25 |
| Source | 10 |
| Resource Impact | 15 |
| **Total** | **100** |

### Formula

```text
Risk Score =
    Secret Type Score
  + Confidence Score
  + Exposure Score
  + Source Score
  + Resource Impact Score