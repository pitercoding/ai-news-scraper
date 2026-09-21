# AI News Scraper

> An AI-powered technology news aggregator built with Python, FastAPI, OpenAI, and Next.js.

AI News Scraper collects technology articles from an RSS feed, extracts their full content, stores them in SQLite, and uses the OpenAI API to generate an English summary, exactly three key points, and a category for each article. The processed data is exposed through a REST API and displayed in a Next.js web interface.

## Table of Contents

- [AI News Scraper](#ai-news-scraper)
  - [Table of Contents](#table-of-contents)
  - [Project Overview](#project-overview)
  - [Motivation](#motivation)
  - [Features](#features)
  - [Screenshots](#screenshots)
    - [News dashboard](#news-dashboard)
    - [Article details](#article-details)
  - [Architecture](#architecture)
  - [Processing Pipeline](#processing-pipeline)
    - [Phase A: Ingestion](#phase-a-ingestion)
    - [Phase B: Content Extraction](#phase-b-content-extraction)
    - [Phase C: AI Analysis](#phase-c-ai-analysis)
    - [Retrying failed articles](#retrying-failed-articles)
  - [AI Analysis](#ai-analysis)
  - [Technologies](#technologies)
  - [Project Structure](#project-structure)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Backend setup](#backend-setup)
    - [Environment variables](#environment-variables)
    - [Database](#database)
  - [Running the Project](#running-the-project)
    - [Running the processing pipeline](#running-the-processing-pipeline)
    - [Running the backend API](#running-the-backend-api)
    - [Running the frontend](#running-the-frontend)
  - [Running Tests](#running-tests)
  - [API Endpoints](#api-endpoints)
    - [`GET /articles`](#get-articles)
    - [`GET /articles/{article_id}`](#get-articlesarticle_id)
    - [`GET /categories`](#get-categories)
  - [Frontend Features](#frontend-features)
  - [Error Handling and Reliability](#error-handling-and-reliability)
  - [Engineering Decisions](#engineering-decisions)
    - [SQLite instead of PostgreSQL](#sqlite-instead-of-postgresql)
    - [No task queue](#no-task-queue)
    - [Structured AI output](#structured-ai-output)
    - [Separated pipeline phases](#separated-pipeline-phases)
    - [Database as processing state](#database-as-processing-state)
    - [The API only exposes fully processed articles](#the-api-only-exposes-fully-processed-articles)
    - [Reader/writer separation](#readerwriter-separation)
    - [Server-side data fetching in the frontend](#server-side-data-fetching-in-the-frontend)
  - [Limitations](#limitations)
  - [Future Improvements](#future-improvements)
  - [License](#license)
  - [Author](#author)

## Project Overview

Technology news is spread across many sources and formats. This project turns one of those sources into a small, structured, searchable news reader. A Python pipeline reads the RSS feed, skips URLs that are already stored, downloads each article page, extracts the article text, and asks an OpenAI model to analyze it. The results are saved back to the same SQLite database.

A FastAPI application then serves the processed articles, and a Next.js frontend lets users browse, search, filter, and open them. Only articles that have completed AI analysis are listed in the interface.

```text
RSS Feed
   ↓
Python Scraper
   ↓
SQLite
   ↓
Article Content Extraction
   ↓
OpenAI Analysis
   ↓
FastAPI
   ↓
Next.js Frontend
```

In short, the application:

- collects articles from an RSS feed;
- avoids duplicate URLs;
- extracts the article content from the source page;
- stores everything locally in SQLite;
- generates an AI summary and exactly 3 key points per article;
- classifies each article into one category;
- exposes the data through a REST API;
- displays the processed articles in a web interface.

## Motivation

I built this project to practice and demonstrate, in a single end-to-end application:

- Python backend development;
- web scraping and RSS processing;
- database persistence with SQLAlchemy;
- REST API development with FastAPI;
- OpenAI API integration and structured AI outputs;
- error handling in a multi-step process;
- automated testing;
- Next.js and TypeScript.

The practical motivation is simple: technology news is published across many different sources and formats. This project explores how a small automated pipeline can collect that information, extract useful content, and transform it into concise structured summaries.

It is a portfolio/MVP project. It is not designed or claimed to be production-scale.

## Features

- RSS feed ingestion (`feedparser` + `requests`)
- Duplicate article detection by URL (unique constraint plus an explicit check)
- Filtering of non-news URLs from the feed
- Article content extraction with BeautifulSoup
- SQLite persistence with SQLAlchemy
- AI-generated English summaries
- Exactly 3 AI-generated key points per article
- AI categorization into six fixed categories
- Structured OpenAI responses validated with Pydantic
- Failure recovery through article processing state (failed articles are retried on the next run)
- REST API with search, category filtering, and pagination
- Interactive API documentation (Swagger UI and ReDoc)
- Next.js frontend with article cards, search, category filter, and pagination
- Article detail pages showing content, AI summary, and key points
- Loading, error, empty, and not-found states
- Automated test suite (120 tests)

## Screenshots

### News dashboard

The main page: a grid of article cards, each with its category badge, title, RSS summary, and links to the detail page and the original article. It also shows the search bar, the category filter, and pagination.

<p align="center">
  <img src="docs/images/news-dashboard.png" alt="AI News Scraper - News Dashboard" width="800">
</p>

> The source feed (Tecnoblog) is in Portuguese, so article titles, RSS summaries, and extracted content appear in Portuguese. The AI summary and key points are generated in English.

### Article details

The detail page for a single article, showing the **Article Content** extracted from the source, the **AI Summary**, and the **Key Points** generated by the model.

<p align="center">
  <img src="docs/images/article-details1.png" alt="AI News Scraper - Article Details: header and extracted content" width="800">
</p>

<p align="center">
  <img src="docs/images/article-details2.png" alt="AI News Scraper - Article Details: AI summary and key points" width="800">
</p>

## Architecture

```text
                  RSS Feed
                     │
                     ▼
              Python Scraper
              (feedparser, requests)
                     │
                     ▼
                  SQLite  ◄──────────────────────────┐
                     │                               │
          ┌──────────┴──────────┐                    │
          │                     │                    │
          ▼                     ▼                    │
   Content Extraction      AI Analysis               │
   (BeautifulSoup)               │                   │
          │                      ▼                   │
          │                 OpenAI API               │
          │                      │                   │
          └─────► results saved ─┴───────────────────┘
                     │
                     ▼
                  FastAPI
                     │
                     ▼
              Next.js Frontend
```

| Layer | Role |
| --- | --- |
| Scraper (`backend/scraper`) | Fetches the RSS feed, parses entries, filters non-news URLs, and extracts article text from the HTML page. |
| Database (`backend/database.py`, `backend/models.py`) | SQLAlchemy model and query helpers for a single `articles` table in SQLite. |
| AI (`backend/ai`) | Builds the prompt, sends it to OpenAI, and validates the structured response. |
| Pipeline (`backend/pipeline`) | Orchestrates ingestion, content extraction, and AI analysis in sequence. |
| API (`backend/api.py`, `backend/schemas.py`) | Read-only FastAPI application that serves analyzed articles. |
| Frontend (`frontend/`) | Next.js (App Router) application that consumes the API. |

The pipeline (writer) and the API (reader) are independent processes that communicate only through the SQLite database.

## Processing Pipeline

The official entry point is `backend/pipeline/run.py`. It runs three phases in order and prints a summary at the end. It is a plain script executed manually, not a background queue or a distributed worker system.

### Phase A: Ingestion

```text
RSS
 ↓
fetch_news()
 ↓
duplicate protection
 ↓
save_article()
```

For each URL in `FEED_URLS`, `fetch_news()` downloads the feed and returns entries with title, URL, publication date, and a summary cleaned from the RSS HTML. Entries with an invalid date are skipped. Entries whose URL is not a news article (`is_news_article()`) are skipped. New articles are saved with an empty `content`; articles whose URL already exists are counted as existing and not saved again. A failing feed is counted and does not stop the run.

### Phase B: Content Extraction

```text
articles without content
 ↓
fetch_article_content()
 ↓
update_article_content()
```

Every article whose `content` is empty is downloaded, and the article body is extracted from the page HTML and stored. If extraction fails or returns nothing, the article keeps an empty `content`.

### Phase C: AI Analysis

```text
articles without AI analysis
 ↓
create_article_prompt()
 ↓
OpenAI
 ↓
structured ArticleAnalysis
 ↓
save summary/key points/category
```

Every article that has content but no `ai_summary` is analyzed, and the summary, key points, and category are saved.

### Retrying failed articles

The database itself is the processing state; there is no separate job table:

| State | Meaning | Picked up by |
| --- | --- | --- |
| `content == ""` | Saved, but content not extracted yet | Phase B |
| `content != ""` and `ai_summary IS NULL` | Content extracted, not analyzed yet | Phase C |
| `ai_summary IS NOT NULL` | Fully processed | Listed by the API |

If an HTTP request or an OpenAI call fails, the article simply stays in its previous state and is picked up again the next time the pipeline runs. An article is only analyzed after its content has been extracted.

## AI Analysis

The AI step lives in `backend/ai/`.

- **Provider and model:** OpenAI API, model `gpt-5-mini`, called through `client.responses.parse(...)`.
- **Structured output:** the response is parsed directly into a Pydantic model instead of free-form text:

  ```python
  class ArticleAnalysis(BaseModel):
      summary: str
      key_points: list[str] = Field(min_length=3, max_length=3)
      category: Literal[
          "AI", "Programming", "Technology",
          "Business", "Science", "Security",
      ]
  ```

- **Exactly 3 key points:** enforced by `min_length=3` and `max_length=3`.
- **Restricted categories:** `AI`, `Programming`, `Technology`, `Business`, `Science`, and `Security`. The prompt also describes each category so the model picks the one matching the article's primary subject.
- **English output:** the prompt asks for the summary and key points in English.
- **Content truncation:** article content is cut to the first 8,000 characters before being sent to the model (`prepare_article_for_ai()`).
- **Prompt input:** title, RSS summary, and (truncated) extracted content.

Instead of relying on free-form text parsing, the application validates the AI response against a defined schema. An answer with a different number of key points or an unknown category is rejected instead of being stored.

Key points are stored in the database as a JSON string and converted back to a list by the API response schema.

## Technologies

| Technology | Purpose |
| --- | --- |
| Python | Backend, scraping, and pipeline |
| FastAPI | REST API |
| Uvicorn | ASGI server for the API |
| SQLAlchemy | Database ORM |
| SQLite | Local persistence |
| Alembic | Database migration tooling (configured, see [Database](#database)) |
| feedparser | RSS parsing |
| requests | HTTP requests |
| BeautifulSoup (`beautifulsoup4`) | HTML content extraction |
| OpenAI API (`openai`) | Article analysis |
| Pydantic | API schemas and structured AI output validation |
| python-dotenv | Loading `OPENAI_API_KEY` from `.env` |
| pytest | Automated testing |
| Next.js 16 | Frontend framework (App Router) |
| React 19 | UI |
| TypeScript | Frontend type safety |
| ESLint | Frontend linting |

## Project Structure

```text
ai-news-scraper/
├── alembic/                    # Alembic environment and migration scripts
├── backend/
│   ├── ai/
│   │   ├── client.py           # OpenAI client and ArticleAnalysis schema
│   │   ├── prepare.py          # Content truncation and prompt construction
│   │   └── reprocess.py        # Standalone script: AI analysis only
│   ├── pipeline/
│   │   └── run.py              # Official pipeline (phases A, B, C)
│   ├── scraper/
│   │   └── rss.py              # RSS parsing and article content extraction
│   ├── api.py                  # FastAPI application
│   ├── database.py             # Engine, table creation, and query helpers
│   ├── models.py               # SQLAlchemy Article model
│   └── schemas.py              # Pydantic API response schemas
├── docs/
│   └── images/                 # README screenshots
├── frontend/
│   ├── public/                 # Static assets (logo)
│   └── src/
│       ├── app/                # Pages: listing, article details, loading, error
│       ├── components/         # ArticleCard, CategoryFilter, SearchBar, Pagination, Header
│       ├── services/           # API client (articleService.ts)
│       └── types/              # TypeScript types
├── tests/
│   ├── conftest.py             # Temporary SQLite database and seed data
│   ├── test_ai_client.py
│   ├── test_ai_prepare.py
│   ├── test_ai_reprocess.py
│   ├── test_api.py
│   ├── test_database.py
│   ├── test_pipeline.py
│   └── test_rss.py
├── .env.example                # Backend environment variables template
├── alembic.ini
├── LICENSE
├── pyproject.toml              # pytest configuration
├── requirements.txt
└── README.md
```

The SQLite file is created at `data/news.db`, which is git-ignored and does not exist in a fresh clone.

## Installation

### Prerequisites

- Python 3.14 (the version the project was developed and tested with)
- Node.js and npm
- Git
- An [OpenAI API key](https://platform.openai.com/api-keys) (required to run the pipeline; not required to run the API or the tests)

The commands below are for Windows PowerShell.

### Backend setup

**1. Clone the repository**

```powershell
git clone https://github.com/pitercoding/ai-news-scraper.git
cd ai-news-scraper
```

**2. Create and activate a virtual environment**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, allow it for the current session only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**3. Install dependencies**

```powershell
pip install -r requirements.txt
```

**4. Configure the Python path**

The backend uses the `backend` directory as the Python import root (for example, `from database import ...`). Set this in every new terminal session before running backend commands:

```powershell
$env:PYTHONPATH="backend"
```

**5. Create the data directory**

The SQLite file lives in `data/`, and SQLite does not create missing directories:

```powershell
New-Item -ItemType Directory -Force data
```

### Environment variables

| Variable | Location | Required by | Description |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | `.env` (repository root) | Pipeline and AI scripts | OpenAI API key. Importing `backend/ai/client.py` raises an error if it is missing. |
| `NEXT_PUBLIC_API_URL` | `frontend/.env.local` | Frontend | Base URL of the FastAPI backend. |

Backend: copy the template and add your key.

```powershell
Copy-Item .env.example .env
```

```text
OPENAI_API_KEY=your_openai_api_key
```

Frontend: copy the template (the default points to the local API).

```powershell
Copy-Item frontend\.env.example frontend\.env.local
```

```text
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

> **Never commit your `.env` file or API keys to Git.** Both `.env` and `frontend/.env.local` are already git-ignored; only the `.env.example` templates are tracked.

### Database

The application uses SQLite. The database file is `data/news.db`, resolved relative to the repository root by `backend/database.py`.

- **Tables are created automatically** by the pipeline (`create_tables()` runs at the start of `backend/pipeline/run.py`). You can also create them without running the pipeline:

  ```powershell
  $env:PYTHONPATH="backend"
  python backend/database.py
  ```

- **Alembic is not required for a normal setup.** The repository contains Alembic configuration and two migrations (adding the AI columns, and changing `published_at` to a timezone-aware datetime), but they document the schema history of an existing database. A new database is created directly from the SQLAlchemy model with `create_all`.
- The database is empty until the pipeline has run at least once.
- The API does not create tables. On a fresh clone, run the pipeline (or the command above) before starting the API.

## Running the Project

Run the pipeline first to populate the database, then start the API, then the frontend.

### Running the processing pipeline

```powershell
$env:PYTHONPATH="backend"
python backend/pipeline/run.py
```

The script runs Phase A (ingestion), Phase B (content extraction), and Phase C (AI analysis), then prints a summary (new/existing/skipped articles, failed feeds, extracted contents, analyzed articles, failures). It is safe to run repeatedly: existing URLs are not duplicated and pending articles are retried.

> **Warning:** the pipeline makes real HTTP requests and real OpenAI API calls. Running it may create OpenAI API usage and costs, because articles are sent to the OpenAI API for analysis. Do not run it blindly if a large number of pending articles exists; each pending article with extracted content results in one API call.

The feed list is defined in `FEED_URLS` in [backend/pipeline/run.py](backend/pipeline/run.py). Currently it contains one feed: `https://tecnoblog.net/feed/` (a Portuguese-language technology news site).

Optionally, `backend/ai/reprocess.py` runs only the AI analysis step over articles that have content but no analysis:

```powershell
$env:PYTHONPATH="backend"
python backend/ai/reprocess.py
```

### Running the backend API

```powershell
$env:PYTHONPATH="backend"
uvicorn api:app --reload
```

| URL | Description |
| --- | --- |
| http://127.0.0.1:8000 | API base URL |
| http://127.0.0.1:8000/docs | Swagger UI |
| http://127.0.0.1:8000/redoc | ReDoc |

The API only reads from the database; it does not call OpenAI, so it does not need `OPENAI_API_KEY`.

### Running the frontend

In a second terminal, with the API running:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:3000. The frontend fetches data from the FastAPI backend at the URL configured in `NEXT_PUBLIC_API_URL`. Other available scripts: `npm run build`, `npm run start`, and `npm run lint`.

## Running Tests

```powershell
$env:PYTHONPATH="backend"
python -m pytest
```

Use `python -m pytest` rather than the bare `pytest` command (the `pytest` launcher has a known issue in the Windows development environment used for this project).

The suite currently has 120 tests across seven files. HTTP requests and OpenAI calls are mocked, and the tests run against a temporary SQLite database seeded in `tests/conftest.py`, so they need neither network access nor a real API key. They cover:

- RSS parsing, date parsing, summary/content cleaning, and non-news URL filtering (`test_rss.py`);
- article content extraction (`test_rss.py`);
- database operations, filtering, ordering, counting, and duplicate prevention (`test_database.py`);
- API endpoints, pagination, search, filtering, validation errors, and 404 handling (`test_api.py`);
- pipeline phases, feed and article failures, idempotency, and retry behavior (`test_pipeline.py`);
- the AI schema (exactly 3 key points, allowed categories), prompt construction, content truncation, and the standalone analysis script (`test_ai_client.py`, `test_ai_prepare.py`, `test_ai_reprocess.py`).

No coverage measurement is configured in the repository.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/articles` | Paginated list of analyzed articles |
| GET | `/articles/{article_id}` | A single article, including its full content |
| GET | `/categories` | Distinct categories currently in the database |

Interactive documentation is available at `/docs` and `/redoc`.

### `GET /articles`

| Query parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `category` | string | none | Exact match on the article category |
| `search` | string | none | Case-insensitive match against the article title or RSS summary |
| `limit` | integer | `20` | Page size, between 1 and 100 |
| `offset` | integer | `0` | Number of articles to skip (must be 0 or greater) |

- Only articles that have completed AI analysis are returned.
- Articles are ordered by publication date, newest first.
- `category` and `search` can be combined.
- Invalid `limit`/`offset` values return a `422` validation error.

Response structure:

```json
{
  "items": [
    {
      "id": 1,
      "title": "...",
      "url": "https://...",
      "published_at": "2026-09-19T12:00:00-03:00",
      "summary": "...",
      "ai_summary": "...",
      "key_points": ["...", "...", "..."],
      "category": "Technology"
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

`total` is the number of articles matching the filters (not just the current page), which the frontend uses to compute the number of pages.

### `GET /articles/{article_id}`

Returns the same fields as a list item plus `content` (the extracted article text). Returns `404` with `{"detail": "Article not found"}` if the ID does not exist. Unlike the list endpoint, this endpoint can also return an article that has not been analyzed yet (in which case `ai_summary`, `key_points`, and `category` are `null`).

### `GET /categories`

Returns a sorted list of distinct category names, for example `["AI", "Business", "Programming"]`.

## Frontend Features

The frontend is a Next.js App Router application written in TypeScript. Pages are async server components that fetch data from the API through `frontend/src/services/articleService.ts`.

- **Article listing:** responsive grid of article cards with category badge, title, RSS summary, a link to the detail page, and a link to the original article (opens in a new tab). The total article count is shown above the grid.
- **Search:** text search form; the term is stored in the URL (`?search=`).
- **Category filter:** dropdown populated from `/categories`; stored in the URL (`?category=`).
- **Pagination:** 12 articles per page with Previous/Next controls (`?page=`). Changing the search or category resets to the first page, and invalid `page` values are clamped to page 1.
- **Article details:** shows the category, title, publication date, RSS summary, the extracted **Article Content**, the **AI Summary**, and the **Key Points**, plus a link to the original article.
- **Loading state:** `loading.tsx`.
- **Error state:** `error.tsx`, with a "Try again" button.
- **Empty state:** message shown when no article matches the current search/filter.
- **Not found:** the detail page renders Next.js's not-found page if the article cannot be loaded.

## Error Handling and Reliability

- A feed that fails to download or parse is counted and skipped; the remaining feeds are still processed.
- Feed entries with an invalid date are skipped instead of aborting the feed.
- Duplicate URLs are prevented: `articles.url` has a unique constraint, and `save_article()` checks for an existing URL before inserting.
- A content extraction failure (network error, non-2xx response, or no content found) is isolated to that article and counted as a failure.
- An AI failure (API error or a response that does not match the schema) is isolated to that article and counted as a failure.
- Failed articles stay pending in the database and are retried on the next pipeline run.
- AI responses are validated against the `ArticleAnalysis` schema before being saved.
- HTTP requests use a 15-second timeout.
- The API validates `limit` and `offset` and returns proper `422` and `404` responses.

This is a simple, sequential script with database-backed state. It is not a production-grade job system.

## Engineering Decisions

### SQLite instead of PostgreSQL

This is a small portfolio/MVP application with a single table and a single writer, so a separate database server would add setup cost without a clear benefit. SQLite keeps installation to `pip install` and a file on disk. SQLAlchemy is used for data access.

### No task queue

Tools such as Celery, Redis, or Kafka were intentionally avoided. The workload is a small batch of articles processed sequentially by a script, which does not justify the operational complexity.

### Structured AI output

The model's response is parsed directly into a Pydantic schema (exactly 3 key points, a fixed category set) rather than parsed from arbitrary text. Invalid output fails loudly and the article is retried later, instead of storing malformed data.

### Separated pipeline phases

Ingestion, content extraction, and AI analysis are separate functions with separate failure counters. Cheap steps (RSS, HTML) are decoupled from the paid step (OpenAI), and a failure in one phase does not lose the work done by the previous one.

### Database as processing state

`content` and `ai_summary` double as pipeline state, so no extra state table is needed: an empty `content` means "needs extraction", and a `NULL` `ai_summary` with content means "needs analysis". This makes every phase idempotent and lets incomplete articles be retried automatically.

### The API only exposes fully processed articles

The list endpoint filters on `ai_summary IS NOT NULL` (for both results and totals), so users never see half-processed articles or inconsistent pagination counts.

### Reader/writer separation

The pipeline writes to the database and the API only reads from it. The API has no dependency on OpenAI and can run without an API key.

### Server-side data fetching in the frontend

The Next.js pages fetch from the API on the server. The frontend keeps search, category, and page in the URL, so filtered views are shareable and work with the browser's back button.

## Limitations

Current project scope:

- Content extraction depends on the HTML structure of the source. The extractor and the news URL filter are written for Tecnoblog's page layout and URL structure, so adding other sources would require source-specific extraction.
- The application currently uses a single RSS feed, and the feed contains non-news content that the URL filter has to exclude.
- AI categorization and summaries are probabilistic and may occasionally be imperfect.
- Articles whose content cannot be extracted stay pending and are requested again on every pipeline run.
- Search is a simple substring match over title and RSS summary, not full-text search.
- SQLite is suitable for this project but not necessarily for a high-scale deployment.
- The pipeline is executed manually rather than through a scheduled background worker.
- There are no frontend automated tests; the automated test suite covers the backend.

## Future Improvements

- Scheduled ingestion (running the pipeline periodically)
- More RSS sources, with source-specific content extraction
- Better content filtering
- Improved AI classification
- Frontend tests
- Automated deployment and monitoring
- A production-grade database if the data volume grows

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

Developed by [pitercoding](https://github.com/pitercoding).
