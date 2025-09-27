# FedRAMP Control Extraction System

## Overview

The FedRAMP Control Extraction System is the first step in the comprehensive FedRAMP compliance automation platform. It extracts, normalizes, and classifies FedRAMP Low baseline control requirements from official templates, providing the foundation for automated compliance validation.

## Architecture

### Core Components

1. **FedRAMPExtractor** (`fedramp_extractor.py`)
   - Main extraction engine
   - Database management
   - Control classification and prioritization
   - Statistics and reporting

2. **FedRAMPTemplateParser** (`fedramp_parser.py`)
   - Document parsing (DOCX, PDF, TXT)
   - Control section extraction
   - Text normalization and validation

3. **FedRAMP API** (`fedramp_api.py`)
   - REST API endpoints
   - Web interface
   - File upload handling

4. **Database Schema**
   - SQLite database for control storage
   - Normalized control structure
   - Indexed for fast retrieval

## Features

### Document Processing
- **Multi-format Support**: DOCX, PDF, TXT, MD files
- **Intelligent Parsing**: Extracts control sections automatically
- **Text Normalization**: Cleans and structures extracted text
- **Validation**: Ensures data quality and completeness

### Control Classification
- **Technical Controls**: Measurable through cloud data
- **Non-Technical Controls**: Policy and procedure based
- **Hybrid Controls**: Combination of both types
- **Priority Levels**: High, Medium, Low based on security impact

### Data Management
- **Canonical Schema**: Standardized control structure
- **Relationship Mapping**: Links related controls
- **Version Control**: Tracks control updates
- **Statistics**: Comprehensive reporting and analytics

## Database Schema

### fedramp_controls Table

```sql
CREATE TABLE fedramp_controls (
    id TEXT PRIMARY KEY,                    -- Control ID (e.g., "AC-2")
    family TEXT NOT NULL,                   -- Control family (e.g., "Access Control")
    title TEXT NOT NULL,                    -- Control title
    description TEXT,                       -- Control description
    control_type TEXT NOT NULL,             -- technical/non_technical/hybrid
    priority TEXT NOT NULL,                 -- high/medium/low
    baseline TEXT NOT NULL,                 -- Low/Moderate/High
    requirement_text TEXT NOT NULL,         -- Exact requirement text
    implementation_guidance TEXT,           -- Implementation guidance
    assessment_procedures TEXT,             -- Assessment procedures
    related_controls TEXT,                  -- JSON array of related controls
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### Control Extraction
- `POST /api/fedramp/extract` - Extract controls from template
- `GET /api/fedramp/controls` - Get all controls with filtering
- `GET /api/fedramp/controls/<id>` - Get specific control
- `GET /api/fedramp/statistics` - Get extraction statistics

### Web Interface
- `GET /fedramp` - FedRAMP extraction web interface

## Usage Examples

### 1. Extract Controls from Template

```python
from fedramp_extractor import FedRAMPExtractor
from fedramp_parser import FedRAMPTemplateParser

# Initialize components
extractor = FedRAMPExtractor()
parser = FedRAMPTemplateParser()

# Parse document
parsed_controls = parser.parse_document("fedramp_template.docx")

# Convert and save controls
for parsed_control in parsed_controls:
    control = extractor._create_control_from_parsed(parsed_control, "Low")
    extractor.save_control(control)
```

### 2. Query Controls by Type

```python
# Get all technical controls
technical_controls = extractor.get_controls_by_type(ControlType.TECHNICAL)

# Get controls by family
access_controls = extractor.get_controls_by_family("Access Control")

