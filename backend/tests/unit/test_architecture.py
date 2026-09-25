import ast
import os
from pathlib import Path

def get_imports(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError:
            return set()
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports

def test_architecture_layer_rules():
    backend_app = Path("backend/app")
    if not backend_app.exists():
        return  # skip if not run from root
        
    for root, _, files in os.walk(backend_app):
        for file in files:
            if not file.endswith(".py"):
                continue
            path = Path(root) / file
            imports = get_imports(path)
            
            # Rule: analysis never imports ai (except in application/container.py where factories are injected)
            if "analysis" in path.parts:
                for imp in imports:
                    assert not imp.startswith("backend.app.ai"), f"Layer violation: {path} imports {imp}"
            
            # Rule: ai cannot import analysis (must remain decoupled)
            if "ai" in path.parts:
                for imp in imports:
                    assert not imp.startswith("backend.app.analysis"), f"Layer violation: {path} imports {imp}"

            # Rule: frontend logic never duplicates backend rules (we only check backend here)
            # Rule: No module imports api (api depends on application, not vice-versa)
            if "api" not in path.parts and "main.py" not in path.name:
                for imp in imports:
                    assert not imp.startswith("backend.app.api"), f"Layer violation: {path} imports {imp}"

            # Whitelist check for container.py
            if "application" in path.parts:
                if path.name != "container.py":
                    for imp in imports:
                        assert not imp.startswith("backend.app.ai"), f"Layer violation: {path} imports {imp}"
                else:
                    # container.py is allowed to import factories from ai
                    pass
