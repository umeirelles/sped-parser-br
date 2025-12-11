"""
Integration tests for SPED parsers with real anonymized SPED files.

These tests verify that Phase P0 improvements correctly extract:
- Tax rates (aliq_pis, aliq_cofins, aliq_icms)
- Tax bases (vl_bc_pis, vl_bc_cofins, vl_bc_icms)
- IPI values (for EFD Fiscal)
- Document references (document_number, document_key, document_date)
- Quantity and unit
- Credit classification (nat_bc_cred)
"""

import pytest
from pathlib import Path
from decimal import Decimal
from datetime import date

from sped_parser_br import EFDContribuicoesParser, EFDFiscalParser, ECDParser
from sped_parser_br.schemas import SPEDData, SPEDItem, SPEDExpense


# Test file paths
FIXTURES_DIR = Path(__file__).parent / "fixtures"
EFD_CONTRIB_FILE = FIXTURES_DIR / "efd-contribuicoes.txt"
EFD_FISCAL_FILE = FIXTURES_DIR / "efd-fiscal.txt"
ECD_FILE = FIXTURES_DIR / "ecd.txt"


class TestEFDContribuicoesIntegration:
    """Integration tests for EFD Contribuições parser with real files."""

    @pytest.fixture
    def parsed_data(self) -> SPEDData:
        """Parse EFD Contribuições file once for all tests."""
        parser = EFDContribuicoesParser()
        return parser.parse_file(str(EFD_CONTRIB_FILE))

    def test_file_parses_successfully(self, parsed_data):
        """Verify file parses without errors."""
        assert parsed_data is not None
        assert parsed_data.file_type == "contribuicoes"

    def test_header_extracted(self, parsed_data):
        """Verify header information is extracted."""
        header = parsed_data.header
        assert header.cnpj
        assert len(header.cnpj) == 14  # CNPJ is 14 digits
        assert header.company_name
        assert header.period_start
        assert header.period_end
        assert header.uf
        assert len(header.uf) == 2  # UF is 2 letters

    def test_sales_items_extracted(self, parsed_data):
        """Verify sales items are extracted."""
        assert len(parsed_data.sales_items) > 0
        assert len(parsed_data.purchase_items) == 0  # Contribuições is for sales only

    def test_ncm_preserved_with_leading_zeros(self, parsed_data):
        """Verify NCM codes are 8 digits with leading zeros preserved."""
        for item in parsed_data.sales_items[:10]:
            assert len(item.ncm) == 8
            assert item.ncm.isdigit()

    def test_tax_rates_extracted(self, parsed_data):
        """Verify tax rates (aliq_*) are extracted from C170/A170."""
        items_with_rates = [
            item for item in parsed_data.sales_items
            if item.aliq_pis is not None or item.aliq_cofins is not None
        ]
        assert len(items_with_rates) > 0, "Should have items with tax rates"

        # Check at least one item has valid rates
        for item in items_with_rates[:5]:
            if item.aliq_pis is not None:
                assert isinstance(item.aliq_pis, Decimal)
                assert item.aliq_pis >= 0
            if item.aliq_cofins is not None:
                assert isinstance(item.aliq_cofins, Decimal)
                assert item.aliq_cofins >= 0

    def test_tax_bases_extracted(self, parsed_data):
        """Verify tax bases (vl_bc_*) are extracted from C170/A170."""
        items_with_bases = [
            item for item in parsed_data.sales_items
            if item.vl_bc_pis is not None or item.vl_bc_cofins is not None
        ]
        assert len(items_with_bases) > 0, "Should have items with tax bases"

        # Check at least one item has valid bases
        for item in items_with_bases[:5]:
            if item.vl_bc_pis is not None:
                assert isinstance(item.vl_bc_pis, Decimal)
                assert item.vl_bc_pis >= 0
            if item.vl_bc_cofins is not None:
                assert isinstance(item.vl_bc_cofins, Decimal)
                assert item.vl_bc_cofins >= 0

    def test_quantity_and_unit_extracted(self, parsed_data):
        """Verify quantity and unit are extracted from C170."""
        items_with_qty = [
            item for item in parsed_data.sales_items
            if item.quantity is not None
        ]
        assert len(items_with_qty) > 0, "Should have items with quantity"

        for item in items_with_qty[:5]:
            assert isinstance(item.quantity, Decimal)
            assert item.quantity > 0
            # Unit may or may not be present

    def test_document_references_extracted(self, parsed_data):
        """Verify document references (NUM_DOC, CHV_NFE, DT_DOC) from parent C100/A100."""
        items_with_doc = [
            item for item in parsed_data.sales_items
            if item.document_number is not None or item.document_key is not None
        ]
        assert len(items_with_doc) > 0, "Should have items with document references"

        for item in items_with_doc[:5]:
            # At least one document field should be present
            assert item.document_number or item.document_key or item.document_date

    def test_nat_bc_cred_for_services(self, parsed_data):
        """Verify NAT_BC_CRED is extracted for service sales (A170)."""
        # Services typically have CFOP 5933 (hardcoded default in parser)
        # NAT_BC_CRED should be present in A170 items
        items_with_nat_bc = [
            item for item in parsed_data.sales_items
            if item.nat_bc_cred is not None
        ]
        # May or may not have services, so we just check if present, it's valid
        if len(items_with_nat_bc) > 0:
            for item in items_with_nat_bc[:5]:
                assert isinstance(item.nat_bc_cred, str)
                assert len(item.nat_bc_cred) == 2  # NAT_BC_CRED is 2 digits

    def test_operation_is_saida(self, parsed_data):
        """Verify all items are marked as saída (sales)."""
        for item in parsed_data.sales_items[:10]:
            assert item.operation == "saida"


