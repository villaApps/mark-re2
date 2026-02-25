"""
Unit tests for opportunity scorer.

Tests the scoring algorithm and all scoring components.
"""

from decimal import Decimal
import pytest

from src.scoring.opportunity_scorer import (
    _score_cash_flow,
    _score_cap_rate,
    _score_dscr,
    _score_grm,
    _score_cash_on_cash,
    score_opportunity,
    get_score_interpretation,
)


class TestCashFlowScore:
    """Tests for cash flow scoring."""
    
    def test_negative_cash_flow(self):
        """Negative cash flow gets low score."""
        score = _score_cash_flow(Decimal("-500"))
        assert score >= 0
        assert score < 40
    
    def test_zero_cash_flow(self):
        """Zero cash flow gets moderate score."""
        score = _score_cash_flow(Decimal("0"))
        assert score == 40
    
    def test_small_positive_cash_flow(self):
        """Small positive cash flow gets decent score."""
        score = _score_cash_flow(Decimal("100"))
        assert score > 40
        assert score < 60
    
    def test_good_cash_flow(self):
        """Good cash flow (€300-500) gets good score."""
        score = _score_cash_flow(Decimal("400"))
        assert score >= 60
        assert score < 80
    
    def test_excellent_cash_flow(self):
        """Excellent cash flow (€500-1000) gets high score."""
        score = _score_cash_flow(Decimal("750"))
        assert score >= 80
        assert score < 95
    
    def test_exceptional_cash_flow(self):
        """Exceptional cash flow (€1000+) gets very high score."""
        score = _score_cash_flow(Decimal("1200"))
        assert score >= 95
        assert score <= 100
    
    def test_very_negative_cash_flow(self):
        """Very negative cash flow gets minimum score."""
        score = _score_cash_flow(Decimal("-2000"))
        assert score == 0


class TestCapRateScore:
    """Tests for cap rate scoring."""
    
    def test_poor_cap_rate(self):
        """Cap rate below 3% gets low score."""
        score = _score_cap_rate(Decimal("0.025"))
        assert score >= 0
        assert score < 30
    
    def test_below_average_cap_rate(self):
        """Cap rate 3-4% gets below average score."""
        score = _score_cap_rate(Decimal("0.035"))
        assert score >= 30
        assert score < 50
    
    def test_average_cap_rate(self):
        """Cap rate 4-5% gets average score."""
        score = _score_cap_rate(Decimal("0.045"))
        assert score >= 50
        assert score < 70
    
    def test_good_cap_rate(self):
        """Cap rate 5-6% gets good score."""
        score = _score_cap_rate(Decimal("0.055"))
        assert score >= 70
        assert score < 85
    
    def test_excellent_cap_rate(self):
        """Cap rate 6-8% gets excellent score."""
        score = _score_cap_rate(Decimal("0.07"))
        assert score >= 85
        assert score < 95
    
    def test_exceptional_cap_rate(self):
        """Cap rate above 8% gets exceptional score."""
        score = _score_cap_rate(Decimal("0.10"))
        assert score >= 95
        assert score <= 100


class TestDSCRScore:
    """Tests for DSCR scoring."""
    
    def test_dangerous_dscr(self):
        """DSCR below 1.0 gets very low score."""
        score = _score_dscr(Decimal("0.8"))
        assert score >= 0
        assert score < 20
    
    def test_risky_dscr(self):
        """DSCR 1.0-1.1 gets low score."""
        score = _score_dscr(Decimal("1.05"))
        assert score >= 20
        assert score < 40
    
    def test_acceptable_dscr(self):
        """DSCR 1.1-1.25 gets acceptable score."""
        score = _score_dscr(Decimal("1.15"))
        assert score >= 40
        assert score < 60
    
    def test_good_dscr(self):
        """DSCR 1.25-1.5 gets good score."""
        score = _score_dscr(Decimal("1.35"))
        assert score >= 60
        assert score < 80
    
    def test_excellent_dscr(self):
        """DSCR 1.5-2.0 gets excellent score."""
        score = _score_dscr(Decimal("1.75"))
        assert score >= 80
        assert score < 95
    
    def test_exceptional_dscr(self):
        """DSCR above 2.0 gets exceptional score."""
        score = _score_dscr(Decimal("2.5"))
        assert score >= 95
        assert score <= 100


