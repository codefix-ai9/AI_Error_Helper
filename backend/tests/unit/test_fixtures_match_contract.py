import json
from pathlib import Path
from backend.app.models.responses import AnalysisResult
from backend.app.models.envelope import Envelope, ErrorResponse

FIXTURES_DIR = Path("data/contract_fixtures")

def test_result_hybrid_ok():
    with open(FIXTURES_DIR / "result_hybrid_ok.json", "r") as f:
        data = json.load(f)
    result = AnalysisResult(**data)
    assert result.error_type == "Name / Reference"
    assert result.schema_version == "1.0"
