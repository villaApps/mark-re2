"""Unit tests for Lambda handlers with mocked dependencies."""

import json
import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch, Mock

from src.models.property import PropertyCreate, PropertyType, PropertyStatus
from src.models.scraper import ScraperSource, ScraperResult, ScraperStatus


@pytest.mark.unit
class TestScraperHandler:
    """Tests for Scraper Lambda handler."""

    @pytest.fixture
    def mock_eventbridge(self):
        """Mock EventBridge client."""
        with patch("src.handlers.scraper.events_client") as mock:
            mock.put_events = MagicMock(return_value={"Entries": [{"EventId": "test-id"}]})
            yield mock

    @pytest.fixture
    def mock_scraper_service(self):
        """Mock ScraperService."""
        with patch("src.handlers.scraper.scraper_service") as mock:
            mock.create_run = AsyncMock(return_value=MagicMock(
                run_id="run_123",
                status=ScraperStatus.PENDING,
            ))
            mock.start_run = AsyncMock(return_value=MagicMock(
                run_id="run_123",
                status=ScraperStatus.RUNNING,
            ))
            mock.complete_run = AsyncMock(return_value=MagicMock(
                run_id="run_123",
                status=ScraperStatus.COMPLETED,
                total_properties_found=10,
            ))
            mock.add_run_error = AsyncMock()
            mock.save_raw_data = AsyncMock(return_value="s3://bucket/key")
            yield mock

    @pytest.fixture
    def mock_property_service(self):
        """Mock PropertyService."""
        with patch("src.handlers.scraper.property_service") as mock:
            mock.create_property = AsyncMock(return_value=MagicMock(
                property_id="prop_123",
                title="Test Property",
            ))
            mock.get_property = AsyncMock(side_effect=Exception("Not found"))
            mock.update_property = AsyncMock(return_value=MagicMock(
                property_id="prop_123",
                title="Updated Property",
            ))
            yield mock

    @pytest.fixture
    def mock_scraper_module(self):
        """Mock scraper module classes."""
        mock_property = MagicMock()
        mock_property.id = "ext_123"
        mock_property.url = "https://test.com/property/123"
        mock_property.title = "Test Property"
        mock_property.location = "Sliema"
        mock_property.property_type = "apartment"
        mock_property.price = Decimal("450000")
        mock_property.bedrooms = 3
        mock_property.bathrooms = 2
        mock_property.square_meters = 120
        mock_property.images = ["https://test.com/img1.jpg"]
        mock_property.model_dump = MagicMock(return_value={
            "id": "ext_123",
            "title": "Test Property",
            "price": "450000",
        })

        mock_scraper = AsyncMock()
        mock_scraper.scrape_listings = AsyncMock(return_value=[mock_property])
        mock_scraper.__aenter__ = AsyncMock(return_value=mock_scraper)
        mock_scraper.__aexit__ = AsyncMock(return_value=None)

        with patch("src.handlers.scraper.SimonEstatesScraper", return_value=mock_scraper):
            with patch("src.handlers.scraper.FrankSaltScraper", return_value=mock_scraper):
                with patch("src.handlers.scraper.RemaxScraper", return_value=mock_scraper):
                    with patch("src.handlers.scraper.DhaliaScraper", return_value=mock_scraper):
                        with patch("src.handlers.scraper.SCRAPER_AVAILABLE", True):
                            yield mock_scraper

    @pytest.mark.asyncio
    async def test_handler_with_schedule_event(
        self,
        mock_dynamodb,
        mock_eventbridge,
        mock_scraper_service,
        mock_property_service,
        mock_lambda_context,
    ):
        """Test handler with scheduled EventBridge event."""
        from src.handlers.scraper import handler

        event = {"source": "aws.events", "detail-type": "Scheduled Event"}

        with patch("src.handlers.scraper.SCRAPER_AVAILABLE", False):
            response = await handler(event, mock_lambda_context)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["success"] is True
        assert "runId" in body

    @pytest.mark.asyncio
    async def test_handler_publishes_completion_event(
        self,
        mock_dynamodb,
        mock_eventbridge,
        mock_scraper_service,
        mock_property_service,
        mock_lambda_context,
    ):
        """Test that handler publishes ScraperComplete event."""
        from src.handlers.scraper import handler

        event = {"source": "schedule"}

        with patch("src.handlers.scraper.SCRAPER_AVAILABLE", False):
            await handler(event, mock_lambda_context)

        mock_eventbridge.put_events.assert_called_once()
        call_args = mock_eventbridge.put_events.call_args
        entries = call_args[1]["Entries"]
        assert len(entries) == 1
        assert entries[0]["Source"] == "malta.property.scraper"
        assert entries[0]["DetailType"] == "ScraperComplete"


