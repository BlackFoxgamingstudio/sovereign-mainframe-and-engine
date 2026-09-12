# Contributing to Sovereign Mainframe & Autonomous Protocol Engine

We welcome contributions from developers worldwide!

## Principles
1. **Zero External Core Dependencies**: All core engines and adapters must run cleanly on standard Python 3.10+ libraries.
2. **100% Test Coverage**: Every PR must include unit tests verifying state transitions, cryptographic integrity, and error boundaries.
3. **Security First**: No hardcoded keys or unverified hash transitions.

## Pull Request Workflow
1. Fork repository and create a feature branch (`feat/your-feature`).
2. Implement your changes following PEP 8 guidelines.
3. Run test suite: `pytest tests/ -v`.
4. Submit PR against `main` branch.
