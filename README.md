# sped-parser

[![PyPI version](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://pypi.org/project/sped-parser/)
[![Python versions](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://pypi.org/project/sped-parser/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/umeirelles/sped-parser/workflows/Tests/badge.svg)](https://github.com/umeirelles/sped-parser/actions)

Python library for parsing Brazilian SPED files (Sistema Público de Escrituração Digital).

[Installation](#installation) · [Quick Start](#quick-start) · [Documentation](#documentation) · [Contributing](#contributing)

## Features

- Parse **EFD Contribuições** (PIS/COFINS) files
- Parse **EFD Fiscal** (ICMS/IPI) files
- Parse **ECD** (Escrituração Contábil Digital) files
- **Layered API** for flexible access:
  - High-level: Typed business data (Pydantic models)
  - Mid-level: Any register as dict
  - Low-level: Raw pandas DataFrame
- Type-safe with Pydantic validation
- Production-ready error handling

## Installation

```bash
pip install sped-parser
```

## Quick Start

```python
from sped_parser import EFDContribuicoesParser, EFDFiscalParser, ECDParser

# Parse EFD Contribuições (for sales data)
parser = EFDContribuicoesParser()
data = parser.parse_file("efd_contribuicoes_2024.txt")

# High-level API: Get typed business data
print(f"Company: {data.header.company_name}")
print(f"Period: {data.header.period_start}")
print(f"Sales items: {len(data.sales_items)}")

for item in data.sales_items[:5]:
    print(f"  NCM {item.ncm}: R$ {item.total_value}")

# Mid-level API: Access any register
m100_records = data.get_register('M100')
c100_records = data.get_register('C100')

# Low-level API: Raw DataFrame
df = data.raw_dataframe
custom_analysis = df[df['0'] == 'C197']
```

## Supported File Types

| File Type | Parser | Use For |
|-----------|--------|---------|
| **EFD Contribuições** | `EFDContribuicoesParser` | Sales data (PIS/COFINS débitos) |
| **EFD Fiscal** | `EFDFiscalParser` | Purchase data (ICMS/IPI créditos) |
| **ECD** | `ECDParser` | Expense data (contabilidade) |

## Layered API Design

The library provides three levels of access to serve different use cases:

### Level 1: High-Level (Business Data)

Ready-to-use business data with Pydantic validation:

```python
data = parser.parse_file("file.txt")

# Typed models
header: SPEDHeader = data.header
sales: list[SPEDItem] = data.sales_items
purchases: list[SPEDItem] = data.purchase_items
expenses: list[SPEDExpense] = data.expenses
```

### Level 2: Mid-Level (Any Register)

Access any SPED register as a list of dictionaries:

```python
# Get any register by code
m100 = data.get_register('M100')
c100 = data.get_register('C100')
d200 = data.get_register('D200')
e110 = data.get_register('E110')
```

### Level 3: Low-Level (Raw DataFrame)

Full access to the raw pandas DataFrame:

```python
# Get raw DataFrame
df = data.raw_dataframe

# Custom filtering and analysis
custom = df[df['0'] == 'C197']
grouped = df.groupby('0').size()
```

## Examples

### Tax Reform Impact Simulation

```python
from sped_parser import EFDContribuicoesParser, EFDFiscalParser, ECDParser

# Load all three file types
contrib_parser = EFDContribuicoesParser()
fiscal_parser = EFDFiscalParser()
ecd_parser = ECDParser()

sales_data = contrib_parser.parse_file("efd_contrib.txt")
purchase_data = fiscal_parser.parse_file("efd_fiscal.txt")
expense_data = ecd_parser.parse_file("ecd.txt")

# Calculate débitos (from sales)
total_sales = sum(item.total_value for item in sales_data.sales_items)

# Calculate créditos (from purchases and expenses)
total_purchases = sum(item.total_value for item in purchase_data.purchase_items)
total_expenses = sum(exp.value for exp in expense_data.expenses)

print(f"Sales: R$ {total_sales:,.2f}")
print(f"Purchases: R$ {total_purchases:,.2f}")
print(f"Expenses: R$ {total_expenses:,.2f}")
```

### Custom Register Analysis

```python
parser = EFDContribuicoesParser()
data = parser.parse_file("efd_contrib.txt")

# Get M blocks (current PIS/COFINS totals)
m100 = data.get_register('M100')  # Credits
m200 = data.get_register('M200')  # Debits

# Get C blocks (operations detail)
c100 = data.get_register('C100')  # Invoice headers
c170 = data.get_register('C170')  # Invoice items

# Raw DataFrame for complex queries
df = data.raw_dataframe
high_value_items = df[(df['0'] == 'C170') & (df['7'].astype(float) > 10000)]
```

## Documentation

### SPED File Types

**EFD Contribuições (PIS/COFINS)**
- Records: 0000 (header), 0200 (products), C100/C170 (goods), A100/A170 (services), M blocks (totals)
- Use for: Sales data for tax reform simulations

**EFD Fiscal (ICMS/IPI)**
- Records: 0000 (header), 0150 (participants), 0200 (products), C170 (items), E110 (ICMS totals)
- Use for: Purchase data (ALL incoming invoices)

**ECD (Contábil Digital)**
- Records: 0000 (header), I050/I051 (chart of accounts), I355 (P&L balances)
- Use for: Expense data (complete accounting records)

### Business Rules

1. **C170 Obrigatoriedade**:
   - EFD Contribuições: C170 required for BOTH sales and purchases
   - EFD Fiscal: C170 required ONLY for purchases (entradas)

2. **Data Source Priority**:
   - Sales → Use EFD Contribuições C170 saídas
   - Purchases → Use EFD Fiscal C170 (NOT Contribuições)
   - Expenses → Use ECD I355

## Development

```bash
# Clone the repository
git clone https://github.com/fiscalia/sped-parser.git
cd sped-parser

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check src/

# Format code
black src/
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- [Official SPED Portal](http://sped.rfb.gov.br/)
- [EFD Contribuições Guide](http://sped.rfb.gov.br/pasta/show/1989)
- [EFD Fiscal Guide](http://sped.rfb.gov.br/pasta/show/1644)
