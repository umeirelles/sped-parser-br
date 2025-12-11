# FISCALIA Integration Guide - sped-parser v0.2.0

## Quick Start: How to Use sped-parser in FISCALIA

### Step 1: Install the Library

Since sped-parser is on GitHub (not PyPI yet), you have two options:

#### Option A: Install from GitHub (Recommended)
```bash
# In FISCALIA project directory
pip install git+https://github.com/umeirelles/sped-parser.git@main
```

Add to `requirements.txt`:
```
git+https://github.com/umeirelles/sped-parser.git@main
```

#### Option B: Local Development Install
```bash
# If you want to develop both projects simultaneously
cd ~/projects/sped-parser
pip install -e .

# Then in FISCALIA, it will use the local version
```

### Step 2: Import in FISCALIA

```python
# In your FISCALIA code (e.g., app/services/sped_service.py)
from sped_parser_br import (
    EFDContribuicoesParser,
    EFDFiscalParser,
    ECDParser,
    SPEDItem,
    SPEDExpense,
)
```

### Step 3: Parse SPED Files

```python
def process_user_sped_files(contrib_file, fiscal_file):
    """
    Process uploaded SPED files and extract tax data for reform simulation.

    Args:
        contrib_file: Uploaded EFD Contribuições file (sales/débitos)
        fiscal_file: Uploaded EFD Fiscal file (purchases/créditos)

    Returns:
        dict with sales_items and purchase_items
    """
    # Parse sales (débitos)
    contrib_parser = EFDContribuicoesParser()
    sales_data = contrib_parser.parse(contrib_file.read())  # from bytes
    # OR: sales_data = contrib_parser.parse_file("/path/to/file.txt")

    # Parse purchases (créditos)
    fiscal_parser = EFDFiscalParser()
    purchase_data = fiscal_parser.parse(fiscal_file.read())

    return {
        "company": {
            "cnpj": sales_data.header.cnpj,
            "name": sales_data.header.company_name,
            "period_start": sales_data.header.period_start,
            "period_end": sales_data.header.period_end,
            "uf": sales_data.header.uf,
        },
        "sales_items": sales_data.sales_items,      # List[SPEDItem]
        "purchase_items": purchase_data.purchase_items,  # List[SPEDItem]
    }
```

### Step 4: Use the Data for Tax Reform Simulation

Here's how to access all the Phase P0 fields you need:

```python
def simulate_tax_reform(sales_items, purchase_items):
    """
    Simulate tax reform impact using sped-parser data.

    This is where FISCALIA's tax calculation logic goes.
    """
    from fiscalia.calc import TaxCalculator  # Your existing calculator

    calculator = TaxCalculator()

    # ─────────────────────────────────────────────────────────────
    # SALES (Débitos) - Process each sales item
    # ─────────────────────────────────────────────────────────────
    for item in sales_items:
        # ✅ All these fields are now available from sped-parser:

        # Basic identification
        ncm = item.ncm                    # str: "85439090" (8 digits)
        cfop = item.cfop                  # str: "5124" (4 digits)

        # Values
        total_value = item.total_value    # Decimal: total item value
        quantity = item.quantity          # Optional[Decimal]
        unit = item.unit                  # Optional[str]: "PC", "KG", etc.

        # Current system taxes
        pis_value = item.pis_value        # Decimal: current PIS paid
        cofins_value = item.cofins_value  # Decimal: current COFINS paid

        # Tax rates (critical for LC 214 recalculation)
        aliq_pis = item.aliq_pis          # Optional[Decimal]: PIS rate %
        aliq_cofins = item.aliq_cofins    # Optional[Decimal]: COFINS rate %

        # Tax bases (critical for IBS/CBS calculation)
        vl_bc_pis = item.vl_bc_pis        # Optional[Decimal]: PIS tax base
        vl_bc_cofins = item.vl_bc_cofins  # Optional[Decimal]: COFINS tax base

        # Credit classification (critical for LC 214)
        nat_bc_cred = item.nat_bc_cred    # Optional[str]: "01", "02", etc.

        # Document reference (for audit trail)
        doc_number = item.document_number # Optional[str]: invoice number
        doc_key = item.document_key       # Optional[str]: NFe access key
        doc_date = item.document_date     # Optional[date]: invoice date

        # Calculate new system (IBS/CBS)
        new_tax = calculator.calcular_ibs_cbs(
            base=total_value,
            ano=2029,
            ncm=ncm,
            # Use the extracted fields for accurate simulation
        )

        # Compare old vs new
        old_tax = pis_value + cofins_value
        impact = new_tax - old_tax

        print(f"NCM {ncm}: Old={old_tax}, New={new_tax}, Impact={impact}")

    # ─────────────────────────────────────────────────────────────
    # PURCHASES (Créditos) - Process each purchase item
    # ─────────────────────────────────────────────────────────────
    for item in purchase_items:
        # ✅ Additional fields for purchases:

        # All sales fields PLUS:
        ipi_value = item.ipi_value        # Optional[Decimal]: IPI value
        aliq_icms = item.aliq_icms        # Optional[Decimal]: ICMS rate %
        vl_bc_icms = item.vl_bc_icms      # Optional[Decimal]: ICMS tax base
        participant_uf = item.participant_uf  # Optional[str]: "AM", "SP", etc.

        # Calculate credit recalculation (LC 214)
        # This is critical for tax reform simulation
        old_credit = item.pis_value + item.cofins_value
        new_credit = calculator.recalculate_credit_lc214(
            old_pis=item.pis_value,
            old_cofins=item.cofins_value,
            nat_bc_cred=item.nat_bc_cred,  # Nature of credit base
            aliq_pis=item.aliq_pis,
            aliq_cofins=item.aliq_cofins,
        )

        credit_impact = new_credit - old_credit
        print(f"Purchase NCM {item.ncm}: Credit impact={credit_impact}")
```

