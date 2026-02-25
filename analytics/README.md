# Malta Property Investment Analytics Engine

A comprehensive ROI analysis engine for evaluating property investment opportunities in Malta.

## Features

- **Malta-Specific Calculations**: Accurate stamp duty, notary fees, and market data for Malta
- **Complete Financial Modeling**: Cap rate, cash-on-cash return, IRR, and 10-year projections
- **Cash Flow Analysis**: Detailed operating expense breakdowns and cash flow projections
- **Opportunity Scoring**: 0-100 scoring system with risk classification
- **Pure, Testable Functions**: All calculations are pure functions with 90%+ test coverage

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd malta-property-analyzer/analytics

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Quick Start

```python
from decimal import Decimal
from src.models.investment import InvestmentScenario
from src.calculators.roi_calculator import analyze_investment

# Create an investment scenario
scenario = InvestmentScenario(
    property_price=Decimal("300000"),      # €300,000 property
    monthly_rent=Decimal("1200"),          # €1,200/month rent
    property_area="sliema",                 # Location in Malta
    down_payment_percent=Decimal("0.20"),  # 20% down payment
    loan_interest_rate=Decimal("0.035"),   # 3.5% interest rate
    loan_term_years=25,
    vacancy_rate=Decimal("0.05"),          # 5% vacancy
    annual_appreciation=Decimal("0.03"),   # 3% annual appreciation
)

# Analyze the investment
analysis, costs, cash_flow = analyze_investment(scenario, property_id="PROP-001")

# View results
print(f"Cap Rate: {analysis.cap_rate * 100:.2f}%")
print(f"Cash-on-Cash Return: {analysis.cash_on_cash_return * 100:.2f}%")
print(f"Monthly Cash Flow: €{analysis.monthly_cash_flow}")
print(f"Opportunity Score: {analysis.opportunity_score}/100")
print(f"Recommendation: {analysis.recommendation}")
```

## Key Financial Metrics

### Capitalization Rate (Cap Rate)
```
Cap Rate = Net Operating Income / Purchase Price
```
The unlevered return on a property, useful for comparing properties regardless of financing.

### Cash-on-Cash Return
```
Cash-on-Cash = Annual Cash Flow / Cash Invested
```
The return on actual cash invested, accounting for leverage from financing.

### Price-to-Rent Ratio
```
Price-to-Rent = Property Price / Annual Rent
```
- Under 15: Potentially good for buying
- 15-20: Neutral
- Over 20: Potentially better to rent

### Net Operating Income (NOI)
```
NOI = Effective Gross Income - Operating Expenses
```

### Internal Rate of Return (IRR)
The discount rate that makes NPV of all cash flows equal to zero.

## Malta-Specific Purchase Costs

### First-Time Buyers
- **Stamp Duty**: 3.5% on first €150,000, 5% on remainder
- **Notary Fees**: ~1.5%
- **Registration Fees**: ~1%

### Second/Subsequent Property
- **Stamp Duty**: 5% flat rate
- **Notary Fees**: ~1.5%
- **Registration Fees**: ~1%

### Example Purchase Costs (€300,000 property)

| Cost Type | First-Time Buyer | Second-Time Buyer |
|-----------|------------------|-------------------|
| Stamp Duty | €12,750 | €15,000 |
| Notary Fees | €4,500 | €4,500 |
| Registration | €3,000 | €3,000 |
| **Total** | **€20,250** | **€22,500** |

## Operating Expenses

| Expense | % of Income | Notes |
|---------|-------------|-------|
| Property Management | 10% | Typical range 8-12% |
| Maintenance Reserve | 5% | Annual repair budget |
| Insurance | 0.3% | Of property value annually |
| Property Tax | 0% | Malta has no property tax |

## Opportunity Scoring

Properties are scored 0-100 based on:

| Factor | Weight | Description |
|--------|--------|-------------|
| Cash-on-Cash Return | 30% | Most important metric |
| Cap Rate | 25% | Unlevered return |
| Cash Flow | 20% | Monthly cash flow positivity |
| Location | 15% | Area desirability |
| Price-to-Rent | 10% | Value indicator |

### Score Classifications

| Score | Classification | Recommendation |
|-------|----------------|----------------|
| 80-100 | Excellent | Strong Buy |
| 60-79 | Good | Consider Buying |
| 40-59 | Fair | Worth Considering |
| <40 | Poor | Not Recommended |

### Risk Levels

| Level | Criteria |
|-------|----------|
| Low | Score ≥70, positive cash flow, CoC ≥7%, Cap Rate ≥5% |
| Medium | Score 40-69 or mixed signals |
| High | Score <40, negative cash flow, poor returns |

