# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-12-08

### Added - FISCALIA Integration (Phase P0)
**Critical fields for tax reform simulation:**
- Tax rates to SPEDItem: `aliq_pis`, `aliq_cofins`, `aliq_icms`
- Tax bases to SPEDItem: `vl_bc_pis`, `vl_bc_cofins`, `vl_bc_icms`
- Quantity and unit fields: `quantity`, `unit`
- IPI value for EFD Fiscal: `ipi_value`
- Document references: `document_number`, `document_key`, `document_date`
- Credit classification: `nat_bc_cred` (critical for LC 214)

**New constants module:**
- `IND_OPER` - Operation indicator (entrada/saída)
- `COD_SIT` - Document situation codes
- `NAT_BC_CRED` - Nature of credit base (16 codes for LC 214)

### Changed
- EFD Fiscal parser now extracts tax rates, bases, IPI, and document info from C170 and parent C100
- EFD Contribuições parser now extracts tax rates, bases, and document info from C170/A170 and parent records
- A170 service parser now extracts `NAT_BC_CRED` for credit classification

### Fixed
- Document references now properly linked from parent C100/A100 records
- **Critical**: SPED file parsing with leading delimiter (files start with `|`)
- **Critical**: Participant UF extraction using IBGE code mapping (13→AM, 35→SP, etc.)

## [0.1.0] - 2025-12-08

### Added
- First alpha release
- EFD Contribuições parser
- EFD Fiscal parser
- ECD parser
- Layered API (high-level, mid-level, low-level)
- Pydantic schemas for type safety
- Complete SPED constants (CST, CFOP, layouts)
- Basic parsing functionality for all three SPED file types
