"""Integration tests for API handlers."""

import json
import pytest
from decimal import Decimal

from src.models.property import PropertyCreate, PropertyType
from src.services.property_service import PropertyService
from src.services.analysis_service import AnalysisService


@pytest.mark.integration
class TestPropertiesApiIntegration:
    """Integration tests for Properties API."""

    @pytest.fixture
    def property_service(self, mock_dynamodb):
        """Create PropertyService with mocked DynamoDB."""
        return PropertyService(table_name="properties-test")

    @pytest.fixture
    def analysis_service(self, mock_dynamodb):
        """Create AnalysisService with mocked DynamoDB."""
        return AnalysisService(table_name="analysis-test")

    @pytest.fixture
    async def sample_properties(self, property_service, sample_property_data):
        """Create sample properties for testing."""
        properties = []
        for i in range(5):
            data = sample_property_data.copy()
            data["property_id"] = f"prop_int_{i}"
            data["title"] = f"Integration Test Property {i}"
            data["price"] = Decimal(str(300000 + i * 50000))
            prop = await property_service.create_property(PropertyCreate(**data))
            properties.append(prop)
        return properties

    @pytest.mark.asyncio
    async def test_list_properties_integration(
        self, property_service, sample_properties
    ):
        """Test listing properties through service layer."""
        from src.models.property import PropertyFilter
        
        filters = PropertyFilter(page=1, page_size=10)
        result = await property_service.list_properties(filters)
        
        assert result.total >= 5
        assert len(result.items) >= 5

    @pytest.mark.asyncio
    async def test_property_workflow(
        self, property_service, analysis_service, sample_property_data
    ):
        """Test complete property workflow: create, get, analyze."""
        from src.models.analysis import ROIInput, InvestmentStrategy
        
        # Create property
        create_data = PropertyCreate(**sample_property_data)
        property_obj = await property_service.create_property(create_data)
        
        assert property_obj.property_id is not None
        
        # Get property
        retrieved = await property_service.get_property(property_obj.property_id)
        assert retrieved.property_id == property_obj.property_id
        
        # Analyze property
        roi_input = ROIInput(
            property_id=property_obj.property_id,
            strategy=InvestmentStrategy.BUY_TO_LET,
            monthly_rent=Decimal("2000"),
        )
        
        analysis = await analysis_service.calculate_roi(property_obj, roi_input)
        await analysis_service.save_analysis(analysis)
        
        # Update property with ROI score
        await property_service.update_roi_score(
            property_obj.property_id,
            analysis.roi_score or Decimal("0"),
        )
        
        # Verify ROI score was saved
        updated = await property_service.get_property(property_obj.property_id)
        assert updated.roi_score is not None
        assert updated.analysis_count == 1

    @pytest.mark.asyncio
    async def test_filter_by_roi_score(
        self, property_service, analysis_service, sample_property_data
    ):
        """Test filtering properties by ROI score."""
        from src.models.property import PropertyFilter
        from src.models.analysis import ROIInput, InvestmentStrategy
        
        # Create properties with different ROI scores
        for i in range(3):
            data = sample_property_data.copy()
            data["property_id"] = f"prop_roi_{i}"
            data["price"] = Decimal(str(200000 + i * 100000))
            prop = await property_service.create_property(PropertyCreate(**data))
            
            # Analyze with different rents to get different ROI scores
            roi_input = ROIInput(
                property_id=prop.property_id,
                strategy=InvestmentStrategy.BUY_TO_LET,
                monthly_rent=Decimal(str(1500 + i * 500)),
            )
            analysis = await analysis_service.calculate_roi(prop, roi_input)
            await analysis_service.save_analysis(analysis)
            
            await property_service.update_roi_score(
                prop.property_id,
                analysis.roi_score or Decimal("0"),
            )
        
        # Filter by ROI score
        filters = PropertyFilter(min_roi_score=Decimal("30"))
        result = await property_service.list_properties(filters)
        
        # Should return properties with ROI >= 30
        for prop in result.items:
            if prop.roi_score:
                assert prop.roi_score >= Decimal("30")