class TestEFDFiscalIntegration:
    """Integration tests for EFD Fiscal parser with real files."""

    @pytest.fixture
    def parsed_data(self) -> SPEDData:
        """Parse EFD Fiscal file once for all tests."""
        parser = EFDFiscalParser()
        return parser.parse_file(str(EFD_FISCAL_FILE))

    def test_file_parses_successfully(self, parsed_data):
        """Verify file parses without errors."""
        assert parsed_data is not None
        assert parsed_data.file_type == "fiscal"

    def test_header_extracted(self, parsed_data):
        """Verify header information is extracted."""
        header = parsed_data.header
        assert header.cnpj
        assert len(header.cnpj) == 14
        assert header.company_name
        assert header.period_start
        assert header.period_end
        assert header.uf

    def test_purchase_items_extracted(self, parsed_data):
        """Verify purchase items are extracted."""
        assert len(parsed_data.purchase_items) > 0
        assert len(parsed_data.sales_items) == 0  # Fiscal is for purchases only

    def test_ncm_preserved(self, parsed_data):
        """Verify NCM codes are 8 digits."""
        for item in parsed_data.purchase_items[:10]:
            assert len(item.ncm) == 8
            assert item.ncm.isdigit()

    def test_tax_rates_extracted(self, parsed_data):
        """Verify tax rates are extracted from C170."""
        items_with_rates = [
            item for item in parsed_data.purchase_items
            if item.aliq_pis is not None or item.aliq_cofins is not None or item.aliq_icms is not None
        ]
        assert len(items_with_rates) > 0, "Should have items with tax rates"

    def test_tax_bases_extracted(self, parsed_data):
        """Verify tax bases are extracted from C170."""
        items_with_bases = [
            item for item in parsed_data.purchase_items
            if item.vl_bc_pis is not None or item.vl_bc_cofins is not None or item.vl_bc_icms is not None
        ]
        assert len(items_with_bases) > 0, "Should have items with tax bases"

    def test_ipi_value_extracted(self, parsed_data):
        """Verify IPI value is extracted from C170 (EFD Fiscal specific)."""
        items_with_ipi = [
            item for item in parsed_data.purchase_items
            if item.ipi_value is not None
        ]
        # May or may not have IPI, but if present should be valid
        if len(items_with_ipi) > 0:
            for item in items_with_ipi[:5]:
                assert isinstance(item.ipi_value, Decimal)
                assert item.ipi_value >= 0

    def test_document_references_extracted(self, parsed_data):
        """Verify document references from parent C100."""
        items_with_doc = [
            item for item in parsed_data.purchase_items
            if item.document_number is not None or item.document_key is not None
        ]
        assert len(items_with_doc) > 0, "Should have items with document references"

    def test_participant_uf_extracted(self, parsed_data):
        """Verify participant UF is extracted from 0150 records."""
        items_with_uf = [
            item for item in parsed_data.purchase_items
            if item.participant_uf is not None
        ]
        assert len(items_with_uf) > 0, "Should have items with participant UF"

        for item in items_with_uf[:5]:
            assert len(item.participant_uf) == 2
            assert item.participant_uf.isupper()

    def test_quantity_extracted(self, parsed_data):
        """Verify quantity is extracted from C170."""
        items_with_qty = [
            item for item in parsed_data.purchase_items
            if item.quantity is not None
        ]
        assert len(items_with_qty) > 0, "Should have items with quantity"

    def test_operation_is_entrada(self, parsed_data):
        """Verify all items are marked as entrada (purchases)."""
        for item in parsed_data.purchase_items[:10]:
            assert item.operation == "entrada"


