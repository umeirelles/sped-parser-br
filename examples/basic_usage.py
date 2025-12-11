"""
Example usage of sped-parser-br library.

This script demonstrates how to use the three parsers and access data
through the layered API.
"""

import sys
from pathlib import Path

# Add parent/src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from sped_parser_br import EFDContribuicoesParser, EFDFiscalParser, ECDParser


def example_contribuicoes():
    """Example: Parse EFD Contribuições for sales data."""
    print("\n" + "="*60)
    print("EFD CONTRIBUIÇÕES (Sales Data)")
    print("="*60)

    parser = EFDContribuicoesParser()

    # Replace with your actual file path
    # data = parser.parse_file("efd_contribuicoes_2024.txt")

    # For demonstration:
    print("Usage:")
    print("  data = parser.parse_file('efd_contribuicoes_2024.txt')")
    print()
    print("Level 1 - High-level API (typed business data):")
    print("  data.header.company_name")
    print("  data.header.cnpj")
    print("  data.sales_items[0].ncm")
    print("  data.sales_items[0].total_value")
    print()
    print("Level 2 - Mid-level API (any register):")
    print("  m100 = data.get_register('M100')")
    print("  c100 = data.get_register('C100')")
    print()
    print("Level 3 - Low-level API (raw DataFrame):")
    print("  df = data.raw_dataframe")
    print("  custom = df[df['0'] == 'C197']")


def example_fiscal():
    """Example: Parse EFD Fiscal for purchase data."""
    print("\n" + "="*60)
    print("EFD FISCAL (Purchase Data)")
    print("="*60)

    parser = EFDFiscalParser()

    print("Usage:")
    print("  data = parser.parse_file('efd_fiscal_2024.txt')")
    print()
    print("Access purchase data:")
    print("  for item in data.purchase_items:")
    print("      print(f'NCM {item.ncm}: R$ {item.total_value}')")
    print("      print(f'  Supplier UF: {item.participant_uf}')")
    print("      print(f'  ICMS: R$ {item.icms_value}')")


def example_ecd():
    """Example: Parse ECD for expense data."""
    print("\n" + "="*60)
    print("ECD (Expense Data)")
    print("="*60)

    parser = ECDParser()

    print("Usage:")
    print("  data = parser.parse_file('ecd_2024.txt')")
    print()
    print("Access expense data:")
    print("  for expense in data.expenses:")
    print("      print(f'Account {expense.account_code}: R$ {expense.value}')")
    print("      print(f'  Description: {expense.account_description}')")
    print("      print(f'  Type: {'Debit' if expense.is_debit else 'Credit'}')")


def example_tax_reform_simulation():
    """Example: Tax reform impact simulation."""
    print("\n" + "="*60)
    print("TAX REFORM SIMULATION")
    print("="*60)

    print("""
# 1. Parse all three file types
contrib_parser = EFDContribuicoesParser()
fiscal_parser = EFDFiscalParser()
ecd_parser = ECDParser()

sales_data = contrib_parser.parse_file("efd_contrib.txt")
purchase_data = fiscal_parser.parse_file("efd_fiscal.txt")
expense_data = ecd_parser.parse_file("ecd.txt")

# 2. Calculate débitos (from sales)
total_sales = sum(item.total_value for item in sales_data.sales_items)

# 3. Calculate créditos (from purchases and expenses)
total_purchases = sum(item.total_value for item in purchase_data.purchase_items)
total_expenses = sum(exp.value for exp in expense_data.expenses if exp.is_debit)

# 4. Apply IBS/CBS/IS rates (use Fiscalia calc engine)
# This would integrate with Fiscalia's tax calculation module
from fiscalia.calc.engine import TaxCalculator

calculator = TaxCalculator()
ibs_total = calculator.calculate_ibs(sales_data.sales_items, purchase_data.purchase_items)
cbs_total = calculator.calculate_cbs(sales_data.sales_items, purchase_data.purchase_items)

print(f"Current (PIS/COFINS): R$ {total_sales * 0.0925:,.2f}")
print(f"Projected (IBS/CBS): R$ {ibs_total + cbs_total:,.2f}")
print(f"Impact: R$ {(ibs_total + cbs_total) - (total_sales * 0.0925):,.2f}")
    """)


if __name__ == "__main__":
    example_contribuicoes()
    example_fiscal()
    example_ecd()
    example_tax_reform_simulation()

    print("\n" + "="*60)
    print("For more information, see README.md")
    print("="*60)
