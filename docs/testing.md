# Testing

The system employs a rigorous test-first methodology utilizing Pytest to validate both the domain model and the pipeline logic.

### How to Run Tests
The test suite can be invoked via the provided project tasks script:
```bash
python scripts/tasks.py test
```
Alternatively, you can run pytest directly on the backend source:
```bash
python -m pytest backend/tests -v
```

### Test Suite Breakdown
The testing effort is cleanly split between isolated component checks and full end-to-end integration boundaries:
- **Integration Tests (15)**: Found in `backend/tests/integration/test_sample_cases.py`, covering the 15 end-to-end golden cases simulating realistic runtime payload evaluation.
- **Unit Tests (44)**: Covering architecture boundaries, preprocessor logic, tracebacks, confidence calculations, redacting mechanics, and specific rule engine bounds.

### Coverage Note
The test suite asserts high coverage on the core orchestrator and the pipeline sequence. Continuous integration pipelines will ensure that coverage bounds on `backend/app/analysis/` and `backend/app/application/` remain strictly adhered to as the project expands.
