# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An AI-powered automotive ticket classifier that uses OpenAI GPT models to automatically classify and categorize support tickets from Zoho Desk. The system extracts dealer information, categorizes tickets, identifies syndicators, and can automatically push classifications back to Zoho.

**Tech Stack**: FastAPI (backend), Streamlit (frontend), PostgreSQL (database), Redis (caching), OpenAI GPT, Docker

## Architecture

### Service Layer Architecture

The application follows a service-oriented architecture:

- **ClassifierService** (`api/app/services/classifier.py`): Core classification logic using OpenAI GPT models. Orchestrates ticket fetching, text preparation, LLM classification, validation, dealer lookup, and database persistence.
- **ZohoService** (`api/app/services/zoho.py`): Handles all Zoho Desk API interactions including authentication, token refresh, ticket fetching, and field updates.
- **CacheService** (`api/app/services/cache.py`): Redis-based caching for classification results and frequently accessed data.

### Key Data Flow

1. Ticket is received (by ID from Zoho or as direct text)
2. If from Zoho: `ZohoService` fetches ticket data and conversation threads
3. `ClassifierService` prepares text combining subject, description, and threads
4. OpenAI GPT model classifies the ticket using structured prompts
5. Classification is validated against allowed values and enhanced with dealer mapping lookups
6. Result is stored in PostgreSQL and optionally cached in Redis
7. If auto-push enabled: Classification is pushed back to Zoho custom fields

### Reference Data System

The classifier relies on two CSV files in `data/`:
- `syndicators.csv`: Approved list of syndicator names (Kijiji, AutoTrader, etc.)
- `rep_dealer_mapping.csv`: Maps dealer names to dealer IDs and assigned reps

These are loaded at service initialization and used for validation and enrichment. The system uses fuzzy matching and normalization for dealer name lookups.

## Common Commands

### Running Locally

**Start API server:**
```bash
cd api
uvicorn main:app --reload --port 8088
```

**Start UI:**
```bash
cd ui
streamlit run main.py
```

**Run with Docker Compose:**
```bash
docker-compose up -d
```

### Database Operations

**Create migration:**
```bash
cd api
alembic revision --autogenerate -m "Description"
```

**Apply migrations:**
```bash
cd api
alembic upgrade head
```

**Rollback migration:**
```bash
cd api
alembic downgrade -1
```

### Testing

**Run all tests:**
```bash
cd api
pytest
```

**Run specific test file:**
```bash
cd api
pytest tests/test_classifier.py
```

**Run with coverage:**
```bash
cd api
pytest --cov=app --cov-report=html
```

## Configuration

Environment variables are defined in `.env` file (copy from `.env.example`). Key configuration is managed through `api/app/core/config.py` using Pydantic settings.

**Critical environment variables:**
- `OPENAI_API_KEY`: Required for classification
- `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN`, `ZOHO_ORG_ID`: Required for Zoho integration
- `POSTGRES_*`: Database connection details
- `REDIS_HOST`: Cache connection (optional, system works without it)
- `ENVIRONMENT`: Set to `development`, `staging`, or `production`

## Classification Fields

The system extracts exactly 8 fields from each ticket:

1. **contact**: Contact person (usually the rep, unless ticket is from client domain)
2. **dealer_name**: Dealership name (must be rooftop, not group name)
3. **dealer_id**: Dealer ID from mapping CSV
4. **rep**: Assigned rep name
5. **category**: Ticket category (see `VALID_CATEGORIES` in config)
6. **sub_category**: Sub-category (see `VALID_SUBCATEGORIES` in config)
7. **syndicator**: Syndicator name (must match `syndicators.csv`)
8. **inventory_type**: Inventory type (New, Used, Demo, New + Used)

### Validation Rules

- Multiple dealers are formatted as `"Multiple: [Name1], [Name2]"` with blank `dealer_id`
- Syndicator refers to export/feed destination, not import source
- Fields use strict dropdown validation - invalid values are blanked
- Fallback extraction applies keyword matching if GPT classification is incomplete
- Dealer names are normalized (lowercased, accents removed) for fuzzy matching

## OpenAI Integration (GPT-5)

The classifier uses **GPT-5** (released August 2025) with structured prompts and few-shot examples. Prompts are bilingual (English/French) aware.

**Key GPT-5 Changes:**
- Uses `client.responses.create()` API (not the old `chat.completions.create()`)
- Parameters: `reasoning={"effort": "low"}` and `verbosity="low"` instead of temperature/max_tokens
- Response accessed via `response.output_text` (not `choices[0].message.content`)
- Model names: `gpt-5`, `gpt-5-mini`, `gpt-5-nano`

**Configuration:**
- `OPENAI_MODEL`: Default is `gpt-5-mini` (balance of cost and performance)
- `OPENAI_REASONING_EFFORT`: `minimal`, `low`, `medium`, or `high` (default: `low`)
- `OPENAI_VERBOSITY`: `low`, `medium`, or `high` (default: `low` for concise JSON)

**System Features:**
- Parses JSON from GPT response (handles markdown code blocks)
- Low verbosity ensures concise JSON output
- Falls back to rule-based extraction if GPT fails
- Retry logic with exponential backoff

## Zoho Integration

**Token Management**: OAuth tokens are automatically refreshed and stored in the `zoho_tokens` database table. Tokens are refreshed 5 minutes before expiry.

**Custom Fields**: The system maps classification results to Zoho custom fields:
- `cf_syndicators` → syndicator
- `cf_inventory_type` → inventory_type
- `category` → category (core field)
- `subCategory` → sub_category (core field)

**Rate Limiting**: Automatic retry with exponential backoff for rate limits (429) and server errors (5xx).

## Code Structure Patterns

### Adding New Endpoints

Endpoints are organized in `api/app/api/endpoints/`:
- `classifier.py`: Classification and Zoho ticket operations
- `management.py`: Batch processing and admin operations
- `settings.py`: Configuration management

Follow the dependency injection pattern using FastAPI `Depends()` for database sessions and service instances.

### Database Models

Models are in `api/app/db/models/`. Use SQLAlchemy ORM with:
- `created_at` and `updated_at` timestamps on all models
- JSON fields for flexible metadata storage
- Foreign key relationships with cascade deletes

### Adding New Syndicators or Categories

1. **Syndicators**: Add to `data/syndicators.csv` (single column: "Syndicator")
2. **Categories**: Update `VALID_CATEGORIES` list in `api/app/core/config.py`
3. **Sub-categories**: Update `VALID_SUBCATEGORIES` in config
4. **Inventory types**: Update `VALID_INVENTORY_TYPES` in config

Changes to valid values require service restart to reload.

## Bilingual Support

The system handles both English and French tickets. The GPT prompt includes examples in both languages. Dealer name matching is accent-insensitive using Unicode normalization.

## Troubleshooting

**Zoho authentication failures**: Check token expiry in `zoho_tokens` table. Force refresh by setting `force_refresh=True` in `get_access_token()`.

**Classification returns empty fields**: Check OpenAI API key, review GPT response in logs, verify reference CSVs are loaded correctly.

**Dealer lookup failures**: Verify `data/rep_dealer_mapping.csv` format (columns: "Rep Name", "Dealer Name", "Dealer ID"). Check normalization logic in `app/utils/dealer.py`.

**Database connection issues**: Ensure PostgreSQL is running and `POSTGRES_*` environment variables are correct. Check `docker-compose.yml` for service dependencies.