## Rental Yields by Area

| Area | Annual Yield | Desirability |
|------|--------------|--------------|
| Sliema | 4.5% | 95/100 |
| St. Julian's | 4.8% | 93/100 |
| Valletta | 5.0% | 90/100 |
| Gzira | 4.6% | 80/100 |
| Msida | 4.7% | 78/100 |
| Mosta | 5.5% | 70/100 |
| Birkirkara | 5.8% | 68/100 |
| Mellieha | 4.0% | 75/100 |
| Hamrun | 6.0% | 55/100 |

## API Reference

### Models

#### InvestmentScenario
```python
scenario = InvestmentScenario(
    property_price=Decimal("300000"),
    monthly_rent=Decimal("1200"),
    property_area="sliema",
    down_payment_percent=Decimal("0.20"),
    loan_interest_rate=Decimal("0.035"),
    loan_term_years=25,
    vacancy_rate=Decimal("0.05"),
    annual_appreciation=Decimal("0.03"),
)
```

#### ROIAnalysis
Complete analysis result with all metrics:
- `cap_rate`: Capitalization rate
- `cash_on_cash_return`: Cash-on-cash return
- `gross_rental_yield`: Gross rental yield
- `net_rental_yield`: Net rental yield
- `monthly_cash_flow`: Monthly cash flow
- `opportunity_score`: 0-100 score
- `risk_level`: low/medium/high
- `recommendation`: Investment recommendation

### Calculator Functions

#### calculate_purchase_costs
```python
from src.calculators.roi_calculator import calculate_purchase_costs

costs = calculate_purchase_costs(
    property_price=Decimal("300000"),
    is_first_time=True,
    include_agency_fees=False,
)
print(costs.total)  # Total closing costs
```

#### calculate_mortgage_payment
```python
from src.calculators.roi_calculator import calculate_mortgage_payment

payment = calculate_mortgage_payment(
    principal=Decimal("240000"),
    annual_rate=Decimal("0.035"),
    years=25,
)
```

#### calculate_cap_rate
```python
from src.calculators.roi_calculator import calculate_cap_rate

cap_rate = calculate_cap_rate(
    net_operating_income=Decimal("15000"),
    purchase_price=Decimal("300000"),
)
```

#### calculate_cash_on_cash_return
```python
from src.calculators.roi_calculator import calculate_cash_on_cash_return

coc = calculate_cash_on_cash_return(
    annual_cash_flow=Decimal("6000"),
    cash_invested=Decimal("80000"),
)
```

#### project_10_year_returns
```python
from src.calculators.projections import project_10_year_returns

projection = project_10_year_returns(scenario)
print(projection.total_cash_flow)
print(projection.total_appreciation)
print(projection.irr)
```

### Scoring Functions

#### score_opportunity
```python
from src.scoring.opportunity_scorer import score_opportunity

result = score_opportunity(
    cash_on_cash=Decimal("0.085"),
    cap_rate=Decimal("0.055"),
    monthly_cash_flow=Decimal("350"),
    area="sliema",
    price_to_rent=Decimal("18"),
)

print(result['score'])           # Overall score
print(result['risk_level'])      # low/medium/high
print(result['recommendation'])  # Investment recommendation
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_roi_calculator.py

# Run with verbose output
pytest -v
```

### Test Coverage

- ROI Calculator: 95%+
- Cash Flow: 95%+
- Projections: 90%+
- Rental Yield: 95%+
- Opportunity Scorer: 95%+
- Malta Market Data: 90%+
- Models: 90%+

## Project Structure

```
analytics/
├── pyproject.toml          # Project configuration
├── pytest.ini              # Test configuration
├── README.md               # This file
├── src/
│   ├── __init__.py
│   ├── calculators/        # Financial calculators
│   │   ├── roi_calculator.py
│   │   ├── rental_yield.py
│   │   ├── cash_flow.py
│   │   └── projections.py
│   ├── models/             # Pydantic models
│   │   ├── investment.py
│   │   ├── analysis.py
│   │   └── market_data.py
│   ├── data/               # Malta market data
│   │   └── malta_market.py
│   └── scoring/            # Opportunity scoring
│       └── opportunity_scorer.py
└── tests/
    ├── conftest.py         # Test fixtures
    └── unit/               # Unit tests
        ├── test_roi_calculator.py
        ├── test_rental_yield.py
        ├── test_cash_flow.py
        ├── test_projections.py
        ├── test_opportunity_scorer.py
        ├── test_malta_market.py
        └── test_models.py
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Disclaimer

This tool is for educational and analytical purposes only. It does not constitute financial advice. Always consult with qualified financial advisors and conduct thorough due diligence before making investment decisions.