class TestECDIntegration:
    """Integration tests for ECD parser with real files."""

    @pytest.fixture
    def parsed_data(self) -> SPEDData:
        """Parse ECD file once for all tests."""
        parser = ECDParser()
        return parser.parse_file(str(ECD_FILE))

    def test_file_parses_successfully(self, parsed_data):
        """Verify file parses without errors."""
        assert parsed_data is not None
        assert parsed_data.file_type == "ecd"

    def test_header_extracted(self, parsed_data):
        """Verify header information is extracted."""
        header = parsed_data.header
        assert header.cnpj
        assert len(header.cnpj) == 14
        assert header.company_name
        assert header.period_start
        assert header.period_end

    def test_expenses_extracted(self, parsed_data):
        """Verify expenses are extracted from I355."""
        assert len(parsed_data.expenses) > 0

    def test_expense_fields(self, parsed_data):
        """Verify expense fields are valid."""
        for expense in parsed_data.expenses[:10]:
            assert expense.account_code
            assert isinstance(expense.value, Decimal)
            assert isinstance(expense.is_debit, bool)


class TestLayeredAPIAccess:
    """Test that layered API (high/mid/low) works with real files."""

    def test_high_level_api(self):
        """Test Level 1: High-level typed business data."""
        parser = EFDContribuicoesParser()
        data = parser.parse_file(str(EFD_CONTRIB_FILE))

        # Can access typed data
        assert len(data.sales_items) > 0
        item = data.sales_items[0]
        assert isinstance(item, SPEDItem)
        assert item.ncm
        assert item.cfop
        assert item.total_value

    def test_mid_level_api(self):
        """Test Level 2: get_register() for any register."""
        parser = EFDContribuicoesParser()
        data = parser.parse_file(str(EFD_CONTRIB_FILE))

        # Can access any register
        c100 = data.get_register('C100')
        assert len(c100) > 0
        assert isinstance(c100, list)
        assert isinstance(c100[0], dict)

    def test_low_level_api(self):
        """Test Level 3: raw_dataframe for power users."""
        parser = EFDContribuicoesParser()
        data = parser.parse_file(str(EFD_CONTRIB_FILE))

        # Can access raw DataFrame
        df = data.raw_dataframe
        assert df is not None
        assert len(df) > 0
        assert '0' in df.columns  # Register code column


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
