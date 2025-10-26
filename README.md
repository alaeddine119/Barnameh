# 🏭 Barnameh - AI-Powered Operational Intelligence Platform

> Transform operational data into actionable insights with AI-driven analytics and predictive recommendations.

[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11-green)](https://www.python.org/)

## Overview

Barnameh helps operations managers make better decisions faster by centralizing operational data, automatically analyzing trends and anomalies, predicting future needs, and providing AI-powered recommendations through conversational interfaces.  

## Key Features

- **Real-Time Analytics Dashboard**: Live metrics, resource utilization, production trends, and attendance monitoring
- **AI-Powered Recommendations**: Natural language interface for operational insights using Groq LLM
- **Machine Learning Engine**: Anomaly detection, predictive maintenance, and resource optimization
- **Modern UI**: Dark/light mode, responsive design, intuitive data visualization

## Technology Stack

**Frontend**
- Next.js 15 with TypeScript
- TailwindCSS & shadcn/ui components
- Convex for real-time data sync

**Backend**
- Python FastAPI ML engine
- PostgreSQL database
- Groq LLM for AI inference
- scikit-learn for ML models

**Infrastructure**
- Turborepo monorepo
- RESTful API architecture

## Quick Start

### Prerequisites
- Node.js 18+ and Bun
- Python 3.11+
- PostgreSQL (optional - uses mock data by default)

### Installation

1. **Clone and install dependencies**
```bash
git clone https://github.com/alaeddine119/Barnameh.git
cd Barnameh
bun install
```

2. **Set up Convex backend**
```bash
bun dev:setup
```
Follow the prompts to create a Convex project.

3. **Configure ML Engine**
```bash
cd packages/ml-engine
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **Set environment variables**
```bash
# Create .env file in packages/ml-engine
export GROQ_API_KEY="your-groq-api-key"
export DATABASE_URL="postgresql://user:pass@localhost/dbname"  # Optional
```

5. **Run the application**

Terminal 1 - Start ML Engine:
```bash
cd packages/ml-engine
source venv/bin/activate
python -m uvicorn api.main:app --reload --port 8000
```

Terminal 2 - Start Web App:
```bash
bun dev
```

6. **Access the application**
- Web Dashboard: http://localhost:3001
- ML API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Data Configuration

### Using Mock Data (Default)
The application comes with mock data generators for development and demonstration. No database setup required.

### Using Real Database

1. **Set up PostgreSQL database**
```sql
CREATE DATABASE operational_db;
```

2. **Run migrations** (schema in `packages/ml-engine/database/schema.sql`)

3. **Configure database connection** in `packages/ml-engine/api/main.py`:
```python
# Update DATABASE_URL environment variable
DATABASE_URL = "postgresql://user:password@localhost/operational_db"
```

4. **Populate with your operational data** using the provided data models:
   - `operational_events`: Production, maintenance, downtime events
   - `resources`: Equipment and machinery data
   - `employees`: Staff and attendance records
   - `shifts`: Scheduling information

The ML engine will automatically analyze your real data and provide insights.

## API Documentation

The ML Engine provides RESTful endpoints for analytics:

- `GET /api/v1/health` - Health check
- `GET /api/v1/recommendations` - Get AI-powered recommendations
- `POST /api/v1/chat` - Chat with AI assistant
- `GET /api/v1/analytics/resource-utilization` - Resource metrics
- `GET /api/v1/analytics/attendance-trends` - Attendance analysis
- `GET /api/v1/analytics/production-revenue` - Production & cost trends
- `GET /api/v1/anomalies` - Detect operational anomalies
- `GET /api/v1/predictions/maintenance` - Predict maintenance needs

Full API documentation available at http://localhost:8000/docs

## Development

### Running Tests
```bash
# Frontend tests
cd apps/web
bun test

# Backend tests
cd packages/ml-engine
pytest
```

### Linting & Formatting
```bash
# Run Biome for code quality
bun run check
bun run format
```

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

MIT License - see LICENSE file for details.

---

Built with modern technologies for operational excellence. 🚀







## Project Structure

```
Barnameh/
├── apps/
│   ├── web/         # Frontend application (Next.js)
├── packages/
│   ├── backend/     # Convex backend functions and schema
```

## Available Scripts

- `bun dev`: Start all applications in development mode
- `bun build`: Build all applications
- `bun dev:web`: Start only the web application
- `bun dev:setup`: Setup and configure your Convex project
- `bun check-types`: Check TypeScript types across all apps
- `bun check`: Run Biome formatting and linting
