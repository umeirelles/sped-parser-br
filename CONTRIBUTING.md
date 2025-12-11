# Contributing to sped-parser

Thank you for your interest in contributing to sped-parser! 🎉

This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

---

## Code of Conduct

Be respectful, inclusive, and collaborative. We're all here to make a better library.

## How Can I Contribute?

### 1. Reporting Bugs

Found a bug? Please [open an issue](https://github.com/umeirelles/sped-parser/issues/new?template=bug_report.md) with:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)

### 2. Suggesting Features

Have an idea? [Open a feature request](https://github.com/umeirelles/sped-parser/issues/new?template=feature_request.md) with:
- Problem description
- Proposed solution
- Use case examples

### 3. Writing Code

Want to contribute code? Great! Here's how:

## Development Setup

### 1. Fork and Clone

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/sped-parser.git
cd sped-parser
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install in Development Mode

```bash
pip install -e ".[dev]"
```

This installs:
- The library in editable mode
- Development dependencies (pytest, black, ruff)

### 4. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-123
```

## Coding Standards

### Python Style

We follow [PEP 8](https://peps.python.org/pep-0008/) with some modifications:

- **Line length**: 100 characters (not 80)
- **Formatting**: Use `black` (auto-formats to our style)
- **Linting**: Use `ruff` (catches common issues)

### Before Committing

**1. Format your code:**
```bash
black src/
```

**2. Check for issues:**
```bash
ruff check src/
```

**3. Run tests (when they exist):**
```bash
pytest
```

### Code Organization

- **One class per file** (unless closely related)
- **Docstrings required** for public methods
- **Type hints encouraged** (but not required)

### Docstring Format

```python
def parse_file(self, file_path: str) -> SPEDData:
    """
    Parse SPED file from filesystem path.

    Args:
        file_path: Path to SPED file

    Returns:
        SPEDData with parsed content

    Raises:
        SPEDFileNotFoundError: If file doesn't exist
        SPEDParseError: If parsing fails
    """
    ...
```

## Project Structure

```
src/sped_parser/
├── __init__.py          # Public API exports
├── base.py              # Abstract base class
├── contribuicoes.py     # EFD Contribuições parser
├── fiscal.py            # EFD Fiscal parser
├── ecd.py               # ECD parser
├── schemas.py           # Pydantic models
├── exceptions.py        # Error classes
└── constants/           # Constants sub-package
    ├── cst.py
    ├── cfop.py
    ├── uf.py
    └── layouts.py
```

## Submitting Changes

### 1. Commit Messages

Use clear, descriptive commit messages:

**Good:**
```
Add support for C197 register in EFD Contribuições

- Parse C197 records with full field extraction
- Add unit tests for C197 parsing
- Update documentation with C197 examples
```

**Bad:**
```
fix bug
```

### 2. Push Your Branch

```bash
git push origin feature/your-feature-name
```

### 3. Create a Pull Request

1. Go to https://github.com/umeirelles/sped-parser/pulls
2. Click "New Pull Request"
3. Select your branch
4. Fill in the PR template with:
   - What changed
   - Why it changed
   - How to test it

### 4. Code Review

- Be patient - reviews may take a few days
- Address feedback constructively
- Make requested changes in new commits (don't force-push)

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sped_parser

# Run specific test file
pytest tests/test_contribuicoes.py

# Run specific test
pytest tests/test_contribuicoes.py::test_parse_c170
```

### Writing Tests

Place tests in `tests/` directory:

```python
# tests/test_contribuicoes.py
import pytest
from sped_parser_br import EFDContribuicoesParser

def test_parse_valid_file():
    parser = EFDContribuicoesParser()
    data = parser.parse_file("tests/fixtures/valid_contrib.txt")

    assert data.header.cnpj == "12345678000190"
    assert len(data.sales_items) > 0

def test_parse_empty_file():
    parser = EFDContribuicoesParser()

    with pytest.raises(SPEDEmptyFileError):
        parser.parse_file("tests/fixtures/empty.txt")
```

## Types of Contributions We Need

### High Priority

- [ ] **Tests**: Unit tests for all parsers
- [ ] **Documentation**: More examples, tutorials
- [ ] **Bug fixes**: See [issues](https://github.com/umeirelles/sped-parser/issues)

### Medium Priority

- [ ] **Performance**: Optimize parsing for large files
- [ ] **New parsers**: EFD-Reinf, eSocial support
- [ ] **Validation**: Validate SPED files against official schemas

### Nice to Have

- [ ] **CLI tool**: Command-line interface
- [ ] **Export**: Generate SPED files from Python data
- [ ] **Async**: Async parsers for concurrent processing

## Questions?

- **General questions**: [Open a discussion](https://github.com/umeirelles/sped-parser/discussions)
- **Bug reports**: [Open an issue](https://github.com/umeirelles/sped-parser/issues/new?template=bug_report.md)
- **Feature requests**: [Open an issue](https://github.com/umeirelles/sped-parser/issues/new?template=feature_request.md)

## Recognition

All contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in commit history

Thank you for making sped-parser better! 🚀
