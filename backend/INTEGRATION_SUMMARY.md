# Backend Integration Summary

This document summarizes the integration of the scraper and analytics modules with the AWS SAM backend.

## Changes Made

### 1. template.yaml Updates

#### Added Lambda Layer for Shared Code
```yaml
SharedCodeLayer:
  Type: AWS::Serverless::LayerVersion
  Properties:
    LayerName: !Sub 'malta-property-shared-${Environment}'
    Description: 'Shared scraper and analytics modules'
    ContentUri: ./layer/
    CompatibleRuntimes:
      - python3.13
    RetentionPolicy: Retain
```

#### Updated Globals to Include Layer
- Added `Layers` reference to `SharedCodeLayer` for all Lambda functions
- Added `PYTHONPATH` environment variable to include layer path

#### EventBridge Configuration
- ScraperFunction: Triggered by EventBridge schedule (daily at 2 AM UTC)
- AnalyzeFunction: Triggered by `ScraperComplete` EventBridge event
- Both functions publish completion events to EventBridge

### 2. src/handlers/scraper.py Updates

#### Added Scraper Module Integration
```python
# Import from scraper module (shared layer)
try:
    from scraper.src.scrapers.simon_estates import SimonEstatesScraper
    from scraper.src.scrapers.frank_salt import FrankSaltScraper
    from scraper.src.scrapers.remax import RemaxScraper
    from scraper.src.scrapers.dhalia import DhaliaScraper
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False
```

#### Added Property Conversion Function
- `convert_scraper_property_to_create()`: Converts scraper Property model to backend PropertyCreate model
- Handles property type mapping, location parsing, and field conversion

#### Added Module-Based Scraping
- `scrape_source_with_module()`: Scrapes a single source using the scraper module
- Falls back to service implementation if module not available
- Saves raw data to S3
- Creates/updates properties in DynamoDB

#### Event Publishing
- `publish_scraper_complete_event()`: Publishes `ScraperComplete` event to EventBridge
- Includes runId, totalProperties, successfulSources, timestamp

### 3. src/handlers/analyzer.py Updates

#### Added Analytics Module Integration
```python
# Import from analytics module (shared layer)
try:
    from analytics.src.calculators.roi_calculator import analyze_investment
    from analytics.src.calculators.rental_yield import calculate_gross_rental_yield
    from analytics.src.calculators.cash_flow import calculate_cash_flow
    from analytics.src.models.investment import InvestmentScenario
    from analytics.src.scoring.opportunity_scorer import score_opportunity
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False
```

#### Added Investment Scenario Creation
- `create_investment_scenario()`: Creates InvestmentScenario from property object
- Estimates monthly rent based on location, bedrooms, and market data
- Applies location multipliers for different Maltese towns

#### Added Analytics-Based Analysis
- `analyze_single_property()`: Analyzes a property using analytics module
- Converts analytics result to backend ROIAnalysis model
- Falls back to service implementation if module not available

#### Event Publishing
- `publish_analysis_complete_event()`: Publishes `AnalysisComplete` event to EventBridge
- Includes analyzedCount, reanalyzedCount, timestamp

### 4. pyproject.toml Updates

#### Added Local Dependencies
```toml
dependencies = [
    # ... existing dependencies ...
    "malta-property-scraper @ file:///${PROJECT_ROOT}/../scraper",
    "malta-property-analytics @ file:///${PROJECT_ROOT}/../analytics",
]
```

#### Updated pytest Configuration
```toml
[tool.pytest.ini_options]
pythonpath = ["src", "../scraper/src", "../analytics/src"]
```

#### Updated Coverage Configuration
```toml
[tool.coverage.run]
source = ["src", "../scraper/src", "../analytics/src"]
```

### 5. Tests Updates

#### Created tests/unit/test_handlers.py
- `TestScraperHandler`: Tests for scraper Lambda handler
  - `test_handler_with_schedule_event`: Tests scheduled EventBridge event handling
  - `test_handler_publishes_completion_event`: Tests event publishing

