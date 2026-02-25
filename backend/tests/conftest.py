"""Pytest fixtures and configuration."""

import os
import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import MagicMock, patch

import boto3
from moto import mock_aws

# Set environment variables for testing
os.environ["PROPERTIES_TABLE"] = "properties-test"
os.environ["ANALYSIS_TABLE"] = "analysis-test"
os.environ["SCRAPER_RUNS_TABLE"] = "scraper-runs-test"
os.environ["EVENT_BUS_NAME"] = "property-events-test"
os.environ["DLQ_URL"] = "https://sqs.eu-west-1.amazonaws.com/123456789012/test-dlq"
os.environ["RAW_DATA_BUCKET"] = "test-raw-data-bucket"
os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["POWERTOOLS_SERVICE_NAME"] = "malta-property-analyzer-test"
os.environ["LOG_LEVEL"] = "DEBUG"


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"


@pytest.fixture(scope="function")
def mock_dynamodb(aws_credentials):
    """Create mocked DynamoDB tables."""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
        
        # Create Properties table
        properties_table = dynamodb.create_table(
            TableName="properties-test",
            KeySchema=[{"AttributeName": "propertyId", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "propertyId", "AttributeType": "S"},
                {"AttributeName": "location", "AttributeType": "S"},
                {"AttributeName": "createdAt", "AttributeType": "S"},
                {"AttributeName": "priceRange", "AttributeType": "S"},
                {"AttributeName": "price", "AttributeType": "N"},
                {"AttributeName": "propertyType", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "LocationIndex",
                    "KeySchema": [
                        {"AttributeName": "location", "KeyType": "HASH"},
                        {"AttributeName": "createdAt", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "PriceRangeIndex",
                    "KeySchema": [
                        {"AttributeName": "priceRange", "KeyType": "HASH"},
                        {"AttributeName": "price", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "PropertyTypeIndex",
                    "KeySchema": [
                        {"AttributeName": "propertyType", "KeyType": "HASH"},
                        {"AttributeName": "createdAt", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        
        # Create Analysis table
        analysis_table = dynamodb.create_table(
            TableName="analysis-test",
            KeySchema=[{"AttributeName": "analysisId", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "analysisId", "AttributeType": "S"},
                {"AttributeName": "propertyId", "AttributeType": "S"},
                {"AttributeName": "createdAt", "AttributeType": "S"},
                {"AttributeName": "roiScore", "AttributeType": "N"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "PropertyIndex",
                    "KeySchema": [
                        {"AttributeName": "propertyId", "KeyType": "HASH"},
                        {"AttributeName": "createdAt", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "ROIScoreIndex",
                    "KeySchema": [
                        {"AttributeName": "roiScore", "KeyType": "HASH"},
                        {"AttributeName": "createdAt", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        
        # Create Scraper Runs table
        scraper_runs_table = dynamodb.create_table(
            TableName="scraper-runs-test",
            KeySchema=[{"AttributeName": "runId", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "runId", "AttributeType": "S"},
                {"AttributeName": "status", "AttributeType": "S"},
                {"AttributeName": "startedAt", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "StatusIndex",
                    "KeySchema": [
                        {"AttributeName": "status", "KeyType": "HASH"},
                        {"AttributeName": "startedAt", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        
        yield {
            "dynamodb": dynamodb,
            "properties_table": properties_table,
            "analysis_table": analysis_table,
            "scraper_runs_table": scraper_runs_table,
        }


@pytest.fixture(scope="function")
def mock_s3(aws_credentials):
    """Create mocked S3 bucket."""
    with mock_aws():
        s3 = boto3.client("s3", region_name="eu-west-1")
        s3.create_bucket(
            Bucket="test-raw-data-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-1"},
        )
        yield s3


@pytest.fixture(scope="function")
def mock_sqs(aws_credentials):
    """Create mocked SQS queue."""
    with mock_aws():
        sqs = boto3.client("sqs", region_name="eu-west-1")
        queue = sqs.create_queue(QueueName="test-dlq")
        yield sqs


@pytest.fixture(scope="function")
def mock_eventbridge(aws_credentials):
    """Create mocked EventBridge event bus."""
    with mock_aws():
        events = boto3.client("events", region_name="eu-west-1")
        events.create_event_bus(Name="property-events-test")
        yield events


@pytest.fixture(scope="function")
def mock_secretsmanager(aws_credentials):
    """Create mocked Secrets Manager."""
    with mock_aws():
        secrets = boto3.client("secretsmanager", region_name="eu-west-1")
        secrets.create_secret(
            Name="malta-property-scraper/api-keys-test",
            SecretString='{"scrapingbee_key":"test_key","proxy_key":"test_proxy"}',
        )
        yield secrets


@pytest.fixture
def sample_property_data():
    """Return sample property data for testing."""
    return {
        "property_id": "prop_test123",
        "external_id": "ext_12345",
        "source_url": "https://example.com/property/123",
        "source_name": "test_source",
        "title": "Beautiful 3-bedroom apartment in Sliema",
        "description": "Spacious apartment with sea views",
        "property_type": "apartment",
        "status": "for_sale",
        "price": Decimal("450000"),
        "location": {
            "latitude": 35.9123,
            "longitude": 14.5034,
            "address": "123 Test Street, Sliema",
            "locality": "Sliema",
        },
        "region": "Central",
        "town": "Sliema",
        "bedrooms": 3,
        "bathrooms": 2,
        "total_rooms": 5,
        "internal_area_sqm": Decimal("120"),
        "external_area_sqm": Decimal("20"),
        "floor_number": 2,
        "total_floors": 5,
        "year_built": 2010,
        "condition": "good",
        "features": ["sea_view", "balcony", "air_conditioning"],
        "has_garage": True,
        "has_garden": False,
        "has_pool": False,
        "has_elevator": True,
        "is_furnished": True,
        "has_air_conditioning": True,
        "has_heating": False,
        "images": ["https://example.com/img1.jpg"],
        "is_active": True,
    }


@pytest.fixture
def sample_roi_input_data():
    """Return sample ROI input data for testing."""
    return {
        "property_id": "prop_test123",
        "strategy": "buy_to_let",
        "down_payment_percentage": Decimal("0.20"),
        "interest_rate": Decimal("0.035"),
        "loan_term_years": 25,
        "closing_costs": Decimal("0.05"),
        "renovation_costs": Decimal("0"),
        "monthly_rent": Decimal("1800"),
        "occupancy_rate": Decimal("0.90"),
        "annual_rent_increase": Decimal("0.03"),
        "annual_appreciation_rate": Decimal("0.03"),
    }


@pytest.fixture
def sample_analysis_data():
    """Return sample analysis data for testing."""
    return {
        "analysis_id": "anl_test456",
        "property_id": "prop_test123",
        "strategy": "buy_to_let",
        "purchase_price": Decimal("450000"),
        "down_payment_percentage": Decimal("0.20"),
        "interest_rate": Decimal("0.035"),
        "loan_term_years": 25,
        "closing_costs": Decimal("0.05"),
        "renovation_costs": Decimal("0"),
        "rental_income": {
            "monthly_rent": Decimal("1800"),
            "occupancy_rate": Decimal("0.90"),
            "annual_rent_increase": Decimal("0.03"),
        },
        "monthly_expenses": {
            "mortgage_payment": Decimal("1440"),
            "property_tax": Decimal("37.50"),
            "insurance": Decimal("75"),
            "maintenance": Decimal("375"),
            "management_fees": Decimal("180"),
            "utilities": Decimal("110"),
            "vacancy_reserve": Decimal("255"),
        },
        "annual_appreciation_rate": Decimal("0.03"),
    }


@pytest.fixture
def mock_lambda_context():
    """Return a mock Lambda context."""
    context = MagicMock()
    context.function_name = "test-function"
    context.memory_limit_in_mb = 512
    context.invoked_function_arn = "arn:aws:lambda:eu-west-1:123456789012:function:test"
    context.aws_request_id = "test-request-id"
    context.log_group_name = "/aws/lambda/test"
    context.log_stream_name = "2024/01/01/test-stream"
    context.get_remaining_time_in_millis.return_value = 30000
    return context


@pytest.fixture
def mock_scraper_module():
    """Mock the scraper module for testing."""
    with patch.dict("sys.modules", {
        "scraper": MagicMock(),
        "scraper.src": MagicMock(),
        "scraper.src.scrapers": MagicMock(),
        "scraper.src.models": MagicMock(),
    }):
        mock_scraper = MagicMock()
        mock_scraper.scrape_listings = AsyncMock(return_value=[])
        mock_scraper.__aenter__ = AsyncMock(return_value=mock_scraper)
        mock_scraper.__aexit__ = AsyncMock(return_value=None)

        mock_simon = MagicMock(return_value=mock_scraper)
        mock_frank = MagicMock(return_value=mock_scraper)
        mock_remax = MagicMock(return_value=mock_scraper)
        mock_dhalia = MagicMock(return_value=mock_scraper)

        with patch("src.handlers.scraper.SimonEstatesScraper", mock_simon):
            with patch("src.handlers.scraper.FrankSaltScraper", mock_frank):
                with patch("src.handlers.scraper.RemaxScraper", mock_remax):
                    with patch("src.handlers.scraper.DhaliaScraper", mock_dhalia):
                        yield {
                            "simon": mock_simon,
                            "frank": mock_frank,
                            "remax": mock_remax,
                            "dhalia": mock_dhalia,
                        }


@pytest.fixture
def mock_analytics_module():
    """Mock the analytics module for testing."""
    mock_result = MagicMock()
    mock_result.opportunity_score = 75
    mock_result.cash_on_cash_return = Decimal("0.075")
    mock_result.gross_rental_yield = Decimal("0.045")
    mock_result.net_rental_yield = Decimal("0.035")
    mock_result.cap_rate = Decimal("0.040")
    mock_result.analysis_id = "anl_test123"

    mock_purchase_costs = MagicMock()
    mock_purchase_costs.total = Decimal("20000")

    mock_cash_flow = MagicMock()
    mock_cash_flow.monthly_mortgage_payment = Decimal("1200")
    mock_cash_flow.property_tax = Decimal("50")
    mock_cash_flow.insurance = Decimal("75")
    mock_cash_flow.maintenance = Decimal("150")
    mock_cash_flow.management_fees = Decimal("180")
    mock_cash_flow.utilities = Decimal("100")
    mock_cash_flow.vacancy_reserve = Decimal("100")

    with patch("src.handlers.analyzer.analyze_investment") as mock_analyze:
        mock_analyze.return_value = (mock_result, mock_purchase_costs, mock_cash_flow)
        yield mock_analyze


@pytest.fixture
def sample_scraped_property():
    """Return a sample scraped property for testing."""
    return {
        "id": "ext_12345",
        "source": "simonestates",
        "url": "https://simonestates.com/property/12345",
        "title": "Beautiful 3-bedroom apartment in Sliema",
        "location": "Sliema, Malta",
        "property_type": "apartment",
        "price": "450000",
        "bedrooms": 3,
        "bathrooms": 2,
        "square_meters": 120.0,
        "images": ["https://simonestates.com/img1.jpg"],
        "scraped_at": "2024-01-15T10:00:00Z",
    }


@pytest.fixture
def sample_investment_scenario():
    """Return a sample investment scenario for testing."""
    return {
        "property_price": Decimal("450000"),
        "property_area": "sliema",
        "is_first_time_buyer": True,
        "down_payment_percent": Decimal("0.20"),
        "loan_interest_rate": Decimal("0.035"),
        "loan_term_years": 25,
        "monthly_rent": Decimal("1800"),
        "vacancy_rate": Decimal("0.05"),
        "property_management_percent": Decimal("0.10"),
        "maintenance_reserve_percent": Decimal("0.05"),
        "insurance_annual_percent": Decimal("0.003"),
        "annual_appreciation": Decimal("0.03"),
        "annual_rent_increase": Decimal("0.025"),
    }
