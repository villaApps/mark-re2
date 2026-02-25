"""Tests for opportunity scorer functions."""

from decimal import Decimal

import pytest

from src.scoring.opportunity_scorer import (
    calculate_cash_flow_score,
    calculate_cash_on_cash_score,
    calculate_cap_rate_score,
    calculate_location_score,
    calculate_price_to_rent_score,
    classify_risk_level,
    get_recommendation,
    score_opportunity,
)


class TestCalculateCashOnCashScore:
    """Tests for calculate_cash_on_cash_score function."""
    
    def test_excellent_return(self):
        """Test excellent cash-on-cash return (10%+)."""
        score = calculate_cash_on_cash_score(Decimal("0.12"))
        assert score == 100.0
    
    def test_good_return(self):
        """Test good cash-on-cash return (7-10%)."""
        score = calculate_cash_on_cash_score(Decimal("0.085"))
        assert score > 80.0
        assert score < 100.0
    
    def test_fair_return(self):
        """Test fair cash-on-cash return (5-7%)."""
        score = calculate_cash_on_cash_score(Decimal("0.06"))
        assert score > 60.0
        assert score < 80.0
    
    def test_poor_return(self):
        """Test poor cash-on-cash return (3-5%)."""
        score = calculate_cash_on_cash_score(Decimal("0.04"))
        assert score > 40.0
        assert score < 60.0
    
    def test_very_poor_return(self):
        """Test very poor cash-on-cash return (<3%)."""
        score = calculate_cash_on_cash_score(Decimal("0.02"))
        assert score > 0.0
        assert score < 40.0
    
    def test_zero_return(self):
        """Test zero cash-on-cash return."""
        score = calculate_cash_on_cash_score(Decimal("0"))
        assert score == 0.0
    
    def test_negative_return(self):
        """Test negative cash-on-cash return."""
        score = calculate_cash_on_cash_score(Decimal("-0.05"))
        assert score == 0.0


class TestCalculateCapRateScore:
    """Tests for calculate_cap_rate_score function."""
    
    def test_excellent_cap_rate(self):
        """Test excellent cap rate (7%+)."""
        score = calculate_cap_rate_score(Decimal("0.08"))
        assert score == 100.0
    
    def test_good_cap_rate(self):
        """Test good cap rate (5.5-7%)."""
        score = calculate_cap_rate_score(Decimal("0.06"))
        assert score > 80.0
        assert score < 100.0
    
    def test_fair_cap_rate(self):
        """Test fair cap rate (4.5-5.5%)."""
        score = calculate_cap_rate_score(Decimal("0.05"))
        assert score > 60.0
        assert score < 80.0
    
    def test_poor_cap_rate(self):
        """Test poor cap rate (3.5-4.5%)."""
        score = calculate_cap_rate_score(Decimal("0.04"))
        assert score > 40.0
        assert score < 60.0
    
    def test_zero_cap_rate(self):
        """Test zero cap rate."""
        score = calculate_cap_rate_score(Decimal("0"))
        assert score == 0.0


class TestCalculateCashFlowScore:
    """Tests for calculate_cash_flow_score function."""
    
    def test_excellent_cash_flow(self):
        """Test excellent cash flow (€500+/month)."""
        score = calculate_cash_flow_score(Decimal("600"))
        assert score == 100.0
    
    def test_good_cash_flow(self):
        """Test good cash flow (€200-500/month)."""
        score = calculate_cash_flow_score(Decimal("350"))
        assert score > 80.0
        assert score < 100.0
    
    def test_fair_cash_flow(self):
        """Test fair cash flow (€0-200/month)."""
        score = calculate_cash_flow_score(Decimal("100"))
        assert score > 60.0
        assert score < 80.0
    
    def test_break_even(self):
        """Test break-even cash flow (€0/month)."""
        score = calculate_cash_flow_score(Decimal("0"))
        assert score == 60.0
    
    def test_slight_negative_cash_flow(self):
        """Test slight negative cash flow (-€200 to €0/month)."""
        score = calculate_cash_flow_score(Decimal("-100"))
        assert score > 40.0
        assert score < 60.0
    
    def test_moderate_negative_cash_flow(self):
        """Test moderate negative cash flow (-€500 to -€200/month)."""
        score = calculate_cash_flow_score(Decimal("-350"))
        assert score > 20.0
        assert score < 40.0
    
    def test_severe_negative_cash_flow(self):
        """Test severe negative cash flow (<-€500/month)."""
        score = calculate_cash_flow_score(Decimal("-600"))
        assert score > 0.0
        assert score < 20.0
    
    def test_extreme_negative_cash_flow(self):
        """Test extreme negative cash flow."""
        score = calculate_cash_flow_score(Decimal("-2000"))
        assert score == 0.0