class TestGRMScore:
    """Tests for GRM scoring."""
    
    def test_poor_grm(self):
        """GRM above 25 gets low score."""
        score = _score_grm(Decimal("30"))
        assert score >= 0
        assert score < 30
    
    def test_below_average_grm(self):
        """GRM 20-25 gets below average score."""
        score = _score_grm(Decimal("22"))
        assert score >= 30
        assert score < 50
    
    def test_average_grm(self):
        """GRM 15-20 gets average score."""
        score = _score_grm(Decimal("17"))
        assert score >= 50
        assert score < 70
    
    def test_good_grm(self):
        """GRM 12-15 gets good score."""
        score = _score_grm(Decimal("13"))
        assert score >= 70
        assert score < 85
    
    def test_excellent_grm(self):
        """GRM 10-12 gets excellent score."""
        score = _score_grm(Decimal("11"))
        assert score >= 85
        assert score < 95
    
    def test_exceptional_grm(self):
        """GRM below 10 gets exceptional score."""
        score = _score_grm(Decimal("8"))
        assert score >= 95
        assert score <= 100


class TestCashOnCashScore:
    """Tests for cash-on-cash return scoring."""
    
    def test_negative_coc(self):
        """Negative CoC gets low score."""
        score = _score_cash_on_cash(Decimal("-0.05"))
        assert score >= 0
        assert score < 30
    
    def test_zero_coc(self):
        """Zero CoC gets moderate score."""
        score = _score_cash_on_cash(Decimal("0"))
        assert score == 30
    
    def test_poor_coc(self):
        """CoC 0-4% gets below average score."""
        score = _score_cash_on_cash(Decimal("0.02"))
        assert score >= 30
        assert score < 50
    
    def test_average_coc(self):
        """CoC 4-7% gets average score."""
        score = _score_cash_on_cash(Decimal("0.055"))
        assert score >= 50
        assert score < 70
    
    def test_good_coc(self):
        """CoC 7-10% gets good score."""
        score = _score_cash_on_cash(Decimal("0.085"))
        assert score >= 70
        assert score < 85
    
    def test_excellent_coc(self):
        """CoC 10-15% gets excellent score."""
        score = _score_cash_on_cash(Decimal("0.12"))
        assert score >= 85
        assert score < 95
    
    def test_exceptional_coc(self):
        """CoC above 15% gets exceptional score."""
        score = _score_cash_on_cash(Decimal("0.20"))
        assert score >= 95
        assert score <= 100


class TestOverallScore:
    """Tests for overall opportunity scoring."""
    
    def test_perfect_score(self):
        """Perfect metrics should yield high score."""
        score, breakdown = score_opportunity(
            cap_rate=Decimal("0.10"),
            cash_on_cash=Decimal("0.20"),
            monthly_cash_flow=Decimal("2000"),
            debt_coverage_ratio=Decimal("3.0"),
            gross_rent_multiplier=Decimal("8"),
        )
        
        assert score >= 90
        assert score <= 100
        assert len(breakdown) == 5
    
    def test_poor_score(self):
        """Poor metrics should yield low score."""
        score, breakdown = score_opportunity(
            cap_rate=Decimal("0.02"),
            cash_on_cash=Decimal("-0.10"),
            monthly_cash_flow=Decimal("-500"),
            debt_coverage_ratio=Decimal("0.8"),
            gross_rent_multiplier=Decimal("30"),
        )
        
        assert score >= 0
        assert score < 40
    
    def test_average_score(self):
        """Average metrics should yield moderate score."""
        score, breakdown = score_opportunity(
            cap_rate=Decimal("0.05"),
            cash_on_cash=Decimal("0.06"),
            monthly_cash_flow=Decimal("300"),
            debt_coverage_ratio=Decimal("1.3"),
            gross_rent_multiplier=Decimal("16"),
        )
        
        assert score >= 50
        assert score < 70
    
    def test_score_bounds(self):
        """Score should always be between 0 and 100."""
        test_cases = [
            (Decimal("0.15"), Decimal("0.30"), Decimal("5000"), Decimal("5.0"), Decimal("5")),
            (Decimal("0.01"), Decimal("-0.50"), Decimal("-5000"), Decimal("0.5"), Decimal("50")),
            (Decimal("0.08"), Decimal("0.15"), Decimal("1500"), Decimal("2.0"), Decimal("10")),
        ]
        
        for cap, coc, cf, dscr, grm in test_cases:
            score, _ = score_opportunity(cap, coc, cf, dscr, grm)
            assert 0 <= score <= 100
    
    def test_score_breakdown_structure(self):
        """Score breakdown should contain all components."""
        score, breakdown = score_opportunity(
            cap_rate=Decimal("0.055"),
            cash_on_cash=Decimal("0.08"),
            monthly_cash_flow=Decimal("500"),
            debt_coverage_ratio=Decimal("1.5"),
            gross_rent_multiplier=Decimal("15"),
        )
        
        expected_keys = ["cash_flow", "cap_rate", "dscr", "cash_on_cash", "grm"]
        for key in expected_keys:
            assert key in breakdown
            assert 0 <= breakdown[key] <= 100


