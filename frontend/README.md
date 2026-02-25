# Malta Property Investment Analyzer - Frontend

A modern, SEO-optimized Next.js 14+ frontend for the Malta Property Investment Analyzer platform.

## Features

- **Property Search & Filtering**: Browse properties with advanced filters (location, price, type, bedrooms)
- **ROI Calculator**: Interactive calculator with customizable parameters
- **Opportunity Scoring**: Intelligent scoring system to identify best investments
- **Market Statistics**: Comprehensive market data and trends
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **SEO Optimized**: Server-side rendering, structured data, sitemap, robots.txt
- **Type Safe**: Full TypeScript support with strict mode

## Tech Stack

- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript 5.3+ (strict mode)
- **Styling**: Tailwind CSS
- **Data Fetching**: TanStack Query (React Query)
- **Validation**: Zod
- **Charts**: Recharts
- **Icons**: Lucide React
- **Testing**: Vitest (unit) + Playwright (E2E)

## Getting Started

### Prerequisites

- Node.js 18.17.0 or later
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd malta-property-analyzer/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env.local
```

Edit `.env.local` with your configuration:
```env
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_USE_MOCK_API=true
```

4. Run the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run typecheck` - Run TypeScript type checking
- `npm run test` - Run unit tests
- `npm run test:watch` - Run unit tests in watch mode
- `npm run test:coverage` - Run unit tests with coverage
- `npm run test:e2e` - Run E2E tests
- `npm run test:e2e:ui` - Run E2E tests with UI

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page
│   │   ├── loading.tsx         # Loading UI
│   │   ├── error.tsx           # Error UI
│   │   ├── not-found.tsx       # 404 page
│   │   ├── properties/         # Property pages
│   │   ├── opportunities/      # Opportunities page
│   │   ├── stats/              # Market stats page
│   │   ├── about/              # About page
│   │   ├── api/                # API routes
│   │   ├── sitemap.ts          # Dynamic sitemap
│   │   └── robots.ts           # robots.txt
│   ├── components/
│   │   ├── ui/                 # Reusable UI components
│   │   ├── layout/             # Layout components
│   │   ├── property/           # Property components
│   │   ├── roi/                # ROI components
│   │   └── stats/              # Stats components
│   ├── hooks/                  # Custom React hooks
│   ├── lib/                    # Utilities and API
│   ├── types/                  # TypeScript types
│   └── styles/                 # Global styles
├── tests/
│   ├── unit/                   # Unit tests
│   └── e2e/                    # Playwright E2E tests
└── public/                     # Static assets
```

## Key Components

### UI Components
- `Button` - Flexible button with variants and sizes
- `Card` - Card container with header, content, footer
- `Input` - Form input with label and error handling
- `Select` - Dropdown select component
- `Badge` - Status badges with color variants
- `Loading` - Loading states and skeletons

### Property Components
- `PropertyCard` - Property listing card
- `PropertyList` - Grid of property cards
- `PropertyFilters` - Filter and sort controls
- `PropertyGallery` - Image gallery with zoom
- `PropertyMap` - Location map display

### ROI Components
- `ROICalculator` - Interactive ROI calculator
- `ROIDisplay` - ROI metrics display
- `CashFlowChart` - 10-year cash flow projection chart
- `OpportunityScore` - Visual score display

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Home | `/` | Landing page with featured properties |
| Properties | `/properties` | Filterable property listings |
| Property Detail | `/properties/[id]` | Individual property page |
| ROI Analysis | `/properties/[id]/roi` | Detailed ROI analysis |
| Opportunities | `/opportunities` | Top 20 opportunities ranked |
| Market Stats | `/stats` | Market statistics and trends |
| About | `/about` | About the platform |

## SEO

The application implements comprehensive SEO:

- **Dynamic Metadata**: Each page has unique title and description
- **Structured Data**: JSON-LD for properties and pages
- **Sitemap**: Dynamic sitemap generation (`/sitemap.xml`)
- **Robots.txt**: Configured for optimal crawling
- **Open Graph**: Social sharing meta tags
- **Canonical URLs**: Prevent duplicate content issues
- **Semantic HTML**: Proper heading hierarchy and landmarks

## Testing

### Unit Tests

Run unit tests with Vitest:

```bash
npm run test
```

Run with coverage:

```bash
npm run test:coverage
```

### E2E Tests

Run E2E tests with Playwright:

```bash
npm run test:e2e
```

Run with UI:

```bash
npm run test:e2e:ui
```

### Test Coverage

- Unit tests: Components, utilities, hooks
- E2E tests: User journeys, navigation, filtering, ROI calculator
- Target: 90%+ coverage

## API Integration

The frontend connects to a backend API. Configure the API URL in `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For development without a backend, enable mock data:

```env
NEXT_PUBLIC_USE_MOCK_API=true
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_APP_URL` | Application URL | `http://localhost:3000` |
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_USE_MOCK_API` | Use mock data | `false` |

## Deployment

### Build for Production

```bash
npm run build
```

### Deploy to Vercel

1. Push to GitHub
2. Connect repository to Vercel
3. Configure environment variables
4. Deploy

### Static Export

For static hosting:

```bash
npm run build
```

The `dist` folder will contain the static export.

## Performance

- **Image Optimization**: Next.js Image component with lazy loading
- **Code Splitting**: Automatic route-based splitting
- **Prefetching**: Link prefetching for instant navigation
- **Caching**: React Query caching with stale-while-revalidate

## Accessibility

- Semantic HTML structure
- ARIA labels and roles
- Keyboard navigation support
- Focus management
- Color contrast compliance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For support, email info@malta-property-analyzer.com or open an issue on GitHub.