@pytest.mark.integration
class TestAnalysisIntegration:
    """Integration tests for analysis functionality."""

    @pytest.fixture
    def property_service(self, mock_dynamodb):
        """Create PropertyService."""
        return PropertyService(table_name="properties-test")

    @pytest.fixture
    def analysis_service(self, mock_dynamodb):
        """Create AnalysisService."""
        return AnalysisService(table_name="analysis-test")

    @pytest.mark.asyncio
    async def test_roi_calculation_accuracy(
        self, property_service, analysis_service, sample_property_data
    ):
        """Test ROI calculation accuracy with known values."""
        from src.models.analysis import ROIInput, InvestmentStrategy
        
        # Create a property with known values
        data = sample_property_data.copy()
        data["price"] = Decimal("300000")
        data["internal_area_sqm"] = Decimal("100")
        prop = await property_service.create_property(PropertyCreate(**data))
        
        # Calculate ROI with known parameters
        roi_input = ROIInput(
            property_id=prop.property_id,
            strategy=InvestmentStrategy.BUY_TO_LET,
            down_payment_percentage=Decimal("0.20"),
            interest_rate=Decimal("0.035"),
            loan_term_years=25,
            monthly_rent=Decimal("1500"),
            occupancy_rate=Decimal("0.90"),
        )
        
        analysis = await analysis_service.calculate_roi(prop, roi_input)
        
        # Verify calculations
        assert analysis.down_payment == Decimal("60000")  # 20% of 300k
        assert analysis.loan_amount == Decimal("240000")  # 80% of 300k
        
        # Gross yield: (1500 * 12 * 0.9) / 300000 = 5.4%
        assert analysis.gross_rental_yield is not None
        assert Decimal("4") < analysis.gross_rental_yield < Decimal("7")

    @pytest.mark.asyncio
    async def test_multiple_analyses_per_property(
        self, property_service, analysis_service, sample_property_data
    ):
        """Test creating multiple analyses for the same property."""
        from src.models.analysis import ROIInput, InvestmentStrategy
        
        data = sample_property_data.copy()
        prop = await property_service.create_property(PropertyCreate(**data))
        
        # Create analyses with different strategies
        strategies = [
            InvestmentStrategy.BUY_TO_LET,
            InvestmentStrategy.HOLIDAY_RENTAL,
            InvestmentStrategy.LONG_TERM_RENTAL,
        ]
        
        for strategy in strategies:
            roi_input = ROIInput(
                property_id=prop.property_id,
                strategy=strategy,
                monthly_rent=Decimal("1800"),
            )
            analysis = await analysis_service.calculate_roi(prop, roi_input)
            await analysis_service.save_analysis(analysis)
        
        # Retrieve all analyses
        analyses = await analysis_service.get_analyses_for_property(prop.property_id)
        
        assert len(analyses) == 3


@pytest.mark.integration
class TestStatsIntegration:
    """Integration tests for statistics functionality."""

    @pytest.fixture
    def property_service(self, mock_dynamodb):
        """Create PropertyService."""
        return PropertyService(table_name="properties-test")

    @pytest.fixture
    def stats_service(self, mock_dynamodb):
        """Create StatsService."""
        from src.services.stats_service import StatsService
        return StatsService(table_name="properties-test")

    @pytest.mark.asyncio
    async def test_market_statistics(
        self, property_service, stats_service, sample_property_data
    ):
        """Test generating market statistics."""
        # Create multiple properties
        for i in range(10):
            data = sample_property_data.copy()
            data["property_id"] = f"prop_stats_{i}"
            data["price"] = Decimal(str(250000 + i * 25000))
            data["internal_area_sqm"] = Decimal(str(80 + i * 10))
            await property_service.create_property(PropertyCreate(**data))
        
        # Get statistics
        stats = await stats_service.get_market_statistics()
        
        assert stats["total_properties"] == 10
        assert "price_statistics" in stats
        assert stats["price_statistics"]["average"] > 0
        assert "property_type_distribution" in stats

    @pytest.mark.asyncio
    async def test_location_statistics(
        self, property_service, stats_service, sample_property_data
    ):
        """Test generating location-specific statistics."""
        # Create properties in different locations
        locations = ["Sliema", "St Julians", "Valletta"]
        for i, location in enumerate(locations):
            data = sample_property_data.copy()
            data["property_id"] = f"prop_loc_{i}"
            data["town"] = location
            data["price"] = Decimal(str(300000 + i * 50000))
            await property_service.create_property(PropertyCreate(**data))
        
        # Get statistics for specific location
        stats = await stats_service.get_location_statistics("Sliema")
        
        assert stats["location"] == "Sliema"
        assert stats["total_properties"] >= 1
