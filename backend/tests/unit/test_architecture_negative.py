import os
from pathlib import Path
from tempfile import TemporaryDirectory
import pytest
from backend.tests.unit.test_architecture import get_imports

def test_negative_architecture():
    # Test that the scanner catches violations in synthetic files
    with TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        # 1. ai importing analysis
        ai_dir = tmp / "backend" / "app" / "ai"
        ai_dir.mkdir(parents=True)
        (ai_dir / "bad_ai.py").write_text("import backend.app.analysis.module")

        # 2. analysis importing ai
        analysis_dir = tmp / "backend" / "app" / "analysis"
        analysis_dir.mkdir(parents=True)
        (analysis_dir / "bad_analysis.py").write_text("from backend.app.ai import module")

        # 3. application importing ai (not container.py)
        app_dir = tmp / "backend" / "app" / "application"
        app_dir.mkdir(parents=True)
        (app_dir / "bad_app.py").write_text("import backend.app.ai")
        
        # 4. anything importing api
        (analysis_dir / "bad_api_imp.py").write_text("import backend.app.api.router")

        def check_violations(root_path):
            violations = []
            for root, _, files in os.walk(root_path):
                for file in files:
                    if not file.endswith(".py"):
                        continue
                    path = Path(root) / file
                    imports = get_imports(path)
                    
                    if "analysis" in path.parts:
                        for imp in imports:
                            if imp.startswith("backend.app.ai"):
                                violations.append(f"{path} imports ai")
                                
                    if "ai" in path.parts:
                        for imp in imports:
                            if imp.startswith("backend.app.analysis"):
                                violations.append(f"{path} imports analysis")

                    if "api" not in path.parts and "main.py" not in path.name:
                        for imp in imports:
                            if imp.startswith("backend.app.api"):
                                violations.append(f"{path} imports api")
                    
                    if "application" in path.parts and path.name != "container.py":
                        for imp in imports:
                            if imp.startswith("backend.app.ai"):
                                violations.append(f"{path} imports ai")
            return violations

        violations = check_violations(tmp / "backend" / "app")
        assert len(violations) >= 4, "Negative test failed to catch layer violations"
