# Building a Python Library: A Complete Guide

**For**: First-time library authors
**Level**: Beginner to Intermediate
**Time to read**: 20 minutes

---

## Table of Contents

1. [What is a Library?](#what-is-a-library)
2. [Library vs Application](#library-vs-application)
3. [Anatomy of sped-parser](#anatomy-of-sped-parser)
4. [How Python Finds Your Code](#how-python-finds-your-code)
5. [The Import System](#the-import-system)
6. [Package Structure Deep Dive](#package-structure-deep-dive)
7. [Building Blocks](#building-blocks)
8. [The Publishing Process](#the-publishing-process)
9. [How Users Consume Your Library](#how-users-consume-your-library)
10. [Common Patterns](#common-patterns)

---

## What is a Library?

### The Restaurant Analogy

Think of software like restaurants:

| Type | What It Is | Example |
|------|------------|---------|
| **Application** | A full restaurant | You walk in, sit down, order food, eat |
| **Library** | A commercial kitchen supplier | Provides tools/ingredients for restaurants to use |

A **library** doesn't do anything by itself. It provides **reusable tools** that other programs can use.

### Real-World Example

```python
# This is a LIBRARY (provides tools)
import sped_parser

# This is an APPLICATION (uses the tools)
parser = sped_parser.EFDContribuicoesParser()
data = parser.parse_file("myfile.txt")
print(data.header.company_name)
```

**The library** (`sped_parser`) provides the `EFDContribuicoesParser` class.

**The application** (your script) uses that class to do actual work.

---

## Library vs Application

### Application (Streamlit App)

```
taxdash-mvp/
├── reforma-trib-app-tabs.py  ← You RUN this
├── requirements.txt
└── taxdash/
    ├── loaders.py            ← Helper modules
    └── processors.py
```

**How it works**:
1. You type: `streamlit run reforma-trib-app-tabs.py`
2. It shows a web page
3. You upload files, click buttons
4. It displays results

**Purpose**: Do a specific job (simulate tax reform)

### Library (sped-parser)

```
sped-parser/
├── src/sped_parser/          ← Code OTHER programs import
│   ├── __init__.py
│   ├── base.py
│   └── ...
├── pyproject.toml            ← Build instructions
└── README.md                 ← Documentation
```

**How it works**:
1. User types: `pip install sped-parser`
2. Now any Python program can do: `import sped_parser`
3. The program uses your tools

**Purpose**: Provide reusable tools for OTHER programs

---

## Anatomy of sped-parser

### The Big Picture

```
sped-parser/
│
├── src/                      ← SOURCE CODE (the actual library)
│   └── sped_parser/         ← The Python package
│       ├── __init__.py      ← Package entry point
│       ├── base.py          ← Abstract base class
│       ├── contribuicoes.py ← Concrete parser 1
│       ├── fiscal.py        ← Concrete parser 2
│       ├── ecd.py           ← Concrete parser 3
│       ├── schemas.py       ← Data structures
│       ├── exceptions.py    ← Error types
│       └── constants/       ← Sub-package
│           ├── __init__.py
│           ├── cst.py
│           ├── cfop.py
│           ├── uf.py
│           └── layouts.py
│
├── examples/                 ← USAGE EXAMPLES (not part of library)
│   └── basic_usage.py
│
├── tests/                    ← TESTS (not part of library)
│   └── test_*.py
│
├── pyproject.toml            ← BUILD CONFIGURATION
├── README.md                 ← DOCUMENTATION
├── LICENSE                   ← LEGAL
└── CHANGELOG.md              ← VERSION HISTORY
```

### What Gets Installed

When someone does `pip install sped-parser`, they get:

```
site-packages/
└── sped_parser/              ← Only this!
    ├── __init__.py
    ├── base.py
    ├── contribuicoes.py
    ├── fiscal.py
    ├── ecd.py
    ├── schemas.py
    ├── exceptions.py
    └── constants/
        ├── __init__.py
        ├── cst.py
        ├── cfop.py
        ├── uf.py
        └── layouts.py
```

**They do NOT get**:
- ❌ `examples/` - These are just for documentation
- ❌ `tests/` - Only developers need these
- ❌ `README.md`, `LICENSE` - Metadata only
- ❌ `pyproject.toml` - Build instructions only

---

## How Python Finds Your Code

### Python's Search Path

When you do `import sped_parser`, Python looks in these places **in order**:

```python
import sys
print(sys.path)
```

Output:
```
[
    '',                                    # 1. Current directory
    '/usr/lib/python3.11',                # 2. Standard library
    '/usr/lib/python3.11/site-packages',  # 3. Installed packages ← YOUR LIBRARY HERE
    ...
]
```

### During Development (Before Publishing)

Your library isn't installed yet. Two options:

**Option 1: Add to sys.path manually**
```python
import sys
sys.path.insert(0, '/path/to/sped-parser/src')
import sped_parser  # Now Python can find it
```

**Option 2: Editable install** (BEST for development)
```bash
cd /path/to/sped-parser
pip install -e .
```

This creates a **symlink** from `site-packages` to your source:
```
site-packages/
└── sped-parser.egg-link  → /path/to/sped-parser/src/sped_parser
```

Now changes you make are **immediately available** without reinstalling!

---

## The Import System

### What is `__init__.py`?

`__init__.py` makes a directory into a **Python package**.

#### Without `__init__.py`:

```
my_code/
├── parser.py
└── schemas.py
```

```python
import my_code  # ❌ ERROR: No module named 'my_code'
```

#### With `__init__.py`:

```
my_code/
├── __init__.py    ← This file makes it a package!
├── parser.py
└── schemas.py
```

```python
import my_code  # ✅ WORKS!
```

### What Goes in `__init__.py`?

`__init__.py` is the **entry point** - it runs when someone imports your package.

**Minimal** (empty):
```python
# src/sped_parser/__init__.py
# Empty file - package exists but exports nothing convenient
```

**User experience**:
```python
import sped_parser
# Nothing useful here, must do:
from sped_parser.contribuicoes import EFDContribuicoesParser
```

**Better** (with exports):
```python
# src/sped_parser/__init__.py
from .contribuicoes import EFDContribuicoesParser
from .fiscal import EFDFiscalParser
from .ecd import ECDParser

__all__ = ['EFDContribuicoesParser', 'EFDFiscalParser', 'ECDParser']
```

**User experience**:
```python
from sped_parser import EFDContribuicoesParser  # ✅ Clean!
```

### Relative vs Absolute Imports

**Inside your library files**, use **relative imports**:

```python
# ✅ GOOD (relative import)
# src/sped_parser/contribuicoes.py
from .base import SPEDParser
from .schemas import SPEDData
from .constants import PARENT_CODES_CONTRIBUICOES

# ❌ BAD (absolute import)
from sped_parser.base import SPEDParser  # Breaks if package renamed
```

**Why?**
- ✅ Works regardless of package name
- ✅ Works during development
- ✅ Clearer that it's internal

**Outside your library** (in user code), use **absolute imports**:

```python
# User's script.py
from sped_parser import EFDContribuicoesParser  # ✅ Absolute
```

---

## Package Structure Deep Dive

### Single vs Multi-File Packages

#### Single-File Package

```
simple_lib/
└── src/
    └── simple_lib/
        └── __init__.py    ← Everything in one file (1000 lines)
```

**Good for**: Tiny libraries (<500 lines)

#### Multi-File Package (Our Approach)

```
sped_parser/
└── src/
    └── sped_parser/
        ├── __init__.py        ← Exports only (60 lines)
        ├── base.py            ← Base class (280 lines)
        ├── contribuicoes.py   ← Parser 1 (330 lines)
        ├── fiscal.py          ← Parser 2 (250 lines)
        └── ecd.py             ← Parser 3 (220 lines)
```

**Good for**: Any serious library
**Benefits**:
- ✅ Easy to navigate
- ✅ Clear separation of concerns
- ✅ Multiple developers can work in parallel
- ✅ Easier to test individual modules

### Sub-Packages

A package can contain other packages:

```
sped_parser/
└── constants/           ← Sub-package
    ├── __init__.py     ← Makes it a package
    ├── cst.py
    ├── cfop.py
    └── layouts.py
```

**How to import**:

```python
# From outside
from sped_parser.constants import CST_PIS_COFINS

# From inside sped_parser/base.py
from .constants import ENCODING, DELIMITER
```

**When to use sub-packages**:
- ✅ Logical grouping (all constants together)
- ✅ Many related files (4+ files doing similar things)
- ✅ Optional components (user might not need all of them)

---

## Building Blocks

### 1. Abstract Base Classes (ABC)

**What**: A template that other classes must follow

**Why**: Enforce a contract across multiple implementations

```python
# base.py
from abc import ABC, abstractmethod

class SPEDParser(ABC):
    """Template for all SPED parsers."""

    @abstractmethod
    def _extract_data(self, df):
        """Subclasses MUST implement this."""
        ...

    def parse(self, content):
        """Shared logic - works for all parsers."""
        df = self._read_file(content)
        return self._extract_data(df)  # Calls subclass method
```

```python
# contribuicoes.py
class EFDContribuicoesParser(SPEDParser):
    def _extract_data(self, df):
        # Specific implementation for Contribuições
        return SPEDData(...)
```

**Pattern**: Template Method Pattern
**Benefit**: Common code (file reading) in one place, specific logic (data extraction) in subclasses

### 2. Pydantic Models

**What**: Classes that validate data

**Why**: Catch errors early, provide type hints

```python
from pydantic import BaseModel, Field

class SPEDItem(BaseModel):
    ncm: str = Field(..., pattern=r'^\d{8}$')  # Must be 8 digits
    total_value: Decimal

# Usage
item = SPEDItem(ncm="12345678", total_value=100.00)  # ✅ Valid
item = SPEDItem(ncm="123", total_value=100.00)       # ❌ Raises ValidationError
```

**Without Pydantic**:
```python
# Dictionary - no validation
item = {"ncm": "123", "total_value": "abc"}  # ✅ Accepts garbage
```

**With Pydantic**:
```python
# Automatic validation
item = SPEDItem(ncm="123", total_value="abc")  # ❌ Error caught immediately
```

### 3. Custom Exceptions

**What**: Your own error types

**Why**: Users can catch specific errors

```python
# exceptions.py
class SPEDError(Exception):
    """Base exception."""
    pass

class SPEDParseError(SPEDError):
    """Parsing failed."""
    pass

class SPEDFileNotFoundError(SPEDError):
    """File doesn't exist."""
    pass
```

**User's code**:
```python
from sped_parser import EFDContribuicoesParser, SPEDParseError

try:
    data = parser.parse_file("file.txt")
except SPEDParseError as e:
    print(f"Failed to parse: {e}")
except SPEDFileNotFoundError as e:
    print(f"File not found: {e}")
```

**Hierarchy**:
```
Exception (Python built-in)
└── SPEDError (your base)
    ├── SPEDParseError
    ├── SPEDFileNotFoundError
    ├── SPEDEncodingError
    └── SPEDValidationError
```

**Benefit**: Users can catch all your errors with `except SPEDError` or specific ones

### 4. Constants Module

**What**: A module with only data (no functions)

**Why**: Centralize configuration, avoid magic numbers

```python
# constants/layouts.py
ENCODING = 'latin-1'
DELIMITER = '|'

CST_PIS_COFINS = {
    "01": "Operação Tributável com Alíquota Básica",
    "02": "Operação Tributável com Alíquota Diferenciada",
    # ... 100+ entries
}
```

**Without constants**:
```python
# base.py
df = pd.read_csv(file, encoding='latin-1', delimiter='|')

# contribuicoes.py
df = pd.read_csv(file, encoding='latin-1', delimiter='|')  # Duplicated!

# fiscal.py
df = pd.read_csv(file, encoding='latin-1', delimiter='|')  # Duplicated!
```

**With constants**:
```python
from .constants import ENCODING, DELIMITER

df = pd.read_csv(file, encoding=ENCODING, delimiter=DELIMITER)
```

**Benefit**: Change once, affects everywhere

---

## The Publishing Process

### Overview: From Code to PyPI

```
Your Computer                           PyPI (Python Package Index)
│                                       │
├── sped-parser/                        │
│   ├── src/sped_parser/               │
│   └── pyproject.toml                 │
│                                       │
│   ┌─────────────────┐                │
│   │ 1. Build        │                │
│   │ python -m build │                │
│   └────────┬────────┘                │
│            │                          │
│            ▼                          │
│   ┌─────────────────┐                │
│   │ 2. Generates    │                │
│   │ dist/           │                │
│   │  ├── .whl       │                │
│   │  └── .tar.gz    │                │
│   └────────┬────────┘                │
│            │                          │
│            ▼                          │
│   ┌─────────────────┐                │
│   │ 3. Upload       │                │
│   │ twine upload    │ ──────────────→│
│   └─────────────────┘                │
│                                       │
│                                ┌──────▼──────┐
│                                │ sped-parser │
│                                │   v0.1.0    │
│                                └──────┬──────┘
│                                       │
User's Computer                         │
│                                       │
│   ┌─────────────────┐                │
│   │ 4. Install      │                │
│   │ pip install     │ ◀──────────────┘
│   └────────┬────────┘
│            │
│            ▼
│   site-packages/sped_parser/
```

### Step-by-Step Publishing

#### 1. Build Configuration (`pyproject.toml`)

This file tells Python **how to build** your library:

```toml
[build-system]
requires = ["hatchling"]        # What tool to use for building
build-backend = "hatchling.build"

[project]
name = "sped-parser"            # Package name on PyPI
version = "0.1.0"               # Version number
description = "Parse SPED files"
dependencies = [
    "pandas>=2.0.0",           # What your library needs
    "pydantic>=2.0.0",
]

[tool.hatch.build.targets.wheel]
packages = ["src/sped_parser"]  # What to include in the package
```

**Key sections**:
- `build-system`: How to build
- `project`: Metadata (name, version, description)
- `dependencies`: What your library needs
- `packages`: What to include

#### 2. Building

```bash
cd /path/to/sped-parser
pip install build
python -m build
```

**Output**:
```
dist/
├── sped_parser-0.1.0-py3-none-any.whl    # Wheel (fast install)
└── sped_parser-0.1.0.tar.gz              # Source distribution
```

**What are these?**

| File | Type | Contents |
|------|------|----------|
| `.whl` | Wheel | Pre-built, ready to install (ZIP format) |
| `.tar.gz` | Source | Source code that gets built during install |

**When to use each**:
- **Wheel**: Pure Python libraries (faster)
- **Source**: Libraries with C extensions (needs compilation)

Our library is pure Python, so `.whl` is preferred.

#### 3. Uploading to PyPI

```bash
pip install twine
twine upload dist/*
```

**What happens**:
1. Prompts for PyPI username/password
2. Uploads both files to https://pypi.org
3. Package is now available to everyone!

#### 4. Users Install

```bash
pip install sped-parser
```

**What happens**:
1. `pip` downloads `.whl` from PyPI
2. Extracts it to `site-packages/sped_parser/`
3. Package is now importable!

### Version Numbers (Semantic Versioning)

Format: `MAJOR.MINOR.PATCH`

```
0.1.0
│ │ │
│ │ └─ PATCH: Bug fixes (0.1.0 → 0.1.1)
│ └─── MINOR: New features, backwards compatible (0.1.0 → 0.2.0)
└───── MAJOR: Breaking changes (0.1.0 → 1.0.0)
```

**Examples**:
- `0.1.0` → `0.1.1`: Fixed a bug in `EFDFiscalParser`
- `0.1.0` → `0.2.0`: Added new `NFSeParser` class
- `0.1.0` → `1.0.0`: Changed `parse()` method signature (breaks existing code)

**Before 1.0.0**: Unstable, may have breaking changes
**After 1.0.0**: Stable, breaking changes only in major versions

---

## How Users Consume Your Library

### Installation Flow

```
User's Terminal
│
├─ pip install sped-parser
│
├─ PyPI downloads sped_parser-0.1.0-py3-none-any.whl
│
├─ Extracts to site-packages/
│  └── sped_parser/
│      ├── __init__.py
│      ├── base.py
│      ├── contribuicoes.py
│      ├── fiscal.py
│      ├── ecd.py
│      ├── schemas.py
│      ├── exceptions.py
│      └── constants/
│          ├── __init__.py
│          ├── cst.py
│          ├── cfop.py
│          ├── uf.py
│          └── layouts.py
│
└─ Installation complete!
```

### Import Flow

```python
# User's script.py
from sped_parser import EFDContribuicoesParser
```

**What happens internally**:

```
1. Python looks for 'sped_parser' in sys.path
   └─ Found in site-packages/sped_parser/

2. Runs site-packages/sped_parser/__init__.py
   └─ This file has: from .contribuicoes import EFDContribuicoesParser

3. Runs site-packages/sped_parser/contribuicoes.py
   └─ This file defines the EFDContribuicoesParser class

4. Returns EFDContribuicoesParser to user's script
```

### Dependency Resolution

**Your `pyproject.toml`**:
```toml
dependencies = [
    "pandas>=2.0.0",
    "pydantic>=2.0.0",
]
```

**When user installs**:
```bash
pip install sped-parser
```

**Pip automatically installs**:
```
Installing sped-parser-0.1.0
  - pandas-2.2.0 (dependency)
  - pydantic-2.5.0 (dependency)
  - numpy-1.26.0 (dependency of pandas)
  - ... (all transitive dependencies)
```

**Dependency tree**:
```
sped-parser
├── pandas>=2.0.0
│   ├── numpy>=1.23
│   ├── python-dateutil>=2.8
│   └── pytz>=2020
└── pydantic>=2.0.0
    ├── typing-extensions>=4.6
    └── annotated-types>=0.4
```

**Benefit**: User doesn't need to know what your library needs!

---

## Common Patterns

### Pattern 1: Factory Pattern

**What**: A function/class that creates other objects

**Where we use it**: Could be used for parser selection

```python
# Not implemented yet, but a good pattern for v0.2.0
class SPEDParserFactory:
    @staticmethod
    def create_parser(file_type: str):
        if file_type == "contribuicoes":
            return EFDContribuicoesParser()
        elif file_type == "fiscal":
            return EFDFiscalParser()
        elif file_type == "ecd":
            return ECDParser()
        else:
            raise ValueError(f"Unknown file type: {file_type}")

# User code
parser = SPEDParserFactory.create_parser("contribuicoes")
data = parser.parse_file("file.txt")
```

### Pattern 2: Layered API

**What**: Multiple levels of abstraction

**Where we use it**: Our three API levels

```python
# Level 1: High-level (typed, convenient)
sales_items = data.sales_items  # list[SPEDItem]
for item in sales_items:
    print(item.ncm, item.total_value)

# Level 2: Mid-level (flexible)
m100_records = data.get_register('M100')  # list[dict]
for record in m100_records:
    print(record['7'])

# Level 3: Low-level (full control)
df = data.raw_dataframe  # pd.DataFrame
custom = df[df['0'] == 'C197']
```

**Why**:
- Level 1: 80% of users (tax reform simulation)
- Level 2: 15% of users (custom analysis)
- Level 3: 5% of users (research, debugging)

### Pattern 3: Single Responsibility Principle

**What**: Each module does ONE thing

**How we apply it**:

| File | Responsibility |
|------|---------------|
| `base.py` | File reading, chunking, parent IDs |
| `contribuicoes.py` | Extract sales from Contribuições |
| `fiscal.py` | Extract purchases from Fiscal |
| `ecd.py` | Extract expenses from ECD |
| `schemas.py` | Data structures |
| `exceptions.py` | Error types |
| `constants/` | Configuration data |

**Benefits**:
- ✅ Easy to find code
- ✅ Easy to test
- ✅ Easy to modify
- ✅ Easy for new contributors

### Pattern 4: DRY (Don't Repeat Yourself)

**Bad** (repeated logic):
```python
# contribuicoes.py
df = pd.read_csv(file, encoding='latin-1', delimiter='|', ...)
# ... 50 lines of chunking logic

# fiscal.py
df = pd.read_csv(file, encoding='latin-1', delimiter='|', ...)
# ... 50 lines of chunking logic (DUPLICATED!)

# ecd.py
df = pd.read_csv(file, encoding='latin-1', delimiter='|', ...)
# ... 50 lines of chunking logic (DUPLICATED!)
```

**Good** (shared in base class):
```python
# base.py
class SPEDParser:
    def _read_file(self, content):
        # ... chunking logic (ONCE)

# contribuicoes.py
class EFDContribuicoesParser(SPEDParser):
    # Inherits _read_file, no duplication!

# fiscal.py, ecd.py same
```

---

## Summary: The Complete Flow

### 1. Development

```
Your Computer
│
├── Write code in src/sped_parser/
│   ├── __init__.py
│   ├── base.py
│   └── ...
│
├── Write tests in tests/
│
├── pip install -e .  (editable install)
│
└── Test locally
```

### 2. Publishing

```
├── Update version in pyproject.toml
├── Update CHANGELOG.md
├── python -m build
├── twine upload dist/*
└── Package is on PyPI!
```

### 3. User Consumption

```
User's Computer
│
├── pip install sped-parser
│   └── Downloads from PyPI
│   └── Installs to site-packages/
│
├── from sped_parser import EFDContribuicoesParser
│
└── parser.parse_file("myfile.txt")
```

### 4. The Magic Behind `import`

```
import sped_parser
│
├─ Python checks sys.path for 'sped_parser'
│  └─ Found in site-packages/sped_parser/
│
├─ Runs site-packages/sped_parser/__init__.py
│  └─ This imports from submodules
│      └─ contribuicoes.py, fiscal.py, ecd.py
│
└─ Returns the imported objects to your script
```

---

## Key Takeaways

### 1. A Library is Just Organized Code

It's not magic - it's Python files in a specific structure.

### 2. `__init__.py` is the Entry Point

It controls what users can import.

### 3. `pyproject.toml` is the Build Recipe

It tells Python how to package your code.

### 4. PyPI is Just a File Server

It stores `.whl` and `.tar.gz` files that pip downloads.

### 5. Users Don't See Your Source

They only get the installed package in `site-packages/`.

### 6. Good Structure = Happy Users

- ✅ Clear module names
- ✅ Logical grouping
- ✅ Consistent patterns
- ✅ Good documentation

---

## Next Steps for Learning

### Practice Exercise 1: Minimal Library

Create a tiny library to understand the flow:

```bash
mkdir my-first-lib
cd my-first-lib

# Create structure
mkdir -p src/my_first_lib
touch src/my_first_lib/__init__.py
touch pyproject.toml

# Write code
echo "def greet(name): return f'Hello, {name}!'" > src/my_first_lib/__init__.py

# Write pyproject.toml
cat > pyproject.toml << EOF
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-first-lib"
version = "0.1.0"

[tool.hatch.build.targets.wheel]
packages = ["src/my_first_lib"]
EOF

# Install locally
pip install -e .

# Test
python -c "from my_first_lib import greet; print(greet('World'))"
```

### Practice Exercise 2: Add a Submodule

```bash
# Add a new file
echo "def farewell(name): return f'Goodbye, {name}!'" > src/my_first_lib/goodbyes.py

# Update __init__.py
echo "from .goodbyes import farewell" >> src/my_first_lib/__init__.py

# Test
python -c "from my_first_lib import farewell; print(farewell('World'))"
```

### Read These

1. **Python Packaging Guide**: https://packaging.python.org
2. **Setuptools vs Hatchling**: https://hatch.pypa.io/latest/
3. **Real Python - Packaging**: https://realpython.com/python-application-layouts/

---

## Glossary

| Term | Definition |
|------|------------|
| **Package** | A directory with `__init__.py` |
| **Module** | A single `.py` file |
| **Distribution** | The `.whl` or `.tar.gz` file you upload |
| **Wheel** | A pre-built distribution (`.whl`) |
| **Source Distribution** | Source code that builds during install (`.tar.gz`) |
| **PyPI** | Python Package Index (https://pypi.org) |
| **site-packages** | Where pip installs packages |
| **Editable Install** | `pip install -e .` - links to source instead of copying |
| **Dependency** | Another package your package needs |
| **Transitive Dependency** | A dependency of your dependency |

---

## Congratulations!

You now understand:
- ✅ What a library is vs an application
- ✅ How Python's import system works
- ✅ How packages are structured
- ✅ How building and publishing works
- ✅ How users consume your library
- ✅ Common patterns and best practices

**You've built a real, production-ready library!** 🎉

Most developers never get this far. You're now equipped to:
- Build more libraries
- Contribute to open source
- Publish to PyPI
- Help others learn

Keep building! 🚀
