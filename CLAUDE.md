# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is "Belittle V2" - a Flask-based enterprise management application that handles company data and generates administrative documents. The application follows an MVC architecture and manages a SQLite database of companies with their associated business sectors, contact information, and financial data.

## Development Environment Setup

### Database Initialization
```bash
python utils/init_db.py
```

### Running the Application
```bash
# Development mode
FLASK_ENV=development python run.py

# Production mode  
python run.py
```

The application runs on `http://localhost:5002` by default (configurable via PORT environment variable).

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Architecture

### MVC Structure
- **Models** (`models/`): Database operations and business logic
  - `entreprise.py`: Enterprise CRUD operations, search functionality, financial data
  - `document.py`: Document generation logic for DC1, DC2 forms and enterprise data formatting
  - `projet.py`: Project management, lots creation and assignment, enterprise-lot relationships
- **Views** (`templates/`): Jinja2 HTML templates
  - Main templates: `base.html`, `index.html`, enterprise management templates
  - `document/`: Project management templates, document generation forms, lot assignment interfaces
- **Controllers** (`routes/`): Flask blueprints handling HTTP requests
  - `main.py`: Homepage and search functionality
  - `entreprise.py`: Company management endpoints  
  - `document.py`: Document generation endpoints and complete project management workflow

### Database Schema
SQLite database with tables: 
- Core: `entreprise`, `projets`, `lots`, `lot_entreprises`, `montants_lot_entreprises`
- Reference: `villes`, `type_entreprise`, `corps_metier`, `code_postal`, `cedex`, `entreprise_corps_metier`, `chiffre_affaires`

### Key Configuration
- Database: SQLite file at `data/entreprise.db`
- Configuration: `config.py` with environment variable support
- Document templates: `.docx` files in `templates/document_templates/`

## Development Workflows

### Adding New Features
1. Models: Add database operations in `models/`
2. Routes: Create endpoints in appropriate `routes/` blueprint
3. Templates: Add/modify HTML templates in `templates/`
4. Test with both development and production modes

### Document Generation
- Uses `docxtpl` and `docxcompose` libraries with Word templates
- Templates located in `templates/document_templates/`
- Document data formatting functions in `models/document.py`
- Supports multiple document types: DC1, DC2, ATTRI1, Ordre de Service, EXE10, EXE1T, DC4

### Project Management
- Complete project lifecycle management with MOA/MOE designation
- Lot creation and enterprise assignment with financial tracking
- Mandataire MOE designation for project leadership
- Historical tracking of amount changes with `montants_lot_entreprises` table

### Database Utilities
- `utils/init_db.py`: Initialize database schema
- `utils/import_excel.py`: Import data from Excel files
- `utils/diagnose_ca.py`: Diagnose revenue data issues

## Key Components

### Enterprise Search System
- Advanced filtering by business sector (`corps_metier`) and company type (`type_entreprise`)
- Text-based search across multiple fields
- Results displayed with complete address information

### Document Generation System  
- DC1 form: Company designation with co-contractor information
- DC2 form: Company declaration with financial data
- ATTRI1, Ordre de Service, EXE10, EXE1T, DC4: Project-specific administrative documents
- Project-based document generation with lot and enterprise-specific data
- Dynamic data population from database records with project context

### Financial Data Management
- Annual revenue tracking (`chiffre_affaires` table)
- Project lot amount tracking (`montants_lot_entreprises` table)
- Historical data with timestamps for financial changes
- Integration with document generation and project management

## Important Notes

- The application uses Waitress WSGI server for production deployment (port 5002)
- Database connection management via `database.py` with proper connection closing
- Blueprint-based route organization for modular development
- Responsive design with Bootstrap-based templates
- Document templates are Word files (.docx) processed with docxtpl and docxcompose libraries
- Docker and Docker Compose support for containerized deployment
- Complete project management workflow integrated with document generation