class TestCalculateLocationScore:
    """Tests for calculate_location_score function."""
    
    def test_prime_location(self):
        """Test prime location (Sliema)."""
        score = calculate_location_score("sliema")
        assert score == 95.0
    
    def test_good_location(self):
        """Test good location (Mosta)."""
        score = calculate_location_score("mosta")
        assert score == 70.0
    
    def test_affordable_location(self):
        """Test affordable location (Hamrun)."""
        score = calculate_location_score("hamrun")
        assert score == 55.0
    
    def test_unknown_location(self):
        """Test unknown location."""
        score = calculate_location_score("unknown_area")
        assert score == 50.0  # Default score
    
    def test_none_location(self):
        """Test None location."""
        score = calculate_location_score(None)
        assert score == 50.0  # Default score
    
    def test_case_insensitive(self):
        """Test case insensitivity."""
        score_lower = calculate_location_score("sliema")
        score_upper = calculate_location_score("SLIEMA")
        score_mixed = calculate_location_score("Sliema")
        
        assert score_lower == score_upper == score_mixed


class TestCalculatePriceToRentScore:
    """Tests for calculate_price_to_rent_score function."""
    
    def test_excellent_ratio(self):
        """Test excellent price-to-rent ratio (<15)."""
        score = calculate_price_to_rent_score(Decimal("12"))
        assert score == 100.0
    
    def test_good_ratio(self):
        """Test good price-to-rent ratio (15-18)."""
        score = calculate_price_to_rent_score(Decimal("16"))
        assert score > 80.0
        assert score < 100.0
    
    def test_fair_ratio(self):
        """Test fair price-to-rent ratio (18-22)."""
        score = calculate_price_to_rent_score(Decimal("20"))
        assert score > 60.0
        assert score < 80.0
    
    def test_poor_ratio(self):
        """Test poor price-to-rent ratio (22-25)."""
        score = calculate_price_to_rent_score(Decimal("23"))
        assert score > 40.0
        assert score < 60.0
    
    def test_very_poor_ratio(self):
        """Test very poor price-to-rent ratio (>25)."""
        score = calculate_price_to_rent_score(Decimal("30"))
        assert score > 0.0
        assert score < 40.0
    
    def test_extreme_ratio(self):
        """Test extreme price-to-rent ratio."""
        score = calculate_price_to_rent_score(Decimal("50"))
        assert score == 0.0


class TestClassifyRiskLevel:
    """Tests for classify_risk_level function."""
    
    def test_low_risk(self):
        """Test low risk classification."""
        risk = classify_risk_level(
            cash_on_cash=Decimal("0.08"),
            cap_rate=Decimal("0.055"),
            monthly_cash_flow=Decimal("300"),
            score=75.0,
        )
        assert risk == "low"
    
    def test_medium_risk_good_metrics(self):
        """Test medium risk with good metrics but lower score."""
        risk = classify_risk_level(
            cash_on_cash=Decimal("0.06"),
            cap_rate=Decimal("0.05"),
            monthly_cash_flow=Decimal("200"),
            score=55.0,
        )
        assert risk == "medium"
    
    def test_medium_risk_mixed_signals(self):
        """Test medium risk with mixed signals."""
        risk = classify_risk_level(
            cash_on_cash=Decimal("0.08"),
            cap_rate=Decimal("0.04"),
            monthly_cash_flow=Decimal("100"),
            score=60.0,
        )
        assert risk == "medium"
    
    def test_high_risk_low_score(self):
        """Test high risk due to low score."""
        risk = classify_risk_level(
            cash_on_cash=Decimal("0.02"),
            cap_rate=Decimal("0.03"),
            monthly_cash_flow=Decimal("-100"),
            score=35.0,
        )
        assert risk == "high"
    
    def test_high_risk_negative_cash_flow(self):
        """Test high risk due to negative cash flow."""
        risk = classify_risk_level(
            cash_on_cash=Decimal("0.03"),
            cap_rate=Decimal("0.04"),
            monthly_cash_flow=Decimal("-300"),
            score=50.0,
        )
        assert risk == "high"


