# Contributing to Malta Property Investment Analyzer

Thank you for your interest in contributing to the Malta Property Investment Analyzer project! This document provides comprehensive guidelines for contributing to ensure code quality, consistency, and maintainability.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Git Workflow](#git-workflow)
- [Pull Request Process](#pull-request-process)
- [Issue Tracking](#issue-tracking)
- [Code Review Guidelines](#code-review-guidelines)
- [CI/CD Requirements](#cicd-requirements)
- [Documentation Standards](#documentation-standards)
- [Communication](#communication)
- [Questions?](#questions)

## 📜 Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow:

- Be respectful and inclusive in all interactions
- Provide constructive feedback
- Focus on what is best for the project and community
- Show empathy towards other community members
- Accept responsibility and apologize when mistakes are made

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+** (for backend, scraper, analytics)
- **Node.js 18+** (for frontend)
- **AWS CLI** configured (for backend deployment)
- **SAM CLI** (for local backend development)
- **Git** (for version control)

### Repository Setup

```bash
# Clone the repository
git clone git@github.com:villaApps/mark-re2.git
cd mark-re2

# Set up pre-commit hooks
pip install pre-commit
pre-commit install

# Install backend dependencies
cd backend
pip install -e ".[dev]"

# Install frontend dependencies
cd ../frontend
npm install

# Install scraper dependencies
cd ../scraper
pip install -e ".[dev]"

# Install analytics dependencies
cd ../analytics
pip install -e ".[dev]"
```

### Local Development

```bash
# Start all services with Docker Compose
docker-compose up

# Or start services individually:

# Backend (SAM local)
cd backend
sam build
sam local start-api

# Frontend (Next.js dev server)
cd frontend
npm run dev

# Run tests
cd backend && pytest
cd frontend && npm run test
cd scraper && pytest
cd analytics && pytest
```

## 🔄 Development Workflow

We follow **Test-Driven Development (TDD)** for all features and fixes:

### TDD Cycle

1. **Write a failing test** - Create a test that defines the expected behavior
2. **Run the test** - Confirm it fails (red)
3. **Write minimal implementation** - Just enough to make the test pass
4. **Run the test** - Confirm it passes (green)
5. **Refactor** - Improve code quality while keeping tests green
6. **Repeat** - Continue with next feature/fix

### Example TDD Workflow

```python
# Step 1: Write failing test (test_calculator.py)
def test_add_two_numbers():
    assert add(2, 3) == 5

# Step 2: Run test - FAILS (red)
# pytest test_calculator.py

# Step 3: Write minimal implementation (calculator.py)
def add(a, b):
    return a + b

# Step 4: Run test - PASSES (green)
# pytest test_calculator.py

# Step 5: Refactor if needed
# Improve naming, extract helpers, etc.
```

## 📝 Coding Standards

### Language & Framework Requirements

| Component | Language | Framework | Notes |
|-----------|----------|-----------|-------|
| Backend | Python 3.12+ | AWS SAM, Lambda | Async/await patterns |
| Frontend | TypeScript 5.3+ | Next.js 14+, React | Strict mode enabled |
| Scraper | Python 3.12+ | httpx, BeautifulSoup4 | Async HTTP |
| Analytics | Python 3.12+ | Pydantic v2, numpy | Pure functions |

### Code Quality Standards

#### Python

- **Follow PEP 8** style guide
- **Use type hints** for all function signatures
- **Maximum line length**: 88 characters (Black formatter)
- **Docstrings**: Google style for all public functions
- **Imports**: Grouped (stdlib, third-party, local)

```python
from typing import Optional, List
from decimal import Decimal

import httpx
from pydantic import BaseModel

from src.models.property import Property


def calculate_roi(
    property_price: Decimal,
    monthly_rent: Decimal,
    down_payment_percent: float = 0.20
) -> Decimal:
    """Calculate Return on Investment for a property.
    
    Args:
        property_price: Purchase price in EUR
        monthly_rent: Expected monthly rental income
        down_payment_percent: Down payment as decimal (default 20%)
        
    Returns:
        Annual ROI as a percentage
        
    Example:
        >>> calculate_roi(Decimal('450000'), Decimal('2000'))
        Decimal('5.33')
    """
    annual_rent = monthly_rent * 12
    cash_invested = property_price * Decimal(str(down_payment_percent))
    return (annual_rent / cash_invested) * 100
```

#### TypeScript

- **Enable strict mode** in tsconfig.json
- **Use explicit types** (avoid `any`)
- **Maximum line length**: 100 characters (Prettier)
- **Component props**: Use interfaces
- **Error handling**: Use try/catch with typed errors

```typescript
interface PropertyCardProps {
  property: Property;
  onSelect?: (id: string) => void;
  showRoi?: boolean;
}

export function PropertyCard({ 
  property, 
  onSelect, 
  showRoi = false 
}: PropertyCardProps): JSX.Element {
  const handleClick = () => {
    onSelect?.(property.id);
  };

  return (
    <div 
      className="property-card" 
      onClick={handleClick}
      data-testid="property-card"
    >
      {/* Component JSX */}
    </div>
  );
}
```

### Code Organization

#### Backend (Python)

```
backend/src/
├── handlers/          # Lambda handlers (thin layer)
├── services/          # Business logic (pure functions)
├── models/            # Pydantic models
├── utils/             # Shared utilities
└── tests/
    ├── unit/          # Unit tests (mocked dependencies)
    └── integration/   # Integration tests (real services)
```

#### Frontend (TypeScript)

```
frontend/src/
├── app/               # Next.js App Router pages
├── components/        # React components
│   ├── ui/            # Reusable UI components
│   ├── property/      # Property-specific components
│   ├── roi/           # ROI calculator components
│   └── layout/        # Layout components
├── hooks/             # Custom React hooks
├── lib/               # Utilities and API clients
├── types/             # TypeScript type definitions
└── tests/
    ├── unit/          # Vitest tests
    └── e2e/           # Playwright tests
```

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Functions | snake_case (Python), camelCase (TS) | `calculate_roi`, `calculateRoi` |
| Classes | PascalCase | `PropertyService`, `ROICalculator` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| Variables | snake_case / camelCase | `property_price`, `propertyPrice` |
| Files | snake_case (Python), kebab-case (TS) | `property_service.py`, `property-card.tsx` |
| Test Files | test_*.py / *.spec.ts | `test_property_service.py`, `property-card.spec.ts` |

## 🧪 Testing Requirements

### Coverage Requirements

All code must maintain **90%+ test coverage**:

```
Overall coverage: 90% minimum
Module coverage: 90% minimum
New code coverage: 95% minimum
```

### Test Types

#### 1. Unit Tests

- Test individual functions/classes in isolation
- Mock all external dependencies
- Fast execution (< 100ms per test)
- Deterministic (no randomness, no time dependencies)

```python
# Example unit test
import pytest
from unittest.mock import Mock, patch

from src.services.property_service import PropertyService


class TestPropertyService:
    """Tests for PropertyService."""
    
    @pytest.fixture
    def service(self):
        return PropertyService()
    
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    def test_get_property_by_id_found(self, service, mock_db):
        """Test retrieving an existing property."""
        # Arrange
        mock_db.get_item.return_value = {
            'Item': {'id': '123', 'title': 'Test Property'}
        }
        service.db = mock_db
        
        # Act
        result = service.get_property_by_id('123')
        
        # Assert
        assert result is not None
        assert result['id'] == '123'
        mock_db.get_item.assert_called_once()
    
    def test_get_property_by_id_not_found(self, service, mock_db):
        """Test retrieving a non-existent property."""
        # Arrange
        mock_db.get_item.return_value = {}
        service.db = mock_db
        
        # Act
        result = service.get_property_by_id('999')
        
        # Assert
        assert result is None
```

#### 2. Integration Tests

- Test component interactions
- Use test databases/containers
- Verify API contracts

```python
# Example integration test
import pytest

class TestPropertiesAPI:
    """Integration tests for Properties API."""
    
    @pytest.fixture
    def api_client(self):
        from src.handlers.properties_api import handler
        return handler
    
    def test_list_properties_success(self, api_client):
        """Test successful property listing."""
        # Arrange
        event = {
            'httpMethod': 'GET',
            'path': '/properties',
            'queryStringParameters': {'limit': '10'}
        }
        
        # Act
        response = api_client(event, {})
        
        # Assert
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'properties' in body
        assert len(body['properties']) <= 10
```

#### 3. E2E Tests (Playwright)

- Test complete user journeys
- Run against real application
- Cover all navigable links/buttons

```typescript
// Example E2E test
import { test, expect } from '@playwright/test';

test.describe('Property Search', () => {
  test('should search and filter properties', async ({ page }) => {
    // Navigate to properties page
    await page.goto('/properties');
    
    // Apply location filter
    await page.getByRole('button', { name: /Filters/i }).click();
    await page.getByLabel(/Location/i).selectOption('sliema');
    
    // Wait for results
    await page.waitForTimeout(500);
    
    // Verify filtered results
    const properties = page.locator('.property-card');
    await expect(properties.first()).toBeVisible();
    
    // Verify all properties show Sliema
    const count = await properties.count();
    for (let i = 0; i < count; i++) {
      const location = await properties.nth(i).locator('.location').textContent();
      expect(location).toContain('Sliema');
    }
  });
});
```

### Running Tests

```bash
# Backend tests with coverage
cd backend
pytest --cov=src --cov-report=term-missing --cov-fail-under=90

# Frontend unit tests
cd frontend
npm run test:coverage

# Frontend E2E tests
cd frontend
npm run test:e2e

# Scraper tests
cd scraper
pytest --cov=src --cov-report=term-missing --cov-fail-under=90

# Analytics tests
cd analytics
pytest --cov=src --cov-report=term-missing --cov-fail-under=90

# All tests
make test
```

### Test Isolation

Tests must be **deterministic and isolated**:

- ✅ No shared state between tests
- ✅ No dependencies on environment variables
- ✅ No time-based assertions (use frozen time)
- ✅ No network calls (mock all HTTP)
- ✅ Clean up after each test

```python
# Bad: Time-dependent test
def test_daily_report():
    report = generate_daily_report()  # Fails at midnight!
    assert report.date == date.today()

# Good: Time-independent test
from freezegun import freeze_time

@freeze_time("2024-01-15")
def test_daily_report():
    report = generate_daily_report()
    assert report.date == date(2024, 1, 15)
```

## 🌿 Git Workflow

### Branch Naming

All work must be done on feature branches with specific prefixes:

| Type | Prefix | Example |
|------|--------|---------|
| Feature | `feat/` | `feat/add-user-authentication` |
| Bug Fix | `fix/` | `fix/roi-calculation-error` |
| Documentation | `docs/` | `docs/update-api-reference` |
| Refactoring | `refactor/` | `refactor/property-service` |
| Performance | `perf/` | `perf/optimize-queries` |
| Testing | `test/` | `test/add-missing-tests` |
| Chore | `chore/` | `chore/update-dependencies` |

### Creating a Branch

```bash
# Start from latest main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feat/add-opportunity-alerts

# Make changes, commit, push
git add .
git commit -m "feat: add email alerts for high-opportunity properties"
git push origin feat/add-opportunity-alerts
```

### Conventional Commits

All commits must follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, semicolons)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, etc.

**Examples:**

```bash
# Simple commit
git commit -m "feat: add user authentication"

# Commit with scope
git commit -m "feat(api): add rate limiting to properties endpoint"

# Commit with body
git commit -m "fix(scraper): handle timeout errors from Simon Estates

Add retry logic with exponential backoff for network timeouts.
Increases max retries from 3 to 5."

# Commit with breaking change
git commit -m "feat(api)!: change property ID format

BREAKING CHANGE: Property IDs now use UUID format instead of sequential integers."

# Commit referencing issue
git commit -m "fix: correct ROI calculation for rental properties

Closes #123"
```

### Commit Best Practices

- ✅ Commit early and often
- ✅ Each commit should be a logical unit
- ✅ Write clear, descriptive messages
- ✅ Reference issues in commits (`Closes #123`)
- ❌ Don't commit broken code
- ❌ Don't commit large binary files
- ❌ Don't mix unrelated changes

## 🔀 Pull Request Process

### Creating a Pull Request

1. **Push your branch** to GitHub
2. **Create PR** with detailed description
3. **Link to issue** (`Closes #123`)
4. **Request review** from at least one team member
5. **Ensure CI passes** before requesting review

### PR Title Format

```
<type>: <description>

Examples:
feat: add email alerts for high-opportunity properties
fix: correct cash-on-cash calculation for rental yields
docs: update API reference with new endpoints
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking)
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Related Issues
Closes #123

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] E2E tests added/updated
- [ ] All tests pass locally
- [ ] Coverage >= 90%

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No console errors
- [ ] Mobile responsive (if UI changes)

## Screenshots (if UI changes)
[Add screenshots here]

## Additional Notes
[Any additional context]
```

### PR Review Requirements

- **At least one approval** required before merge
- **All CI checks must pass**
- **No merge conflicts**
- **Branch must be up to date** with main
- **All conversations resolved**

### Merging

- Use **"Squash and merge"** for feature branches
- Use **"Rebase and merge"** for long-running branches
- Delete branch after merge

## 📋 Issue Tracking

### Creating Issues

All work must be tracked as GitHub Issues with clear labels:

**Labels:**
- `type:feature` - New functionality
- `type:bug` - Bug report
- `type:task` - General task
- `type:docs` - Documentation
- `priority:high` - Critical
- `priority:medium` - Important
- `priority:low` - Nice to have
- `status:in-progress` - Currently being worked on
- `status:review` - Ready for review

### Issue Template

```markdown
## Description
Clear description of the task/bug/feature

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Details
[Any technical notes, implementation hints]

## Related
- Related to #456
- Blocked by #789

## Priority
High / Medium / Low

## Estimated Effort
Small / Medium / Large
```

### Linking PRs to Issues

Always link PRs to issues using GitHub keywords:

```markdown
Closes #123
Fixes #456
Resolves #789

Related to #101 (doesn't close)
```

## 👀 Code Review Guidelines

### For Authors

- **Keep PRs small** (< 400 lines when possible)
- **Write clear descriptions** explaining what and why
- **Respond to feedback** promptly and respectfully
- **Test thoroughly** before requesting review
- **Be open to suggestions**

### For Reviewers

- **Review within 24 hours** when possible
- **Be constructive** in feedback
- **Ask questions** if something is unclear
- **Approve when satisfied** (don't just "LGTM")
- **Check**:
  - Code quality and readability
  - Test coverage (90%+)
  - Adherence to standards
  - Performance implications
  - Security considerations
  - Documentation updates

### Review Checklist

```markdown
## Code Review Checklist

### Functionality
- [ ] Code works as expected
- [ ] Edge cases handled
- [ ] Error handling implemented
- [ ] No obvious bugs

### Quality
- [ ] Code is readable and maintainable
- [ ] Naming is clear and consistent
- [ ] No code duplication
- [ ] Functions are focused and small

### Testing
- [ ] Tests cover new code
- [ ] Tests are meaningful (not just for coverage)
- [ ] Edge cases tested
- [ ] All tests pass

### Standards
- [ ] Follows style guidelines
- [ ] Type hints/types used correctly
- [ ] Documentation updated
- [ ] No linting errors

### Performance
- [ ] No obvious performance issues
- [ ] Database queries optimized
- [ ] No N+1 queries
- [ ] Caching considered

### Security
- [ ] No SQL injection vulnerabilities
- [ ] Input validation implemented
- [ ] Secrets not exposed
- [ ] XSS prevention in place
```

## 🔄 CI/CD Requirements

### Continuous Integration

All PRs must pass CI checks before merge:

**Backend CI** (`ci-backend.yml`):
- ✅ Code formatting (Black)
- ✅ Linting (ruff)
- ✅ Type checking (mypy)
- ✅ Unit tests (pytest)
- ✅ Coverage >= 90%
- ✅ Security scan (bandit)
- ✅ SAM template validation

**Frontend CI** (`ci-frontend.yml`):
- ✅ Linting (ESLint)
- ✅ Formatting (Prettier)
- ✅ Type checking (TypeScript)
- ✅ Unit tests (Vitest)
- ✅ Coverage >= 90%
- ✅ Build verification
- ✅ E2E tests (Playwright)

### Pre-commit Hooks

Install pre-commit hooks to catch issues early:

```bash
pip install pre-commit
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

**Configured Hooks:**
- Trailing whitespace removal
- End-of-file fixer
- YAML validation
- JSON validation
- Black (Python formatting)
- ruff (Python linting)
- mypy (Python type checking)
- Prettier (TypeScript formatting)
- ESLint (TypeScript linting)
- Commit message validation (conventional commits)

## 📝 Documentation Standards

### Code Documentation

**Python Docstrings** (Google style):

```python
def calculate_mortgage_payment(
    principal: Decimal,
    annual_rate: float,
    years: int
) -> Decimal:
    """Calculate monthly mortgage payment.
    
    Uses the standard amortization formula:
    M = P[r(1+r)^n]/[(1+r)^n-1]
    
    Args:
        principal: Loan amount in EUR
        annual_rate: Annual interest rate (e.g., 0.035 for 3.5%)
        years: Loan term in years
        
    Returns:
        Monthly payment amount
        
    Raises:
        ValueError: If principal, rate, or years is negative
        
    Example:
        >>> calculate_mortgage_payment(Decimal('360000'), 0.035, 25)
        Decimal('1802.37')
    """
```

**TypeScript JSDoc**:

```typescript
/**
 * Calculate Return on Investment (ROI)
 * 
 * @param propertyPrice - Purchase price in EUR
 * @param monthlyRent - Expected monthly rental income
 * @param downPaymentPercent - Down payment percentage (default 20%)
 * @returns Annual ROI as a percentage
 * 
 * @example
 * ```typescript
 * const roi = calculateROI(450000, 2000, 0.20);
 * console.log(roi); // 5.33
 * ```
 */
function calculateROI(
  propertyPrice: number,
  monthlyRent: number,
  downPaymentPercent: number = 0.20
): number {
  // Implementation
}
```

### README Documentation

Each component must have a README with:

1. **Overview** - What this component does
2. **Installation** - How to set up
3. **Usage** - Basic usage examples
4. **Testing** - How to run tests
5. **API Reference** - If applicable
6. **Configuration** - Environment variables, etc.

### Architecture Decision Records (ADRs)

For significant architectural decisions, create an ADR:

```markdown
# ADR-001: Use AWS SAM for Serverless Infrastructure

## Status
Accepted

## Context
We need to deploy serverless functions with infrastructure as code.

## Decision
Use AWS SAM (Serverless Application Model) for:
- Lambda function deployment
- API Gateway configuration
- DynamoDB table definitions
- EventBridge rules

## Consequences
Positive:
- Infrastructure as code
- Local testing with SAM CLI
- Simplified deployment

Negative:
- AWS vendor lock-in
- Learning curve for team
```

## 💬 Communication

### Communication Channels

- **GitHub Issues** - Bug reports, feature requests, tasks
- **GitHub Discussions** - General questions, ideas
- **Pull Request Comments** - Code-specific discussions
- **Email** - Sensitive or private matters

### Communication Guidelines

- **Be respectful** and professional
- **Provide context** when asking questions
- **Use @mentions** to notify specific people
- **Keep discussions focused** on the topic
- **Summarize decisions** in issues/PRs
- **Update issues** with progress

### Asking Questions

When asking for help:

1. **Search first** - Check existing issues/docs
2. **Provide context** - What are you trying to do?
3. **Show what you've tried** - Code examples, error messages
4. **Be specific** - "X doesn't work" → "X fails with error Y when Z"
5. **Be patient** - Maintainers are volunteers

Good example:

```markdown
I'm trying to add a new property scraper for Frank Salt Real Estate.

I've created `frank_salt.py` following the pattern in `simon_estates.py`,
but I'm getting a `ParseError` when extracting the price.

Here's my code:
[code snippet]

The HTML structure looks like this:
[HTML snippet]

Error message:
```
ParseError: Could not parse price from €450,000
```

I've tried using different regex patterns, but none seem to work.
Any suggestions?
```

## ❓ Questions?

If you have questions not covered in this guide:

1. Check existing [GitHub Issues](https://github.com/villaApps/mark-re2/issues)
2. Search [GitHub Discussions](https://github.com/villaApps/mark-re2/discussions)
3. Create a new issue with the `type:question` label
4. Email the maintainers (for sensitive topics)

## 🙏 Thank You!

Thank you for contributing to the Malta Property Investment Analyzer project!
Your efforts help make property investment analysis accessible to everyone.

---

**Last Updated**: 2024-02-25
**Maintainers**: [List of maintainers]
**License**: MIT
