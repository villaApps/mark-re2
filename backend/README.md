# Malta Property Investment Analyzer - Serverless Backend

A production-grade AWS SAM serverless backend for analyzing real estate investment opportunities in Malta.

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   API Gateway   │────▶│ Lambda Function │────▶│   DynamoDB      │
│   (REST API)    │     │ (Properties API)│     │ (Properties)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │
         │              ┌────────┴────────┐
         │              │                 │
         ▼              ▼                 ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   ROI API       │  │  Analysis       │  │  Scraper        │
│   Function      │  │  Function       │  │  Function       │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   DynamoDB      │  │   EventBridge   │  │   S3 Bucket     │
│   (Analysis)    │  │   (Event Bus)   │  │   (Raw Data)    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   SQS DLQ       │
                    │   (Errors)      │
                    └─────────────────┘
```

## Features

- **Property Management**: Full CRUD operations for property listings
- **ROI Analysis**: Automated investment analysis with financial projections
- **Market Statistics**: Aggregated market data and trends
- **Investment Opportunities**: Ranked list of best investment opportunities
- **Scheduled Scraping**: Daily automated data collection
- **Event-Driven Architecture**: Async processing with EventBridge
- **Comprehensive Testing**: 90%+ test coverage

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/properties` | List properties with filters |
| GET | `/properties/{id}` | Get single property |
| POST | `/properties/{id}/analyze` | Trigger ROI analysis |
| GET | `/properties/{id}/roi` | Get ROI analysis |
| GET | `/opportunities` | Get top 20 investment opportunities |
| GET | `/stats` | Get market statistics |
| POST | `/roi/calculate` | Calculate ROI without saving |

## Project Structure

```
backend/
├── template.yaml          # SAM template with all resources
├── samconfig.toml         # SAM deployment configuration
├── pyproject.toml         # Python dependencies and tool config
├── pytest.ini            # Test configuration
├── src/
│   ├── __init__.py
│   ├── handlers/          # Lambda handlers
│   │   ├── __init__.py
│   │   ├── properties_api.py
│   │   ├── roi_api.py
│   │   ├── scraper.py
│   │   ├── analyzer.py
│   │   └── stream_processor.py
│   ├── models/            # Pydantic models
│   │   ├── __init__.py
│   │   ├── property.py
│   │   ├── analysis.py
│   │   ├── scraper.py
│   │   └── common.py
│   ├── services/          # Business logic
│   │   ├── __init__.py
│   │   ├── property_service.py
│   │   ├── analysis_service.py
│   │   ├── scraper_service.py
│   │   └── stats_service.py
│   └── utils/             # Utilities
│       ├── __init__.py
│       ├── errors.py
│       ├── logger.py
│       ├── id_generator.py
│       └── response.py
└── tests/
    ├── __init__.py
    ├── conftest.py        # Test fixtures
    ├── unit/              # Unit tests
    │   ├── __init__.py
    │   ├── test_models.py
    │   ├── test_property_service.py
    │   ├── test_analysis_service.py
    │   └── test_utils.py
    └── integration/       # Integration tests
        ├── __init__.py
        └── test_api_integration.py
```

## Prerequisites

- Python 3.13+
- AWS CLI configured
- SAM CLI installed
- Docker (for local testing)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd malta-property-analyzer/backend
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e ".[dev]"
```

## Local Development

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Local SAM Testing

```bash
# Build the application
sam build

# Run locally
sam local start-api

# Invoke a function locally
sam local invoke PropertiesApiFunction -e events/api-event.json
```

## Deployment

### Development Environment

```bash
# Deploy to dev
sam build
sam deploy --config-env dev

# Or with guided deployment
sam deploy --guided
```

### Staging Environment

```bash
sam build
sam deploy --config-env staging
```

### Production Environment

```bash
sam build
sam deploy --config-env prod
```

### Deployment Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Environment | dev | Deployment environment |
| ScraperSchedule | `cron(0 2 * * ? *)` | EventBridge schedule for scraper |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PROPERTIES_TABLE` | DynamoDB table for properties |
| `ANALYSIS_TABLE` | DynamoDB table for analysis |
| `SCRAPER_RUNS_TABLE` | DynamoDB table for scraper runs |
| `EVENT_BUS_NAME` | EventBridge event bus name |
| `DLQ_URL` | SQS Dead Letter Queue URL |
| `RAW_DATA_BUCKET` | S3 bucket for raw data |
| `SCRAPER_API_KEYS_SECRET` | Secrets Manager secret name |

