"""Unit tests for AnalysisService."""

import pytest
from decimal import Decimal

from src.models.property import Property, PropertyCreate, PropertyType
from src.models.analysis import (
    ROIAnalysis,
    ROIInput,
    OpportunityFilter,
    InvestmentStrategy,
    MonthlyExpenses,
    RentalIncome,
)
from src.services.analysis_service import AnalysisService
from src.services.property_service import PropertyService
from src.utils.errors import NotFoundError


@pytest.mark.unit
class TestAnalysisService:
    """Tests for AnalysisService."""

    @pytest.fixture
    def analysis_service(self, mock_dynamodb):
        """Create an AnalysisService instance."""
        return AnalysisService(table_name="analysis-test")

    @pytest.fixture
    def property_service(self, mock_dynamodb):
        """Create a PropertyService instance."""
        return PropertyService(table_name="properties-test")

    @pytest.fixture
    async def sample_property(self, property_service, sample_property_data):
        """Create a sample property."""
        create_data = PropertyCreate(**sample_property_data)
        return await property_service.create_property(create_data)

    @pytest.mark.asyncio
    async def test_calculate_roi(self, analysis_service, sample_property):
        """Test ROI calculation."""
        roi_input = ROIInput(
            property_id=sample_property.property_id,
            strategy=InvestmentStrategy.BUY_TO_LET,
            down_payment_percentage=Decimal("0.20"),
            interest_rate=Decimal("0.035"),
            loan_term_years=25,
            monthly_rent=Decimal("1800"),
            occupancy_rate=Decimal("0.90"),
        )
        
        analysis = await analysis_service.calculate_roi(sample_property, roi_input)
        
        assert analysis.property_id == sample_property.property_id
        assert analysis.purchase_price == sample_property.price
        assert analysis.roi_score is not None
        assert analysis.cash_flow is not None
        assert analysis.gross_rental_yield is not None

    @pytest.mark.asyncio
    async def test_calculate_roi_with_auto_rent_estimate(
        self, analysis_service, sample_property
    ):
        """Test ROI calculation with automatic rent estimation."""
        roi_input = ROIInput(
            property_id=sample_property.property_id,
            strategy=InvestmentStrategy.BUY_TO_LET,
            monthly_rent=None,  # Will be estimated
        )
        
        analysis = await analysis_service.calculate_roi(sample_property, roi_input)
        
        assert analysis.rental_income.monthly_rent > 0
        assert analysis.roi_score is not None

    @pytest.mark.asyncio
    async def test_save_and_get_analysis(
        self, analysis_service, sample_property
    ):
        """Test saving and retrieving an analysis."""
        # Create and save analysis
        roi_input = ROIInput(
            property_id=sample_property.property_id,
            strategy=InvestmentStrategy.BUY_TO_LET,
            monthly_rent=Decimal("1800"),
        )
        
        analysis = await analysis_service.calculate_roi(sample_property, roi_input)
        saved = await analysis_service.save_analysis(analysis)
        
        # Retrieve analysis
        retrieved = await analysis_service.get_analysis(saved.analysis_id)
        
        assert retrieved.analysis_id == saved.analysis_id
        assert retrieved.property_id == saved.property_id
        assert retrieved.roi_score == saved.roi_score

    @pytest.mark.asyncio
    async def test_get_analysis_not_found(self, analysis_service):
        """Test getting a non-existent analysis."""
        with pytest.raises(NotFoundError):
            await analysis_service.get_analysis("non-existent-id")

    @pytest.mark.asyncio
    async def test_get_analyses_for_property(
        self, analysis_service, sample_property
    ):
        """Test getting all analyses for a property."""
        # Create multiple analyses
        for i in range(3):
            roi_input = ROIInput(
                property_id=sample_property.property_id,
                strategy=InvestmentStrategy.BUY_TO_LET,
                monthly_rent=Decimal(str(1500 + i * 100)),
            )
            analysis = await analysis_service.calculate_roi(sample_property, roi_input)
            await analysis_service.save_analysis(analysis)
        
        # Get analyses
        analyses = await analysis_service.get_analyses_for_property(
            sample_property.property_id
        )
        
        assert len(analyses) == 3

    @pytest.mark.asyncio
    async def test_get_latest_analysis(
        self, analysis_service, sample_property
    ):
        """Test getting the latest analysis for a property."""
        # Create analyses
        for i in range(2):
            roi_input = ROIInput(
                property_id=sample_property.property_id,
                strategy=InvestmentStrategy.BUY_TO_LET,
                monthly_rent=Decimal(str(1500 + i * 100)),
            )
            analysis = await analysis_service.calculate_roi(sample_property, roi_input)
            await analysis_service.save_analysis(analysis)
        
        # Get latest
        latest = await analysis_service.get_latest_analysis(sample_property.property_id)
        
        assert latest is not None
        assert latest.property_id == sample_property.property_id

    @pytest.mark.asyncio
    async def test_get_top_opportunities(
        self, analysis_service, property_service, sample_property_data
    ):
        """Test getting top investment opportunities."""
        # Create multiple properties with analyses
        for i in range(5):
            # Create property
            data = sample_property_data.copy()
            data["property_id"] = f"prop_opp_{i}"
            data["price"] = Decimal(str(300000 + i * 50000))
            prop = await property_service.create_property(PropertyCreate(**data))
            
            # Create analysis with varying ROI scores
            roi_input = ROIInput(
                property_id=prop.property_id,
                strategy=InvestmentStrategy.BUY_TO_LET,
                monthly_rent=Decimal(str(1500 + i * 200)),
            )
            analysis = await analysis_service.calculate_roi(prop, roi_input)
            await analysis_service.save_analysis(analysis)
        
        # Get top opportunities
        filters = OpportunityFilter(min_roi_score=Decimal("0"), limit=10)
        opportunities = await analysis_service.get_top_opportunities(filters)
        
        assert len(opportunities) > 0
        assert len(opportunities) <= 10

    @pytest.mark.asyncio
    async def test_roi_score_calculation_accuracy(self, analysis_service, sample_property):
        """Test that ROI score is calculated correctly."""
        roi_input = ROIInput(
            property_id=sample_property.property_id,
            strategy=InvestmentStrategy.BUY_TO_LET,
            down_payment_percentage=Decimal("0.20"),
            interest_rate=Decimal("0.035"),
            loan_term_years=25,
            monthly_rent=Decimal("2000"),
            occupancy_rate=Decimal("0.95"),
        )
        
        analysis = await analysis_service.calculate_roi(sample_property, roi_input)
        
        # ROI score should be between 0 and 100
        assert Decimal("0") <= analysis.roi_score <= Decimal("100")
        
        # With good rental income, should have positive cash flow
        assert analysis.cash_flow.monthly_cash_flow > 0
        
        # Should have reasonable gross yield
        assert analysis.gross_rental_yield > Decimal("0")


@pytest.mark.unit
class TestMonthlyExpenses:
    """Tests for MonthlyExpenses calculations."""

    def test_total_expenses(self):
        """Test total expenses calculation."""
        expenses = MonthlyExpenses(
            mortgage_payment=Decimal("1000"),
            property_tax=Decimal("50"),
            insurance=Decimal("30"),
            maintenance=Decimal("100"),
            management_fees=Decimal("150"),
            utilities=Decimal("100"),
            vacancy_reserve=Decimal("100"),
        )
        
        expected_total = Decimal("1530")
        assert expenses.total == expected_total


@pytest.mark.unit
class TestRentalIncome:
    """Tests for RentalIncome calculations."""

    def test_effective_income(self):
        """Test effective monthly income with occupancy."""
        income = RentalIncome(
            monthly_rent=Decimal("2000"),
            occupancy_rate=Decimal("0.90"),
        )
        
        assert income.effective_monthly_income == Decimal("1800")
        assert income.annual_income == Decimal("21600")

    def test_annual_income_calculation(self):
        """Test annual income calculation."""
        income = RentalIncome(
            monthly_rent=Decimal("1500"),
            occupancy_rate=Decimal("1.0"),  # 100% occupancy
        )
        
        assert income.annual_income == Decimal("18000")
