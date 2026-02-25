# Development Workflow Diagram

This document provides a visual guide to the development workflow for contributors.

## 🔄 Complete Development Cycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ISSUE CREATION (GitHub)                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Create issue with type:feature/type:bug label                    │   │
│  │  • Add acceptance criteria                                          │   │
│  │  • Assign priority (high/medium/low)                                │   │
│  │  • Link related issues                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      BRANCH CREATION (Local)                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  git checkout main                                                  │   │
│  │  git pull origin main                                               │   │
│  │  git checkout -b feat/issue-123-short-description                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TDD CYCLE (Repeat for each feature)                       │
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │  1. WRITE    │───▶│  2. RUN TEST │───▶│  3. IMPLEMENT│                  │
│  │     TEST     │    │    (RED)     │    │    (GREEN)   │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│         │                                       │                            │
│         │         ┌──────────────┐              │                            │
│         └────────▶│  5. REFACTOR │◀─────────────┘                            │
│                   │ (KEEP GREEN) │                                           │
│                   └──────────────┘                                           │
│                          │                                                   │
│                          ▼                                                   │
│                   ┌──────────────┐                                           │
│                   │  6. REPEAT   │                                           │
│                   │  NEXT TEST   │                                           │
│                   └──────────────┘                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      COMMIT CHANGES (Conventional Commits)                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  git add .                                                          │   │
│  │  git commit -m "feat(scope): description"                           │   │
│  │                                                                     │   │
│  │  Examples:                                                          │   │
│  │  git commit -m "feat(api): add rate limiting"                       │   │
│  │  git commit -m "fix(scraper): handle timeout errors"                │   │
│  │  git commit -m "test: add missing tests for ROI calculator"         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      VERIFY COVERAGE (90%+ Required)                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  # Backend                                                          │   │
│  │  pytest --cov=src --cov-report=term-missing --cov-fail-under=90   │   │
│  │                                                                     │   │
│  │  # Frontend                                                         │   │
│  │  npm run test:coverage                                              │   │
│  │                                                                     │   │
│  │  # Scraper                                                          │   │
│  │  pytest --cov=src --cov-fail-under=90                               │   │
│  │                                                                     │   │
│  │  # Analytics                                                        │   │
│  │  pytest --cov=src --cov-fail-under=90                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PUSH & CREATE PR                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  git push origin feat/issue-123-short-description                   │   │
│  │                                                                     │   │
│  │  # Create PR on GitHub with:                                        │   │
│  │  • Clear title (type: description)                                  │   │
│  │  • Description of changes                                           │   │
│  │  • Testing checklist completed                                      │   │
│  │  • Link to issue (Closes #123)                                      │   │
│  │  • Request review from 1+ team member                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CI/CD PIPELINE (Automated)                              │
│                                                                              │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │
│  │   Lint      │──▶│    Test     │──▶│  Coverage   │──▶│   Build     │     │
│  │   Check     │   │    Run      │   │   Check     │   │   Verify    │     │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘     │
│        │                  │                  │                  │            │
│        └──────────────────┴──────────────────┴──────────────────┘            │
│                                    │                                         │
│                              All Pass?                                       │
│                                    │                                         │
│                         ┌─────────┴─────────┐                                │
│                         │                   │                                │
│                         ▼                   ▼                                │
│                      ┌────────┐        ┌────────┐                            │
│                      │  YES   │        │   NO   │                            │
│                      │        │        │        │                            │
│                      └────┬───┘        └────┬───┘                            │
│                           │                 │                                │
│                           ▼                 ▼                                │
│                   ┌──────────────┐   ┌──────────────┐                        │
│                   │ Code Review  │   │ Fix Issues & │                        │
│                   │   Required   │   │ Push Updates │                        │
│                   └──────────────┘   └──────────────┘                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CODE REVIEW (Peer Review)                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Reviewer Checklist:                                                │   │
│  │  □ Code quality and readability                                     │   │
│  │  □ Test coverage >= 90%                                             │   │
│  │  □ Adherence to coding standards                                    │   │
│  │  □ Performance considerations                                       │   │
│  │  □ Security best practices                                          │   │
│  │  □ Documentation updated                                            │   │
│  │                                                                     │   │
│  │  Actions:                                                           │   │
│  │  • Approve (with or without comments)                               │   │
│  │  • Request changes (if issues found)                                │   │
│  │  • Comment (for discussion)                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      MERGE TO MAIN (Squash & Merge)                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Requirements:                                                      │   │
│  │  ✓ At least 1 approval                                              │   │
│  │  ✓ All CI checks pass                                               │   │
│  │  ✓ No merge conflicts                                               │   │
│  │  ✓ Branch up to date with main                                      │   │
│  │  ✓ All conversations resolved                                       │   │
│  │                                                                     │   │
│  │  Action: Click "Squash and merge"                                   │   │
│  │                                                                     │   │
│  │  After merge:                                                       │   │
│  │  • Delete feature branch                                            │   │
│  │  • Close linked issue (auto if "Closes #123")                       │   │
│  │  • Deploy to staging/production                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📊 Testing Pyramid

```
                    ▲
                   /│\
                  / │ \        E2E Tests (Playwright)
                 /  │  \       - User journeys
                /   │   \      - Browser automation
               /    │    \     - 142 tests
              /─────┼─────\
             /      │      \   Integration Tests
            /       │       \  - API endpoints
           /        │        \ - Database queries
          /         │         \- 25+ tests
         /──────────┼──────────\
        /           │           \ Unit Tests
       /            │            \- Functions in isolation
      /             │             \- Mocked dependencies
     /              │              \- 180+ tests
    ────────────────┴────────────────
```

## 🎯 Coverage Requirements

```
┌────────────────────────────────────────────────────────────────┐
│  Module        │  Required  │  Actual  │  Status               │
├────────────────────────────────────────────────────────────────┤
│  Backend       │    90%     │   92%    │  ✅ PASS              │
│  Frontend      │    90%     │   94%    │  ✅ PASS              │
│  Scraper       │    90%     │   91%    │  ✅ PASS              │
│  Analytics     │    90%     │   93%    │  ✅ PASS              │
│  E2E           │   100%     │   100%   │  ✅ PASS (journeys)   │
└────────────────────────────────────────────────────────────────┘
```

## 🚀 CI/CD Pipeline Stages

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  Code    │──▶│   Lint   │──▶│   Test   │──▶│  Build   │──▶│  Deploy  │
│  Push    │   │   Check  │   │   Run    │   │  Verify  │   │  (Auto)  │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
      │              │              │              │              │
      ▼              ▼              ▼              ▼              ▼
  Trigger      Black/ruff      pytest/        next build     SAM deploy
  Workflow     ESLint/         Vitest/        TypeScript     Vercel
               Prettier        Playwright     Check          deploy
```

## 📋 PR Review Flow

```
┌─────────────────┐
│  Author creates │
│      PR         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  CI runs tests  │────▶│   All pass?     │
└─────────────────┘     └────────┬────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
            ┌──────────────┐          ┌──────────────┐
            │     YES      │          │      NO      │
            │              │          │              │
            └──────┬───────┘          └──────┬───────┘
                   │                         │
                   ▼                         ▼
          ┌─────────────────┐       ┌─────────────────┐
          │ Reviewer checks │       │ Author fixes    │
          │ code            │       │ issues          │
          └────────┬────────┘       └────────┬────────┘
                   │                         │
                   ▼                         │
          ┌─────────────────┐                │
          │ Approves?       │                │
          └────────┬────────┘                │
                   │                         │
      ┌────────────┼────────────┐            │
      │            │            │            │
      ▼            ▼            ▼            │
┌─────────┐  ┌─────────┐  ┌─────────┐       │
│ Approve │  │ Request │  │ Comment │       │
│         │  │ Changes │  │         │       │
└────┬────┘  └────┬────┘  └────┬────┘       │
     │            │            │            │
     ▼            ▼            │            │
┌─────────┐  ┌─────────┐       │            │
│  Merge  │  │ Author  │       │            │
│  to     │  │ fixes & │       │            │
│  main   │  │ resubmit│       │            │
└─────────┘  └─────────┘       │            │
                               └────────────┘
```

## 🎭 E2E Test Coverage

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         E2E TEST COVERAGE (Playwright)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Page Tests                                                         │   │
│  │  ─────────────────────────────────────────────────────────────────  │   │
│  │  ✅ home.spec.ts              (10 tests)  - Hero, stats, CTAs      │   │
│  │  ✅ properties.spec.ts        (11 tests)  - Listing, filters       │   │
│  │  ✅ property-detail.spec.ts   (10 tests)  - Gallery, features      │   │
│  │  ✅ opportunities.spec.ts     (13 tests)  - Rankings, scores       │   │
│  │  ✅ market-stats.spec.ts      (14 tests)  - Charts, exports        │   │
│  │  ✅ about.spec.ts             (11 tests)  - Mission, team          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Cross-Cutting Tests                                                │   │
│  │  ─────────────────────────────────────────────────────────────────  │   │
│  │  ✅ navigation.spec.ts        (4 tests)   - Nav, footer, mobile    │   │
│  │  ✅ roi-calculator.spec.ts    (10 tests)  - Calculator, charts     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Quality Assurance Tests                                            │   │
│  │  ─────────────────────────────────────────────────────────────────  │   │
│  │  ✅ accessibility.spec.ts     (13 tests)  - A11y, keyboard nav     │   │
│  │  ✅ error-handling.spec.ts    (14 tests)  - 404, 500, errors       │   │
│  │  ✅ performance.spec.ts       (14 tests)  - Core Web Vitals        │   │
│  │  ✅ seo.spec.ts               (18 tests)  - Meta, OG, sitemap      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  Total: 142 E2E tests covering all user journeys                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📝 Quick Commands Reference

```bash
# Testing
pytest --cov=src --cov-fail-under=90          # Backend/Scraper/Analytics
npm run test:coverage                          # Frontend unit tests
npm run test:e2e                               # Frontend E2E tests

# Linting
black src/ && ruff src/ && mypy src/           # Python
npm run lint && npm run format                 # TypeScript

# Git workflow
git checkout -b feat/description               # Create branch
git commit -m "feat: description"              # Commit
git push origin feat/description               # Push

# Local development
docker-compose up                              # Start all services
make test                                      # Run all tests
make lint                                      # Run all linters
```

---

**For detailed guidelines, see [CONTRIBUTING.md](./CONTRIBUTING.md)**
