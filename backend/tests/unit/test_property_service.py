"""Unit tests for PropertyService."""

import pytest
from decimal import Decimal

from src.models.property import Property, PropertyCreate, PropertyFilter, PropertyType, PropertyStatus
from src.services.property_service import PropertyService
from src.utils.errors import NotFoundError


@pytest.mark.unit
class TestPropertyService:
    """Tests for PropertyService."""

    @pytest.fixture
    def service(self, mock_dynamodb):
        """Create a PropertyService instance with mocked DynamoDB."""
        return PropertyService(table_name="properties-test")

    @pytest.fixture
    async def sample_property(self, service, sample_property_data):
        """Create a sample property in the database."""
        create_data = PropertyCreate(**sample_property_data)
        return await service.create_property(create_data)

    @pytest.mark.asyncio
    async def test_create_property(self, service, sample_property_data):
        """Test creating a property."""
        create_data = PropertyCreate(**sample_property_data)
        property_obj = await service.create_property(create_data)
        
        assert property_obj.property_id is not None
        assert property_obj.title == sample_property_data["title"]
        assert property_obj.price == sample_property_data["price"]

    @pytest.mark.asyncio
    async def test_get_property(self, service, sample_property_data):
        """Test getting a property by ID."""
        # Create property first
        create_data = PropertyCreate(**sample_property_data)
        created = await service.create_property(create_data)
        
        # Get the property
        retrieved = await service.get_property(created.property_id)
        
        assert retrieved.property_id == created.property_id
        assert retrieved.title == created.title

    @pytest.mark.asyncio
    async def test_get_property_not_found(self, service):
        """Test getting a non-existent property."""
        with pytest.raises(NotFoundError):
            await service.get_property("non-existent-id")

    @pytest.mark.asyncio
    async def test_list_properties(self, service, sample_property_data):
        """Test listing properties."""
        # Create multiple properties
        for i in range(3):
            data = sample_property_data.copy()
            data["property_id"] = f"prop_test_{i}"
            data["title"] = f"Property {i}"
            create_data = PropertyCreate(**data)
            await service.create_property(create_data)
        
        # List properties
        result = await service.list_properties()
        
        assert result.total >= 3
        assert len(result.items) >= 3

    @pytest.mark.asyncio
    async def test_list_properties_with_filter(self, service, sample_property_data):
        """Test listing properties with filters."""
        # Create property
        create_data = PropertyCreate(**sample_property_data)
        await service.create_property(create_data)
        
        # Filter by property type
        filters = PropertyFilter(property_type=PropertyType.APARTMENT)
        result = await service.list_properties(filters)
        
        assert result.total >= 1

    @pytest.mark.asyncio
    async def test_list_properties_with_price_filter(self, service, sample_property_data):
        """Test listing properties with price filter."""
        # Create property
        create_data = PropertyCreate(**sample_property_data)
        await service.create_property(create_data)
        
        # Filter by price range
        filters = PropertyFilter(min_price=Decimal("400000"), max_price=Decimal("500000"))
        result = await service.list_properties(filters)
        
        assert result.total >= 1
        for prop in result.items:
            assert Decimal("400000") <= prop.price <= Decimal("500000")

    @pytest.mark.asyncio
    async def test_update_property(self, service, sample_property_data):
        """Test updating a property."""
        # Create property
        create_data = PropertyCreate(**sample_property_data)
        created = await service.create_property(create_data)
        
        # Update property
        update_data = {"title": "Updated Title", "price": Decimal("500000")}
        updated = await service.update_property(created.property_id, update_data)
        
        assert updated.title == "Updated Title"
        assert updated.price == Decimal("500000")

    @pytest.mark.asyncio
    async def test_delete_property(self, service, sample_property_data):
        """Test deleting a property."""
        # Create property
        create_data = PropertyCreate(**sample_property_data)
        created = await service.create_property(create_data)
        
        # Delete property
        await service.delete_property(created.property_id)
        
        # Verify deletion
        with pytest.raises(NotFoundError):
            await service.get_property(created.property_id)

    @pytest.mark.asyncio
    async def test_update_roi_score(self, service, sample_property_data):
        """Test updating property ROI score."""
        # Create property
        create_data = PropertyCreate(**sample_property_data)
        created = await service.create_property(create_data)
        
        # Update ROI score
        await service.update_roi_score(created.property_id, Decimal("75.5"))
        
        # Verify update
        updated = await service.get_property(created.property_id)
        assert updated.roi_score == Decimal("75.5")
        assert updated.analysis_count == 1


@pytest.mark.unit
class TestPropertyServicePagination:
    """Tests for PropertyService pagination."""

    @pytest.fixture
    def service(self, mock_dynamodb):
        """Create a PropertyService instance."""
        return PropertyService(table_name="properties-test")

    @pytest.mark.asyncio
    async def test_pagination(self, service, sample_property_data):
        """Test pagination works correctly."""
        # Create multiple properties
        for i in range(25):
            data = sample_property_data.copy()
            data["property_id"] = f"prop_pagination_{i}"
            data["title"] = f"Property {i}"
            data["price"] = Decimal(str(100000 + i * 10000))
            create_data = PropertyCreate(**data)
            await service.create_property(create_data)
        
        # Get first page
        filters = PropertyFilter(page=1, page_size=10)
        result = await service.list_properties(filters)
        
        assert len(result.items) == 10
        assert result.total == 25
        assert result.total_pages == 3
        assert result.has_next is True
        assert result.has_prev is False

    @pytest.mark.asyncio
    async def test_sorting(self, service, sample_property_data):
        """Test property sorting."""
        # Create properties with different prices
        prices = [Decimal("300000"), Decimal("200000"), Decimal("400000")]
        for i, price in enumerate(prices):
            data = sample_property_data.copy()
            data["property_id"] = f"prop_sort_{i}"
            data["price"] = price
            create_data = PropertyCreate(**data)
            await service.create_property(create_data)
        
        # Sort by price ascending
        filters = PropertyFilter(sort_by="price", sort_order="asc")
        result = await service.list_properties(filters)
        
        prices_result = [p.price for p in result.items if "prop_sort_" in p.property_id]
        assert prices_result == sorted(prices_result)
