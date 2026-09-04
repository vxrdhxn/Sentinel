from backend.app.risk.models import (
    RiskBreakdown,
    RiskFindingInput,
    RiskScoreResult,
    RiskSeverity,
)
from backend.app.risk.rules import (
    CONFIDENCE_MAX_SCORE,
    EXPOSURE_SCORES,
    HIGH_IMPACT_RESOURCE_SCORE,
    SECRET_TYPE_SCORES,
    SEVERITY_THRESHOLDS,
    SOURCE_SCORES,
)


class RiskScorer:
    """Deterministic risk scorer for normalized findings."""

    def score(self, finding: RiskFindingInput) -> RiskScoreResult:
        secret_type_score = SECRET_TYPE_SCORES[finding.secret_type]
        confidence_score = finding.confidence * CONFIDENCE_MAX_SCORE
        exposure_score = EXPOSURE_SCORES[finding.exposure]
        source_score = SOURCE_SCORES[finding.source]
        resource_impact_score = HIGH_IMPACT_RESOURCE_SCORE if finding.high_impact_resource else 0.0

        breakdown = RiskBreakdown(
            secret_type=secret_type_score,
            confidence=confidence_score,
            exposure=exposure_score,
            source=source_score,
            resource_impact=resource_impact_score,
        )

        score = round(
            secret_type_score
            + confidence_score
            + exposure_score
            + source_score
            + resource_impact_score,
            2,
        )

        return RiskScoreResult(
            score=score,
            severity=self._severity_for_score(score),
            breakdown=breakdown,
        )

    @staticmethod
    def _severity_for_score(score: float) -> RiskSeverity:
        for threshold, severity in SEVERITY_THRESHOLDS:
            if score >= threshold:
                return severity

        return RiskSeverity.LOW