# Get specific control
control = extractor.get_control("AC-2")
```

### 3. Get Statistics

```python
stats = extractor.get_control_statistics()
print(f"Total controls: {stats['total_controls']}")
print(f"By type: {stats['by_type']}")
print(f"By family: {stats['by_family']}")
```

## Control Classification Logic

### Technical Controls
Identified by keywords and control families:
- **Keywords**: encryption, firewall, authentication, network, system, monitoring, logging, backup, patch, vulnerability, scanning, intrusion detection, antivirus, database, server, cloud, api, endpoint, device
- **Families**: AC, AU, CM, CP, IA, IR, MA, MP, PE, SC, SI

### Non-Technical Controls
Identified by keywords and control families:
- **Keywords**: policy, procedure, training, awareness, personnel, contract, agreement, documentation, planning, risk assessment, governance, compliance, audit, review, approval, authorization, management
- **Families**: AT, CA, PL, PS, RA, SA, SR

### Priority Assignment
- **High Priority**: Critical security functions (AC-1, AC-2, AC-3, AU-1, AU-2, IA-1, IA-2, SC-1, SC-7, SI-1, SI-2)
- **Medium Priority**: Important security functions (CM-1, CM-2, CP-1, CP-2, IR-1, IR-2, MA-1, MA-2)
- **Low Priority**: Supporting security functions (all others)

## File Format Support

### DOCX Files
- Extracts text from paragraphs and tables
- Preserves document structure
- Handles complex formatting

### PDF Files
- Uses PyPDF2 for text extraction
- Handles multi-page documents
- Preserves text formatting

### Text Files
- Supports TXT and MD formats
- Handles various encodings
- Preserves line breaks and structure

## Validation and Quality Assurance

### Parsed Control Validation
- **Required Fields**: Control ID, title, description, requirement text
- **Optional Fields**: Implementation guidance, assessment procedures
- **Data Quality**: Checks for completeness and consistency
- **Statistics**: Tracks validation results

### Database Integrity
- **Primary Key**: Control ID uniqueness
- **Foreign Keys**: Related controls validation
- **Data Types**: Proper type enforcement
- **Indexes**: Performance optimization

## Error Handling

### Document Parsing Errors
- File format validation
- Encoding detection and handling
- Malformed document recovery
- Graceful degradation

### Database Errors
- Connection management
- Transaction rollback
- Data validation
- Error logging

### API Errors
- Input validation
- Error response formatting
- Status code management
- User-friendly messages

## Performance Considerations

### Database Optimization
- Indexed columns for fast queries
- Connection pooling
- Query optimization
- Batch operations

### Memory Management
- Streaming file processing
- Garbage collection
- Memory-efficient data structures
- Resource cleanup

### Scalability
- Modular architecture
- Stateless API design
- Horizontal scaling support
- Caching strategies

## Security Considerations

### Input Validation
- File type validation
- Size limits
- Content sanitization
- Path traversal prevention

### Data Protection
- Secure file handling
- Temporary file cleanup
- Access control
- Audit logging

### API Security
- Input sanitization
- Rate limiting
- Authentication (future)
- Authorization (future)

## Testing

### Unit Tests
- Control classification logic
- Database operations
- API endpoints
- Error handling

### Integration Tests
- End-to-end extraction
- File format support
- Database operations
- API functionality

### Performance Tests
- Large file processing
- Database query performance
- Memory usage
- Response times

## Future Enhancements

### Planned Features
- **Moderate/High Baselines**: Support for additional baselines
- **Advanced Parsing**: ML-based text extraction
- **Control Relationships**: Enhanced relationship mapping
- **Version Control**: Control versioning and history

### Scalability Improvements
- **Database Migration**: PostgreSQL/MySQL support
- **Caching Layer**: Redis integration
- **Background Processing**: Celery task queue
- **Microservices**: Service decomposition

### Integration Features
- **Cloud APIs**: Direct cloud provider integration
- **SSP Generation**: Automated SSP creation
- **Compliance Dashboard**: Real-time compliance monitoring
- **Audit Trail**: Complete audit logging

## Troubleshooting

### Common Issues

1. **File Parsing Errors**
   - Check file format support
   - Verify file integrity
   - Check encoding issues

2. **Database Connection Issues**
   - Verify database file permissions
   - Check disk space
   - Validate database schema

3. **Control Classification Issues**
   - Review classification logic
   - Check control text content
   - Validate family mappings

### Debug Mode
Enable debug logging for detailed error information:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `python test_fedramp_extraction.py`
4. Start development server: `python main.py`

### Code Standards
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation

### Pull Request Process
1. Create feature branch
2. Implement changes with tests
3. Update documentation
4. Submit pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation
- Review the troubleshooting guide
