"""Unit tests for Pydantic models."""

import pytest
from datetime import datetime
from decimal import Decimal

from src.models.property import (
    Property,
    PropertyCreate,
    PropertyUpdate,
    PropertyFilter,
    PropertyType,
    PropertyStatus,
    PriceRange,
)
from src.models.analysis import (
    ROIAnalysis,
    ROIInput,
    OpportunityFilter,
    InvestmentStrategy,
    RiskLevel,
    MonthlyExpenses,
    RentalIncome,
)
from src.models.scraper import (
    ScraperRun,
    ScraperSource,
    ScraperStatus,
    ScrapedProperty,
)
from src.models.common import Location, ApiResponse, PaginatedResponse


class TestLocation:
    """Tests for Location model."""

    def test_location_creation(self):
        """Test creating a Location instance."""
        location = Location(
            latitude=35.9123,
            longitude=14.5034,
            address="123 Test Street",
            locality="Sliema",
        )
        assert location.latitude == 35.9123
        assert location.longitude == 14.5034
        assert location.address == "123 Test Street"
        assert location.locality == "Sliema"

    def test_location_validation(self):
        """Test Location validation."""
        with pytest.raises(ValueError):
            Location(latitude=100, longitude=14.5)  # Invalid latitude
        
        with pytest.raises(ValueError):
            Location(latitude=35.9, longitude=200)  # Invalid longitude


class TestProperty:
    """Tests for Property model."""

    def test_property_creation(self, sample_property_data):
        """Test creating a Property instance."""
        prop = Property(**sample_property_data)
        assert prop.property_id == "prop_test123"
        assert prop.title == "Beautiful 3-bedroom apartment in Sliema"
        assert prop.price == Decimal("450000")
        assert prop.property_type == PropertyType.APARTMENT

    def test_property_price_range_calculation(self):
        """Test automatic price range calculation."""
        prop = Property(
            property_id="test1",
            title="Test Property",
            property_type=PropertyType.APARTMENT,
            price=Decimal("150000"),
        )
        assert prop.price_range == PriceRange.RANGE_100K_200K

    def test_property_total_area_calculation(self):
        """Test total area calculation from internal and external areas."""
        prop = Property(
            property_id="test1",
            title="Test Property",
            property_type=PropertyType.APARTMENT,
            price=Decimal("300000"),
            internal_area_sqm=Decimal("100"),
            external_area_sqm=Decimal("20"),
        )
        assert prop.total_area_sqm == Decimal("120")

    def test_property_to_dynamodb_item(self, sample_property_data):
        """Test conversion to DynamoDB item format."""
        prop = Property(**sample_property_data)
        item = prop.to_dynamodb_item()
        
        assert "property_id" in item
        assert item["price"] == 450000.0  # Decimal converted to float
        assert item["property_type"] == "apartment"  # Enum converted to string

    def test_property_from_dynamodb_item(self, sample_property_data):
        """Test creation from DynamoDB item format."""
        prop = Property(**sample_property_data)
        item = prop.to_dynamodb_item()
        restored = Property.from_dynamodb_item(item)
        
        assert restored.property_id == prop.property_id
        assert restored.price == prop.price
        assert restored.property_type == prop.property_type


class TestPropertyFilter:
    """Tests for PropertyFilter model."""

    def test_filter_defaults(self):
        """Test default filter values."""
        filter_obj = PropertyFilter()
        assert filter_obj.page == 1
        assert filter_obj.page_size == 20
        assert filter_obj.sort_by == "created_at"
        assert filter_obj.sort_order == "desc"

    def test_filter_validation(self):
        """Test filter validation."""
        with pytest.raises(ValueError):
            PropertyFilter(page=0)  # Page must be >= 1
        
        with pytest.raises(ValueError):
            PropertyFilter(page_size=200)  # Page size must be <= 100


class TestROIAnalysis:
    """Tests for ROIAnalysis model."""

    def test_roi_analysis_creation(self, sample_analysis_data):
        """Test creating an ROIAnalysis instance."""
        analysis = ROIAnalysis(**sample_analysis_data)
        assert analysis.analysis_id == "anl_test456"
        assert analysis.property_id == "prop_test123"
        assert analysis.strategy == InvestmentStrategy.BUY_TO_LET

    def test_roi_calculations(self, sample_analysis_data):
        """Test automatic ROI calculations."""
        analysis = ROIAnalysis(**sample_analysis_data)
        
        # Check that calculations were performed
        assert analysis.down_payment is not None
        assert analysis.total_investment is not None
        assert analysis.cash_flow is not None
        assert analysis.gross_rental_yield is not None
        assert analysis.roi_percentage is not None
        assert analysis.roi_score is not None

    def test_cash_flow_calculation(self, sample_analysis_data):
        """Test cash flow calculation."""
        analysis = ROIAnalysis(**sample_analysis_data)
        
        expected_monthly_income = Decimal("1800") * Decimal("0.90")  # 1620
        expected_monthly_expenses = sum([
            Decimal("1440"),  # mortgage
            Decimal("37.50"),  # tax
            Decimal("75"),  # insurance
            Decimal("375"),  # maintenance
            Decimal("180"),  # management
            Decimal("110"),  # utilities
            Decimal("255"),  # vacancy
        ])
        
        assert analysis.cash_flow.monthly_income == expected_monthly_income
        assert analysis.cash_flow.monthly_expenses == expected_monthly_expenses
        assert analysis.cash_flow.monthly_cash_flow == expected_monthly_income - expected_monthly_expenses

    def test_roi_score_range(self, sample_analysis_data):
        """Test that ROI score is within valid range."""
        analysis = ROIAnalysis(**sample_analysis_data)
        
        assert analysis.roi_score is not None
        assert Decimal("0") <= analysis.roi_score <= Decimal("100")

    def test_recommendation_generation(self, sample_analysis_data):
        """Test that recommendation is generated."""
        analysis = ROIAnalysis(**sample_analysis_data)
        
        assert analysis.recommendation is not None
        assert len(analysis.recommendation) > 0

    def test_to_dynamodb_item(self, sample_analysis_data):
        """Test conversion to DynamoDB item format."""
        analysis = ROIAnalysis(**sample_analysis_data)
        item = analysis.to_dynamodb_item()
        
        assert "analysis_id" in item
        assert isinstance(item["roi_score"], float)  # Decimal converted to float