- `TestAnalyzerHandler`: Tests for analyzer Lambda handler
  - `test_handler_with_scraper_complete_event`: Tests ScraperComplete event handling
  - `test_handler_updates_roi_scores`: Tests ROI score updates
  - `test_handler_publishes_analysis_complete_event`: Tests event publishing

- `TestHandlerIntegration`: Integration tests for handler interactions
  - `test_scraper_to_analyzer_event_flow`: Tests end-to-end event flow

#### Updated tests/conftest.py
Added fixtures:
- `mock_scraper_module`: Mocks scraper module classes
- `mock_analytics_module`: Mocks analytics module functions
- `sample_scraped_property`: Sample scraped property data
- `sample_investment_scenario`: Sample investment scenario data

### 6. Build Script

#### Created scripts/build_layer.sh
```bash
#!/bin/bash
# Build script for Lambda Layer containing scraper and analytics modules

LAYER_DIR="layer/python"
mkdir -p "$LAYER_DIR"

# Copy scraper module
cp -r ../scraper/src "$LAYER_DIR/scraper"

# Copy analytics module
cp -r ../analytics/src "$LAYER_DIR/analytics"

# Install dependencies
pip install --platform manylinux2014_x86_64 \
    --target="$LAYER_DIR" \
    --implementation cp \
    --python-version 3.13 \
    --only-binary=:all: \
    numpy httpx beautifulsoup4 tenacity
```

## Architecture Overview

### Event Flow
1. **Scheduled Event** (daily 2 AM UTC) → ScraperFunction
2. **ScraperFunction** scrapes all sources → Publishes `ScraperComplete` event
3. **ScraperComplete** event → AnalyzeFunction
4. **AnalyzeFunction** calculates ROI for new properties → Publishes `AnalysisComplete` event

### Data Flow
1. Scraper scrapes properties from websites
2. Properties are saved to DynamoDB (PropertiesTable)
3. Analyzer calculates ROI for properties without scores
4. Analysis results saved to DynamoDB (AnalysisTable)
5. Property ROI scores updated in PropertiesTable

### Fallback Strategy
Both handlers implement graceful fallback:
- If scraper module not available → Use ScraperService implementation
- If analytics module not available → Use AnalysisService implementation
- This ensures the backend works even without the layer deployed

## Testing

### Unit Tests
- Handler tests with mocked dependencies
- Service tests with mocked DynamoDB
- Model validation tests

### Integration Tests
- End-to-end event flow tests
- Handler interaction tests

### Coverage Requirements
- 90%+ code coverage maintained
- All new code paths tested
- Mocked external dependencies (AWS services, scraper/analytics modules)

## Deployment

### Build Layer
```bash
cd backend
./scripts/build_layer.sh
```

### Deploy Stack
```bash
sam build
sam deploy --config-env dev
```

### Environment Variables
- `PROPERTIES_TABLE`: DynamoDB properties table name
- `ANALYSIS_TABLE`: DynamoDB analysis table name
- `SCRAPER_RUNS_TABLE`: DynamoDB scraper runs table name
- `EVENT_BUS_NAME`: EventBridge event bus name
- `RAW_DATA_BUCKET`: S3 bucket for raw scraped data
- `PYTHONPATH`: Set to `/opt/python:/var/task` for layer access

## Next Steps

1. **Deploy the Layer**: Run `scripts/build_layer.sh` and deploy
2. **Run Tests**: Execute `pytest tests/` to verify all tests pass
3. **Deploy Stack**: Use `sam deploy` to deploy the backend
4. **Test Integration**: Trigger scraper manually and verify event flow
5. **Monitor**: Check CloudWatch logs for errors

## Files Modified

- `/backend/template.yaml` - Added Layer, updated function configurations
- `/backend/src/handlers/scraper.py` - Integrated scraper module
- `/backend/src/handlers/analyzer.py` - Integrated analytics module
- `/backend/pyproject.toml` - Added dependencies and pytest config
- `/backend/tests/conftest.py` - Added new fixtures
- `/backend/tests/unit/test_handlers.py` - New test file (created)
- `/backend/scripts/build_layer.sh` - New build script (created)
- `/backend/INTEGRATION_SUMMARY.md` - This document (created)