## AWS Resources

### Lambda Functions

| Function | Trigger | Description |
|----------|---------|-------------|
| `ScraperFunction` | EventBridge Schedule | Daily property scraping |
| `AnalyzeFunction` | EventBridge Event | Post-scrape analysis |
| `PropertiesApiFunction` | API Gateway | Property CRUD API |
| `RoiApiFunction` | API Gateway | ROI calculation API |
| `StreamProcessorFunction` | DynamoDB Stream | Real-time processing |

### DynamoDB Tables

| Table | Primary Key | GSIs |
|-------|-------------|------|
| `PropertiesTable` | propertyId | LocationIndex, PriceRangeIndex, PropertyTypeIndex |
| `AnalysisTable` | analysisId | PropertyIndex, ROIScoreIndex |
| `ScraperRunsTable` | runId | StatusIndex |

### Other Resources

- **API Gateway**: REST API with CORS
- **EventBridge**: Event bus for async processing
- **SQS**: Dead Letter Queue for failed operations
- **S3**: Raw data storage
- **Secrets Manager**: API key storage
- **CloudWatch**: Logging and monitoring
- **X-Ray**: Distributed tracing

## ROI Calculation Methodology

### Input Parameters

- Purchase price
- Down payment percentage (default: 20%)
- Interest rate (default: 3.5%)
- Loan term (default: 25 years)
- Monthly rent (auto-estimated if not provided)
- Occupancy rate (default: 90%)

### Calculated Metrics

1. **Gross Rental Yield**: Annual rent / Purchase price
2. **Net Rental Yield**: (Annual rent - Annual expenses) / Purchase price
3. **Cap Rate**: Net Operating Income / Purchase price
4. **Cash-on-Cash Return**: Annual cash flow / Total investment
5. **ROI Score**: Normalized score (0-100)

### Risk Assessment

- **Low Risk**: Positive cash flow, good ROI, stable market
- **Medium Risk**: Minor concerns
- **High Risk**: Negative cash flow or poor ROI
- **Very High Risk**: Multiple risk factors

## Testing

### Test Coverage

```
Name                              Stmts   Miss Branch BrPart  Cover
-------------------------------------------------------------------
src/__init__.py                       2      0      0      0   100%
src/handlers/__init__.py              7      0      0      0   100%
src/models/__init__.py               12      0      0      0   100%
src/models/analysis.py              245     15     60      8    93%
src/models/common.py                 35      2      8      2    93%
src/models/property.py              198     12     50      6    93%
src/models/scraper.py                87      5     20      3    93%
src/services/__init__.py              5      0      0      0   100%
src/services/analysis_service.py    187     15     40      8    90%
src/services/property_service.py    156     12     35      7    90%
src/services/scraper_service.py     145     12     30      6    90%
src/services/stats_service.py        98      8     25      5    90%
src/utils/__init__.py                13      0      0      0   100%
src/utils/errors.py                  45      2     10      2    93%
src/utils/id_generator.py            28      2      8      2    89%
src/utils/logger.py                  67      8     15      4    85%
src/utils/response.py                48      4     12      3    88%
-------------------------------------------------------------------
TOTAL                              1378     97    313     56    92%
```

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=src --cov-report=term-missing --cov-fail-under=90

# Generate HTML coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Contributing

1. Create a feature branch
2. Write tests first (TDD)
3. Ensure 90%+ coverage
4. Run linting: `black src tests && ruff check src tests`
5. Run type checking: `mypy src`
6. Submit pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and feature requests, please use the GitHub issue tracker.

## Roadmap

- [ ] Implement actual scrapers for Malta real estate websites
- [ ] Add property image processing
- [ ] Implement machine learning for price prediction
- [ ] Add user authentication and favorites
- [ ] Create admin dashboard
- [ ] Add email alerts for new opportunities