class TestScoreInterpretation:
    """Tests for score interpretation."""
    
    def test_exceptional_interpretation(self):
        """Score 90+ gets exceptional interpretation."""
        text = get_score_interpretation(95)
        assert "Exceptional" in text or "exceptional" in text
    
    def test_excellent_interpretation(self):
        """Score 80-90 gets excellent interpretation."""
        text = get_score_interpretation(85)
        assert "Excellent" in text or "excellent" in text
    
    def test_good_interpretation(self):
        """Score 70-80 gets good interpretation."""
        text = get_score_interpretation(75)
        assert "Good" in text or "good" in text
    
    def test_fair_interpretation(self):
        """Score 60-70 gets fair interpretation."""
        text = get_score_interpretation(65)
        assert "Fair" in text or "fair" in text
    
    def test_below_average_interpretation(self):
        """Score 50-60 gets below average interpretation."""
        text = get_score_interpretation(55)
        assert "Below average" in text or "below average" in text.lower()
    
    def test_weak_interpretation(self):
        """Score 40-50 gets weak interpretation."""
        text = get_score_interpretation(45)
        assert "Weak" in text or "weak" in text.lower()
    
    def test_poor_interpretation(self):
        """Score below 40 gets poor interpretation."""
        text = get_score_interpretation(30)
        assert "Poor" in text or "poor" in text.lower() or "Avoid" in text
    
    def test_boundary_scores(self):
        """Test boundary scores."""
        assert "Exceptional" in get_score_interpretation(90)
        assert "Excellent" in get_score_interpretation(80)
        assert "Good" in get_score_interpretation(70)
        assert "Fair" in get_score_interpretation(60)
        assert "Below average" in get_score_interpretation(50)
        assert "Weak" in get_score_interpretation(40)
        assert "Poor" in get_score_interpretation(30) or "Avoid" in get_score_interpretation(30)


class TestScoringWeights:
    """Tests to verify scoring weights are applied correctly."""
    
    def test_cash_flow_weight_importance(self):
        """Cash flow should have significant impact on score."""
        # Good metrics except cash flow
        score_bad_cf, _ = score_opportunity(
            cap_rate=Decimal("0.08"),
            cash_on_cash=Decimal("0.10"),
            monthly_cash_flow=Decimal("-500"),  # Negative
            debt_coverage_ratio=Decimal("2.0"),
            gross_rent_multiplier=Decimal("10"),
        )
        
        # Same metrics with good cash flow
        score_good_cf, _ = score_opportunity(
            cap_rate=Decimal("0.08"),
            cash_on_cash=Decimal("0.10"),
            monthly_cash_flow=Decimal("1000"),  # Positive
            debt_coverage_ratio=Decimal("2.0"),
            gross_rent_multiplier=Decimal("10"),
        )
        
        # Good cash flow should significantly improve score
        assert score_good_cf > score_bad_cf + 20
    
    def test_cap_rate_weight_importance(self):
        """Cap rate should have significant impact on score."""
        # Good metrics except cap rate
        score_low_cap, _ = score_opportunity(
            cap_rate=Decimal("0.02"),  # Very low
            cash_on_cash=Decimal("0.10"),
            monthly_cash_flow=Decimal("500"),
            debt_coverage_ratio=Decimal("2.0"),
            gross_rent_multiplier=Decimal("10"),
        )
        
        # Same metrics with good cap rate
        score_high_cap, _ = score_opportunity(
            cap_rate=Decimal("0.08"),  # Good
            cash_on_cash=Decimal("0.10"),
            monthly_cash_flow=Decimal("500"),
            debt_coverage_ratio=Decimal("2.0"),
            gross_rent_multiplier=Decimal("10"),
        )
        
        # Good cap rate should significantly improve score
        assert score_high_cap > score_low_cap + 15