class TestGetRecommendation:
    """Tests for get_recommendation function."""
    
    def test_excellent_opportunity_low_risk(self):
        """Test excellent opportunity with low risk."""
        rec = get_recommendation(85.0, "low")
        assert "Excellent" in rec
        assert "Strong Buy" in rec
    
    def test_excellent_opportunity_medium_risk(self):
        """Test excellent opportunity with medium risk."""
        rec = get_recommendation(85.0, "medium")
        assert "Excellent" in rec
        assert "Moderate Risk" in rec
    
    def test_good_opportunity_low_risk(self):
        """Test good opportunity with low risk."""
        rec = get_recommendation(70.0, "low")
        assert "Good" in rec
        assert "Consider Buying" in rec
    
    def test_good_opportunity_high_risk(self):
        """Test good opportunity with high risk."""
        rec = get_recommendation(70.0, "high")
        assert "Good Metrics" in rec
        assert "Caution" in rec
    
    def test_fair_opportunity(self):
        """Test fair opportunity."""
        rec = get_recommendation(50.0, "medium")
        assert "Fair" in rec
    
    def test_poor_opportunity(self):
        """Test poor opportunity."""
        rec = get_recommendation(30.0, "high")
        assert "Poor" in rec
        assert "Not Recommended" in rec


class TestScoreOpportunity:
    """Tests for score_opportunity function."""
    
    def test_excellent_opportunity(self):
        """Test scoring an excellent opportunity."""
        result = score_opportunity(
            cash_on_cash=Decimal("0.10"),
            cap_rate=Decimal("0.07"),
            monthly_cash_flow=Decimal("500"),
            area="sliema",
            price_to_rent=Decimal("15"),
        )
        
        assert result["score"] >= 80.0
        assert result["risk_level"] == "low"
        assert "Excellent" in result["recommendation"]
        assert "component_scores" in result
        assert "raw_metrics" in result
    
    def test_good_opportunity(self):
        """Test scoring a good opportunity."""
        result = score_opportunity(
            cash_on_cash=Decimal("0.07"),
            cap_rate=Decimal("0.055"),
            monthly_cash_flow=Decimal("250"),
            area="mosta",
            price_to_rent=Decimal("18"),
        )
        
        assert result["score"] >= 60.0
        assert result["score"] < 80.0
        assert "Good" in result["recommendation"]
    
    def test_fair_opportunity(self):
        """Test scoring a fair opportunity."""
        result = score_opportunity(
            cash_on_cash=Decimal("0.04"),
            cap_rate=Decimal("0.045"),
            monthly_cash_flow=Decimal("50"),
            area="hamrun",
            price_to_rent=Decimal("22"),
        )
        
        assert result["score"] >= 40.0
        assert result["score"] < 60.0
        assert "Fair" in result["recommendation"]
    
    def test_poor_opportunity(self):
        """Test scoring a poor opportunity."""
        result = score_opportunity(
            cash_on_cash=Decimal("0.02"),
            cap_rate=Decimal("0.03"),
            monthly_cash_flow=Decimal("-200"),
            area="marsa",
            price_to_rent=Decimal("28"),
        )
        
        assert result["score"] < 40.0
        assert result["risk_level"] == "high"
        assert "Poor" in result["recommendation"]
    
    def test_without_optional_params(self):
        """Test scoring without optional parameters."""
        result = score_opportunity(
            cash_on_cash=Decimal("0.06"),
            cap_rate=Decimal("0.05"),
            monthly_cash_flow=Decimal("200"),
        )
        
        assert result["score"] > 0
        assert "recommendation" in result
        # Should use default location score of 50
        assert result["component_scores"]["location"] == 50.0
    
    def test_component_score_ranges(self):
        """Test that all component scores are within valid range."""
        result = score_opportunity(
            cash_on_cash=Decimal("0.06"),
            cap_rate=Decimal("0.05"),
            monthly_cash_flow=Decimal("200"),
            area="sliema",
            price_to_rent=Decimal("20"),
        )
        
        for component, score in result["component_scores"].items():
            assert 0.0 <= score <= 100.0, f"{component} score {score} out of range"
    
    def test_weights_sum_to_100(self):
        """Verify that the weights in the scorer sum to 1.0."""
        from src.scoring.opportunity_scorer import WEIGHTS
        
        total_weight = sum(WEIGHTS.values())
        assert abs(total_weight - 1.0) < 0.001, f"Weights sum to {total_weight}, not 1.0"