### Step 5: Example FISCALIA View/Route

```python
# In app/routes/sped_routes.py or similar

from flask import request, jsonify
from sped_parser_br import EFDContribuicoesParser, EFDFiscalParser

@app.route('/api/upload-sped', methods=['POST'])
def upload_sped():
    """
    Upload SPED files and return tax reform simulation.
    """
    contrib_file = request.files.get('efd_contribuicoes')
    fiscal_file = request.files.get('efd_fiscal')

    if not contrib_file or not fiscal_file:
        return jsonify({"error": "Both files required"}), 400

    try:
        # Parse files
        contrib_parser = EFDContribuicoesParser()
        fiscal_parser = EFDFiscalParser()

        sales_data = contrib_parser.parse(contrib_file.read())
        purchase_data = fiscal_parser.parse(fiscal_file.read())

        # Run simulation
        results = simulate_tax_reform(
            sales_data.sales_items,
            purchase_data.purchase_items
        )

        return jsonify({
            "success": True,
            "company": {
                "cnpj": sales_data.header.cnpj,
                "name": sales_data.header.company_name,
                "period": f"{sales_data.header.period_start} to {sales_data.header.period_end}",
            },
            "summary": {
                "sales_items": len(sales_data.sales_items),
                "purchase_items": len(purchase_data.purchase_items),
                "total_impact": results["total_impact"],
            },
            "details": results["details"],
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

## Real Example with Your Test Data

Based on the actual SPED files you provided, here's what you'll get:

```python
# Parse your test file
parser = EFDContribuicoesParser()
data = parser.parse_file("tests/fixtures/efd-contribuicoes.txt")

# Company info
print(f"Company: {data.header.company_name}")
# Output: "TUTIPLAST INDUSTRIA E COMERCIO LTDA - MATRIZ"

print(f"CNPJ: {data.header.cnpj}")
# Output: "04616842000160"

print(f"Period: {data.header.period_start} to {data.header.period_end}")
# Output: "2025-01-01 to 2025-01-31"

# Sales items
print(f"Total sales items: {len(data.sales_items)}")
# Output: 14911

# First item example
item = data.sales_items[0]
print(f"""
NCM: {item.ncm}                    # "85439090"
CFOP: {item.cfop}                  # "5124"
Total: R$ {item.total_value}       # 6914.2
Quantity: {item.quantity} {item.unit}  # 3820 PC
PIS Rate: {item.aliq_pis}%         # 0%
Document: {item.document_number}   # "735902"
""")
```

## Layered API Access

sped-parser provides 3 levels of access:

### Level 1: High-Level (Typed Business Data)
```python
# This is what you'll use 90% of the time
data = parser.parse_file("contrib.txt")
for item in data.sales_items:  # Type: List[SPEDItem]
    print(item.ncm, item.cfop, item.total_value)
```

### Level 2: Mid-Level (Any Register)
```python
# If you need access to other registers not in high-level API
data = parser.parse_file("contrib.txt")

# Get C100 invoice headers
c100_invoices = data.get_register('C100')
for invoice in c100_invoices:
    print(invoice['NUM_DOC'], invoice['DT_DOC'])

# Get M100 PIS credits
m100_credits = data.get_register('M100')
for credit in m100_credits:
    print(credit['COD_CRED'], credit['VL_CRED'])
```

### Level 3: Low-Level (Raw DataFrame)
```python
# For power users who want to do custom analysis
data = parser.parse_file("contrib.txt")
df = data.raw_dataframe

# You now have the full pandas DataFrame
print(df.columns)  # ['id', 'id_pai', '0', '1', '2', ...]
print(df[df['0'] == 'C170'].head())  # All C170 records