@pytest.mark.unit
class TestAnalyzerHandler:
    """Tests for Analyzer Lambda handler."""

    @pytest.fixture
    def mock_eventbridge(self):
        """Mock EventBridge client."""
        with patch("src.handlers.analyzer.events_client") as mock:
            mock.put_events = MagicMock(return_value={"Entries": [{"EventId": "test-id"}]})
            yield mock

    @pytest.fixture
    def mock_property_service(self):
        """Mock PropertyService."""
        mock_property = MagicMock()
        mock_property.property_id = "prop_123"
        mock_property.price = Decimal("450000")
        mock_property.town = "Sliema"
        mock_property.bedrooms = 3
        mock_property.roi_score = None

        with patch("src.handlers.analyzer.property_service") as mock:
            mock.list_properties = AsyncMock(return_value=MagicMock(
                items=[mock_property],
                total=1,
            ))
            mock.update_roi_score = AsyncMock()
            mock.get_property = AsyncMock(return_value=mock_property)
            yield mock

    @pytest.fixture
    def mock_analysis_service(self):
        """Mock AnalysisService."""
        mock_analysis = MagicMock()
        mock_analysis.analysis_id = "anl_123"
        mock_analysis.property_id = "prop_123"
        mock_analysis.roi_score = Decimal("75.5")
        mock_analysis.roi_percentage = Decimal("8.5")

        with patch("src.handlers.analyzer.analysis_service") as mock:
            mock.calculate_roi = AsyncMock(return_value=mock_analysis)
            mock.save_analysis = AsyncMock(return_value=mock_analysis)
            mock.get_top_opportunities = AsyncMock(return_value=[])
            yield mock

    @pytest.fixture
    def mock_analytics_module(self):
        """Mock analytics module functions."""
        mock_result = MagicMock()
        mock_result.opportunity_score = 80
        mock_result.cash_on_cash_return = Decimal("0.085")
        mock_result.gross_rental_yield = Decimal("0.045")
        mock_result.net_rental_yield = Decimal("0.035")
        mock_result.cap_rate = Decimal("0.040")
        mock_result.analysis_id = "anl_123"

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
            with patch("src.handlers.analyzer.ANALYTICS_AVAILABLE", True):
                yield mock_analyze

    @pytest.mark.asyncio
    async def test_handler_with_scraper_complete_event(
        self,
        mock_dynamodb,
        mock_eventbridge,
        mock_property_service,
        mock_analysis_service,
        mock_lambda_context,
    ):
        """Test handler with ScraperComplete event."""
        from src.handlers.analyzer import handler

        event = {
            "source": "malta.property.scraper",
            "detail-type": "ScraperComplete",
            "detail": json.dumps({"runId": "run_123", "totalProperties": 10}),
        }

        with patch("src.handlers.analyzer.ANALYTICS_AVAILABLE", False):
            response = await handler(event, mock_lambda_context)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["success"] is True

    @pytest.mark.asyncio
    async def test_handler_updates_roi_scores(
        self,
        mock_dynamodb,
        mock_eventbridge,
        mock_property_service,
        mock_analysis_service,
        mock_lambda_context,
    ):
        """Test that handler updates property ROI scores."""
        from src.handlers.analyzer import handler

        event = {"source": "malta.property.scraper", "detail-type": "ScraperComplete"}

        with patch("src.handlers.analyzer.ANALYTICS_AVAILABLE", False):
            await handler(event, mock_lambda_context)

        mock_property_service.update_roi_score.assert_called()

    @pytest.mark.asyncio
    async def test_handler_publishes_analysis_complete_event(
        self,
        mock_dynamodb,
        mock_eventbridge,
        mock_property_service,
        mock_analysis_service,
        mock_lambda_context,
    ):
        """Test that handler publishes AnalysisComplete event."""
        from src.handlers.analyzer import handler

        event = {"source": "malta.property.scraper", "detail-type": "ScraperComplete"}

        with patch("src.handlers.analyzer.ANALYTICS_AVAILABLE", False):
            await handler(event, mock_lambda_context)

        mock_eventbridge.put_events.assert_called()


@pytest.mark.unit
class TestHandlerIntegration:
    """Integration tests for handler interactions."""

    @pytest.mark.asyncio
    async def test_scraper_to_analyzer_event_flow(
        self,
        mock_dynamodb,
        mock_lambda_context,
    ):
        """Test the event flow from scraper to analyzer."""
        from src.handlers.scraper import handler as scraper_handler
        from src.handlers.analyzer import handler as analyzer_handler

        # Mock EventBridge to capture events
        published_events = []

        def mock_put_events(Entries, **kwargs):
            published_events.extend(Entries)
            return {"Entries": [{"EventId": f"event_{i}"} for i in range(len(Entries))]}

        with patch("src.handlers.scraper.events_client") as mock_scraper_events:
            mock_scraper_events.put_events = mock_put_events

            with patch("src.handlers.analyzer.events_client") as mock_analyzer_events:
                mock_analyzer_events.put_events = mock_put_events

                with patch("src.handlers.scraper.SCRAPER_AVAILABLE", False):
                    with patch("src.handlers.analyzer.ANALYTICS_AVAILABLE", False):
                        # Run scraper
                        scraper_event = {"source": "schedule"}
                        scraper_response = await scraper_handler(scraper_event, mock_lambda_context)

                        assert scraper_response["statusCode"] == 200

                        # Verify ScraperComplete event was published
                        scraper_events = [e for e in published_events if e.get("DetailType") == "ScraperComplete"]
                        assert len(scraper_events) == 1

                        # Run analyzer with the scraper event
                        analyzer_event = {
                            "source": "malta.property.scraper",
                            "detail-type": "ScraperComplete",
                            "detail": scraper_events[0]["Detail"],
                        }
                        analyzer_response = await analyzer_handler(analyzer_event, mock_lambda_context)

                        assert analyzer_response["statusCode"] == 200

                        # Verify AnalysisComplete event was published
                        analyzer_events = [e for e in published_events if e.get("DetailType") == "AnalysisComplete"]
                        assert len(analyzer_events) == 1