class TestMonthlyExpenses:
    """Tests for MonthlyExpenses model."""

    def test_total_calculation(self):
        """Test total expenses calculation."""
        expenses = MonthlyExpenses(
            mortgage_payment=Decimal("1000"),
            property_tax=Decimal("50"),
            insurance=Decimal("30"),
        )
        assert expenses.total == Decimal("1080")


class TestRentalIncome:
    """Tests for RentalIncome model."""

    def test_effective_monthly_income(self):
        """Test effective monthly income calculation."""
        income = RentalIncome(
            monthly_rent=Decimal("2000"),
            occupancy_rate=Decimal("0.90"),
        )
        assert income.effective_monthly_income == Decimal("1800")

    def test_annual_income(self):
        """Test annual income calculation."""
        income = RentalIncome(
            monthly_rent=Decimal("2000"),
            occupancy_rate=Decimal("0.90"),
        )
        assert income.annual_income == Decimal("1800") * 12


class TestScraperRun:
    """Tests for ScraperRun model."""

    def test_scraper_run_creation(self):
        """Test creating a ScraperRun instance."""
        run = ScraperRun(
            run_id="scrap_test123",
            sources=[ScraperSource.SIMONESTATES, ScraperSource.FRANKSALT],
            status=ScraperStatus.PENDING,
        )
        assert run.run_id == "scrap_test123"
        assert len(run.sources) == 2
        assert run.status == ScraperStatus.PENDING

    def test_mark_started(self):
        """Test marking a run as started."""
        run = ScraperRun(run_id="test", sources=[])
        run.mark_started()
        
        assert run.status == ScraperStatus.RUNNING
        assert run.started_at is not None

    def test_mark_completed(self):
        """Test marking a run as completed."""
        run = ScraperRun(run_id="test", sources=[])
        run.mark_started()
        run.mark_completed()
        
        assert run.status == ScraperStatus.COMPLETED
        assert run.completed_at is not None
        assert run.duration_seconds is not None

    def test_add_error(self):
        """Test adding an error to a run."""
        run = ScraperRun(run_id="test", sources=[])
        run.add_error("test_source", "Test error", {"detail": "info"})
        
        assert len(run.errors) == 1
        assert run.total_properties_failed == 1
        assert run.errors[0]["source"] == "test_source"


class TestApiResponse:
    """Tests for ApiResponse model."""

    def test_success_response(self):
        """Test successful API response."""
        response = ApiResponse(data={"id": "123"}, message="Success")
        
        assert response.success is True
        assert response.data == {"id": "123"}
        assert response.message == "Success"

    def test_error_response(self):
        """Test error API response."""
        response = ApiResponse(
            success=False,
            error="Something went wrong",
            message="Error occurred",
        )
        
        assert response.success is False
        assert response.error == "Something went wrong"


class TestPaginatedResponse:
    """Tests for PaginatedResponse model."""

    def test_pagination_calculation(self):
        """Test pagination calculations."""
        items = list(range(25))
        response = PaginatedResponse.create(
            items=items[:10],
            total=25,
            page=1,
            page_size=10,
        )
        
        assert response.total == 25
        assert response.page == 1
        assert response.page_size == 10
        assert response.total_pages == 3
        assert response.has_next is True
        assert response.has_prev is False

    def test_last_page(self):
        """Test last page pagination."""
        items = list(range(25))
        response = PaginatedResponse.create(
            items=items[20:],
            total=25,
            page=3,
            page_size=10,
        )
        
        assert response.has_next is False
        assert response.has_prev is True


class TestEnums:
    """Tests for enum models."""

    def test_property_type_values(self):
        """Test PropertyType enum values."""
        assert PropertyType.APARTMENT.value == "apartment"
        assert PropertyType.VILLA.value == "villa"
        assert PropertyType.PENTHOUSE.value == "penthouse"

    def test_property_status_values(self):
        """Test PropertyStatus enum values."""
        assert PropertyStatus.FOR_SALE.value == "for_sale"
        assert PropertyStatus.SOLD.value == "sold"

    def test_investment_strategy_values(self):
        """Test InvestmentStrategy enum values."""
        assert InvestmentStrategy.BUY_TO_LET.value == "buy_to_let"
        assert InvestmentStrategy.FLIP.value == "flip"

    def test_scraper_source_values(self):
        """Test ScraperSource enum values."""
        assert ScraperSource.SIMONESTATES.value == "simonestates"
        assert ScraperSource.FRANKSALT.value == "franksalt"
