# Quick Contributor Reference

> 📖 **Full Guide**: See [CONTRIBUTING.md](./CONTRIBUTING.md) for comprehensive documentation.

## 🚀 Quick Start

```bash
# Clone repo
git clone git@github.com:villaApps/mark-re2.git
cd mark-re2

# Install dependencies
cd backend && pip install -e ".[dev]"
cd ../frontend && npm install
cd ../scraper && pip install -e ".[dev]"
cd ../analytics && pip install -e ".[dev]"

# Start development
docker-compose up  # Or start services individually
```

## 🔄 TDD Workflow (Required)

```bash
# 1. Write failing test
# 2. Run test (red)
# 3. Write minimal code
# 4. Run test (green)
# 5. Refactor
# 6. Repeat
```

## 📝 Commit Format

```bash
# Format: type(scope): description
git commit -m "feat(api): add rate limiting"
git commit -m "fix(scraper): handle timeout errors"
git commit -m "docs: update API reference"

# With issue reference
git commit -m "feat: add email alerts

Closes #123"
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

## 🌿 Branch Naming

```bash
# Format: type/description
git checkout -b feat/add-opportunity-alerts
git checkout -b fix/roi-calculation-error
git checkout -b docs/update-readme
```

## 🧪 Testing Requirements

| Module | Coverage | Command |
|--------|----------|---------|
| Backend | 90%+ | `cd backend && pytest --cov=src --cov-fail-under=90` |
| Frontend | 90%+ | `cd frontend && npm run test:coverage` |
| Scraper | 90%+ | `cd scraper && pytest --cov=src --cov-fail-under=90` |
| Analytics | 90%+ | `cd analytics && pytest --cov=src --cov-fail-under=90` |
| E2E | All journeys | `cd frontend && npm run test:e2e` |

## 🔀 Pull Request Checklist

- [ ] Branch from latest `main`
- [ ] Follow TDD (test first)
- [ ] 90%+ coverage maintained
- [ ] All tests pass
- [ ] No linting errors
- [ ] Conventional commits
- [ ] PR linked to issue (`Closes #123`)
- [ ] At least one reviewer approved
- [ ] CI checks pass

## 📋 Issue Labels

| Label | Use For |
|-------|---------|
| `type:feature` | New functionality |
| `type:bug` | Bug reports |
| `type:task` | General tasks |
| `priority:high` | Critical issues |
| `priority:medium` | Important issues |
| `priority:low` | Nice to have |
| `status:in-progress` | Currently working |
| `status:review` | Ready for review |

## 💻 Code Standards

### Python
```python
# Use type hints, max 88 chars, Google docstrings
def calculate_roi(price: Decimal, rent: Decimal) -> Decimal:
    """Calculate ROI.
    
    Args:
        price: Purchase price
        rent: Monthly rent
        
    Returns:
        Annual ROI percentage
    """
    return (rent * 12 / price) * 100
```

### TypeScript
```typescript
// Use strict types, max 100 chars
interface Props {
  property: Property;
  onSelect?: (id: string) => void;
}

export function PropertyCard({ property, onSelect }: Props): JSX.Element {
  return <div>{/* JSX */}</div>;
}
```

## 🎭 E2E Test Coverage

All user journeys must have Playwright tests:

- ✅ Home page navigation
- ✅ Property listing & filtering
- ✅ Property detail viewing
- ✅ ROI calculator
- ✅ Opportunities ranking
- ✅ Market statistics
- ✅ About page
- ✅ Mobile navigation
- ✅ Error handling
- ✅ Accessibility
- ✅ Performance
- ✅ SEO

## 🐛 Debugging

```bash
# Backend
cd backend && pytest -xvs tests/unit/test_specific.py

# Frontend
cd frontend && npm run test -- --grep "test name"

# E2E
cd frontend && npx playwright test --headed --debug

# With logs
docker-compose logs -f backend
```

## 📞 Need Help?

1. Check [GitHub Issues](https://github.com/villaApps/mark-re2/issues)
2. Read [Full Contributing Guide](./CONTRIBUTING.md)
3. Create new issue with `type:question` label

---

**Remember**: Test first, commit often, communicate clearly! 🚀
