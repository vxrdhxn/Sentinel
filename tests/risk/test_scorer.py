import pytest
from pydantic import ValidationError

from backend.app.risk.models import (
    ExposureLevel,
    RiskFindingInput,
    RiskSecretType,
    RiskSeverity,
    RiskSource,
)
from backend.app.risk.scorer import RiskScorer


@pytest.fixture
def scorer() -> RiskScorer:
    return RiskScorer()


def make_finding(**overrides: object) -> RiskFindingInput:
    values = {
        "secret_type": RiskSecretType.UNKNOWN,
        "confidence": 0.0,
        "exposure": ExposureLevel.LOCAL,
        "source": RiskSource.GIT,
        "high_impact_resource": False,
    }
    values.update(overrides)
    return RiskFindingInput(**values)


def test_minimum_score(scorer: RiskScorer) -> None:
    result = scorer.score(make_finding())

    assert result.score == 0.0
    assert result.severity == RiskSeverity.LOW


def test_maximum_score(scorer: RiskScorer) -> None:
    result = scorer.score(
        make_finding(
            secret_type=RiskSecretType.CLOUD_CREDENTIAL,
            confidence=1.0,
            exposure=ExposureLevel.PUBLIC,
            source=RiskSource.CLOUD,
            high_impact_resource=True,
        )
    )

    assert result.score == 100.0
    assert result.severity == RiskSeverity.CRITICAL


@pytest.mark.parametrize(
    ("score_inputs", "expected_severity"),
    [
        ({"confidence": 0.0}, RiskSeverity.LOW),
        (
            {
                "secret_type": RiskSecretType.API_KEY,
                "confidence": 0.0,
                "exposure": ExposureLevel.LOCAL,
                "source": RiskSource.GIT,
            },
            RiskSeverity.MEDIUM,
        ),
        (
            {
                "secret_type": RiskSecretType.API_KEY,
                "confidence": 0.0,
                "exposure": ExposureLevel.PUBLIC,
                "source": RiskSource.KUBERNETES,
            },
            RiskSeverity.HIGH,
        ),
        (
            {
                "secret_type": RiskSecretType.CLOUD_CREDENTIAL,
                "confidence": 1.0,
                "exposure": ExposureLevel.PUBLIC,
                "source": RiskSource.CLOUD,
                "high_impact_resource": True,
            },
            RiskSeverity.CRITICAL,
        ),
    ],
)
def test_severity_mapping(
    scorer: RiskScorer,
    score_inputs: dict[str, object],
    expected_severity: RiskSeverity,
) -> None:
    result = scorer.score(make_finding(**score_inputs))

    assert result.severity == expected_severity


@pytest.mark.parametrize("secret_type", list(RiskSecretType))
def test_secret_type_affects_score(
    scorer: RiskScorer,
    secret_type: RiskSecretType,
) -> None:
    result = scorer.score(make_finding(secret_type=secret_type))

    assert result.breakdown.secret_type >= 0.0


@pytest.mark.parametrize(
    ("confidence", "expected_score"),
    [
        (0.0, 0.0),
        (0.5, 10.0),
        (1.0, 20.0),
    ],
)
def test_confidence_affects_score(
    scorer: RiskScorer,
    confidence: float,
    expected_score: float,
) -> None:
    result = scorer.score(make_finding(confidence=confidence))

    assert result.breakdown.confidence == expected_score
    assert result.score == expected_score


@pytest.mark.parametrize(
    ("exposure", "expected_score"),
    [
        (ExposureLevel.LOCAL, 0.0),
        (ExposureLevel.INTERNAL, 12.0),
        (ExposureLevel.PUBLIC, 25.0),
    ],
)
def test_exposure_affects_score(
    scorer: RiskScorer,
    exposure: ExposureLevel,
    expected_score: float,
) -> None:
    result = scorer.score(make_finding(exposure=exposure))

    assert result.breakdown.exposure == expected_score
    assert result.score == expected_score


@pytest.mark.parametrize(
    ("source", "expected_score"),
    [
        (RiskSource.GIT, 0.0),
        (RiskSource.KUBERNETES, 5.0),
        (RiskSource.CICD, 8.0),
        (RiskSource.CLOUD, 10.0),
    ],
)
def test_source_affects_score(
    scorer: RiskScorer,
    source: RiskSource,
    expected_score: float,
) -> None:
    result = scorer.score(make_finding(source=source))

    assert result.breakdown.source == expected_score
    assert result.score == expected_score


def test_high_impact_resource_affects_score(scorer: RiskScorer) -> None:
    normal = scorer.score(make_finding(high_impact_resource=False))
    high_impact = scorer.score(make_finding(high_impact_resource=True))

    assert normal.breakdown.resource_impact == 0.0
    assert high_impact.breakdown.resource_impact == 15.0
    assert high_impact.score - normal.score == 15.0


@pytest.mark.parametrize(
    ("confidence", "expected"),
    [
        (0.0, 0.0),
        (1.0, 20.0),
    ],
)
def test_confidence_boundaries(
    scorer: RiskScorer,
    confidence: float,
    expected: float,
) -> None:
    result = scorer.score(make_finding(confidence=confidence))

    assert result.breakdown.confidence == expected


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_invalid_confidence_is_rejected(confidence: float) -> None:
    with pytest.raises(ValidationError):
        make_finding(confidence=confidence)


def test_missing_required_input_is_rejected() -> None:
    with pytest.raises(ValidationError):
        RiskFindingInput(
            confidence=0.5,
            exposure=ExposureLevel.PUBLIC,
            source=RiskSource.GIT,
        )


def test_score_is_deterministic(scorer: RiskScorer) -> None:
    finding = make_finding(
        secret_type=RiskSecretType.DATABASE_CREDENTIAL,
        confidence=0.73,
        exposure=ExposureLevel.INTERNAL,
        source=RiskSource.CICD,
        high_impact_resource=True,
    )

    first = scorer.score(finding)
    second = scorer.score(finding)

    assert first == second


def test_breakdown_sums_to_total_score(scorer: RiskScorer) -> None:
    result = scorer.score(
        make_finding(
            secret_type=RiskSecretType.PRIVATE_KEY,
            confidence=0.8,
            exposure=ExposureLevel.PUBLIC,
            source=RiskSource.CLOUD,
            high_impact_resource=True,
        )
    )

    breakdown_total = sum(
        [
            result.breakdown.secret_type,
            result.breakdown.confidence,
            result.breakdown.exposure,
            result.breakdown.source,
            result.breakdown.resource_impact,
        ]
    )

    assert breakdown_total == result.score


def test_result_contains_no_secret_material(scorer: RiskScorer) -> None:
    result = scorer.score(
        make_finding(
            secret_type=RiskSecretType.API_KEY,
            confidence=0.9,
            exposure=ExposureLevel.PUBLIC,
            source=RiskSource.GIT,
        )
    )

    assert set(result.model_dump().keys()) == {
        "score",
        "severity",
        "breakdown",
    }
