from app.scanners.base import Scanner
from app.scanners.dummy import DummyScanner
from app.scanners.models import ScanInput, ScanResult


def test_scan_input_validates():
    inp = ScanInput(target_id="my/repo", content="some file content", source_path="config.py")
    assert inp.target_id == "my/repo"


def test_dummy_scanner_satisfies_protocol():
    scanner = DummyScanner()
    assert isinstance(scanner, Scanner)


def test_dummy_scanner_returns_scan_results():
    scanner: Scanner = DummyScanner()
    results = scanner.scan(ScanInput(target_id="my/repo", content="fake content"))
    assert len(results) == 1
    assert isinstance(results[0], ScanResult)
    assert 0.0 <= results[0].confidence <= 1.0


def test_second_implementation_is_substitutable():
    class OtherScanner:
        def scan(self, scan_input: ScanInput) -> list[ScanResult]:
            return []

    scanner: Scanner = OtherScanner()
    assert isinstance(scanner, Scanner)
    assert scanner.scan(ScanInput(target_id="x", content="y")) == []