# Do custom filtering, aggregation, etc.
```

## Common Use Cases in FISCALIA

### Use Case 1: Calculate Total Tax Impact by NCM
```python
from decimal import Decimal
from collections import defaultdict

def tax_impact_by_ncm(sales_items):
    """Group tax impact by NCM code."""
    impact_by_ncm = defaultdict(lambda: {"count": 0, "old_tax": Decimal(0), "new_tax": Decimal(0)})

    for item in sales_items:
        old_tax = item.pis_value + item.cofins_value
        # Calculate new tax based on your logic
        new_tax = calculate_new_tax(item)

        impact_by_ncm[item.ncm]["count"] += 1
        impact_by_ncm[item.ncm]["old_tax"] += old_tax
        impact_by_ncm[item.ncm]["new_tax"] += new_tax

    return impact_by_ncm
```

### Use Case 2: Identify Items with Credit Recalculation
```python
def items_with_credit_recalc(sales_items):
    """Find items that have NAT_BC_CRED (service credits)."""
    return [
        item for item in sales_items
        if item.nat_bc_cred is not None
    ]

# These are critical for LC 214 credit recalculation
service_items = items_with_credit_recalc(data.sales_items)
print(f"Found {len(service_items)} service items with credit classification")
```

### Use Case 3: Export to Database
```python
def save_to_database(sales_items):
    """Save parsed items to FISCALIA database."""
    from app.models import SPEDSalesItem  # Your SQLAlchemy model

    for item in sales_items:
        db_item = SPEDSalesItem(
            ncm=item.ncm,
            cfop=item.cfop,
            total_value=float(item.total_value),
            quantity=float(item.quantity) if item.quantity else None,
            unit=item.unit,
            aliq_pis=float(item.aliq_pis) if item.aliq_pis else None,
            aliq_cofins=float(item.aliq_cofins) if item.aliq_cofins else None,
            vl_bc_pis=float(item.vl_bc_pis) if item.vl_bc_pis else None,
            vl_bc_cofins=float(item.vl_bc_cofins) if item.vl_bc_cofins else None,
            nat_bc_cred=item.nat_bc_cred,
            document_number=item.document_number,
        )
        db.session.add(db_item)

    db.session.commit()
```

## Error Handling

```python
from sped_parser_br import (
    SPEDParseError,
    SPEDEncodingError,
    SPEDFileNotFoundError,
    SPEDEmptyFileError,
)

def safe_parse_sped(file_content):
    """Parse SPED file with proper error handling."""
    try:
        parser = EFDContribuicoesParser()
        return parser.parse(file_content)

    except SPEDFileNotFoundError:
        return {"error": "File not found"}

    except SPEDEncodingError:
        return {"error": "Invalid file encoding. Must be ISO-8859-1"}

    except SPEDEmptyFileError:
        return {"error": "File is empty or has no valid records"}

    except SPEDParseError as e:
        return {"error": f"Failed to parse SPED file: {e}"}

    except Exception as e:
        return {"error": f"Unexpected error: {e}"}
```

## Testing in FISCALIA

```python
# In tests/test_sped_integration.py

def test_sped_parser_integration():
    """Test that sped-parser works in FISCALIA."""
    from sped_parser_br import EFDContribuicoesParser

    parser = EFDContribuicoesParser()

    # Use the test fixtures from sped-parser
    data = parser.parse_file("path/to/test/efd-contribuicoes.txt")

    assert len(data.sales_items) > 0
    assert data.header.cnpj

    # Verify fields needed for FISCALIA
    item = data.sales_items[0]
    assert item.ncm
    assert item.cfop
    assert item.total_value > 0
```

## Next Steps

1. **Install sped-parser** in FISCALIA:
   ```bash
   cd ~/Desktop/fiscalia-mvp
   pip install git+https://github.com/umeirelles/sped-parser.git@main
   ```

2. **Create SPED upload route** (see example above)

3. **Integrate with tax calculator**:
   - Use `item.aliq_pis`, `item.aliq_cofins` for rate-based calculations
   - Use `item.vl_bc_pis`, `item.vl_bc_cofins` for base-based calculations
   - Use `item.nat_bc_cred` for LC 214 credit classification

4. **Test with real data**:
   - Upload the test SPED files from `arquivos_teste/`
   - Verify all fields are extracted correctly
   - Run tax reform simulation

5. **Optional: Publish to PyPI** (for easier distribution):
   ```bash
   # Later, when ready for public release
   cd ~/projects/sped-parser
   python -m build
   twine upload dist/*
   ```

## Questions?

If you need help with:
- Database integration → Let me know your DB schema
- Tax calculation logic → Show me your current calculator
- Frontend integration → Show me your upload component
- Performance optimization → We can add chunking/streaming

The library is ready to use in FISCALIA right now! 🎯
