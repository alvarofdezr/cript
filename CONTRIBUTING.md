# Contributing to CRIPT

Thank you for your interest in contributing to CRIPT! We welcome contributions from the community.

## Code of Conduct

Please be respectful and professional in all interactions.

## Getting Started

1. **Install UV** (modern Python package manager)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Fork and clone the repository**
   ```bash
   git clone https://github.com/alvarofdezr/cript.git
   cd cript
   ```

3. **Install dependencies with UV**
   ```bash
   uv sync --group dev
   ```

4. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Code Style

We follow PEP 8 using modern tools:

```bash
# Format code with Black
uv run black src/cript tests

# Check with flake8
uv run flake8 src/cript tests

# Sort imports with isort
uv run isort src/cript tests

# Type checking with mypy
uv run mypy src/cript
```

### Testing

All new features must include tests:

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src/cript --cov-report=html

# Run specific test file
uv run pytest tests/test_protocol.py -v
```

### Commit Messages

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `chore:` Dependencies, build, etc.

Example:
```
feat: implement AES-GCM symmetric encryption
```

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Run full test suite** locally before pushing
4. **Describe changes** clearly in PR description
5. **Link related issues** with `Fixes #123`

## Security Issues

**Do NOT** open a public issue for security vulnerabilities. See [SECURITY.md](SECURITY.md) for reporting procedures.

## Contribution Areas

### High Priority
- [ ] AES-GCM symmetric encryption implementation
- [ ] Extended Key Exchange Protocol (EKEP)
- [ ] Comprehensive security audit
- [ ] Production deployment guide

### Medium Priority
- [ ] Multi-recipient group messaging
- [ ] Key directory service
- [ ] Kubernetes deployment
- [ ] Web dashboard

### Documentation
- [ ] API reference
- [ ] Protocol specification
- [ ] Deployment guides
- [ ] Security analysis

## Questions?

- **Issues**: Check existing GitHub issues
- **Discussions**: Use GitHub Discussions
- **Email**: your.email@example.com

---

Thank you for contributing to CRIPT! 🔐
