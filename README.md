# Malta Property Investment Analyzer

A comprehensive platform for scraping, analyzing, and identifying high-ROI property investment opportunities in Malta.

## 🏗️ Architecture

This project follows a serverless microservices architecture with:

- **Backend**: AWS SAM (Serverless Application Model) with Lambda, API Gateway, DynamoDB, EventBridge
- **Frontend**: Next.js 14+ with TypeScript, React, and Tailwind CSS
- **Scraper**: Python async scraper for Malta property websites
- **Analytics**: Malta-specific ROI calculation engine

## 📁 Project Structure

```
malta-property-analyzer/
├── backend/              # AWS SAM serverless backend
├── frontend/             # Next.js 14+ frontend
├── scraper/              # Property scraper
├── analytics/            # ROI analysis engine
└── .github/              # GitHub Actions workflows
```

## 🚀 Quick Start

See individual component READMEs for setup instructions.

## 🧪 Testing

All components require 90%+ test coverage.

## 📝 License

MIT License
