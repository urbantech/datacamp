# 🧠 PRD: Product Scraper Agent (Shein + Temu)
**Project Codename**: `BoomScraper`
**Owner**: Data Engineering Team
**Date**: April 2025
**Platform**: Langflow + Python

---

## 📋 Executive Summary

We are developing a modular, Langflow-powered agent that ingests product data from e-commerce platforms **Shein.com** and **Temu.com**, performs **data cleaning and normalization**, and posts the structured data to a RESTful API powering the **Boom Marketplace**.

The agent accepts a **product or category URL**, performs dynamic web scraping (handling JavaScript), and addresses anti-bot protections using randomized headers, delays, and proxy support. It is modular, testable, and deployable with minimal configuration. Langflow enables visual flow orchestration and rapid tool chaining.

---

## 🎯 Objectives

- Ingest product data from Shein and Temu (via URL)
- Normalize and clean the data to a fixed schema
- Handle bot protection measures and dynamic content
- POST data to Boom’s backend via API
- Operate modularly via Langflow and Python tools
- Log all activity for observability and debugging
- Ready for production batch mode scraping in future phases

---

## 🛠️ Architecture Overview

### High-Level Flow:
```
[URL Input]
    ↓
[Bot Defense Tool]
    ↓
[Crawler Tool]
    ↓
[Scraper Tool]
    ↓
[Cleaner Tool]
    ↓
[Validator Tool]
    ↓
[API Poster Tool]
    ↓
[Logger Tool]
```

Each tool is a self-contained Python class, wrapped as a Langflow-compatible node.

---

## 🧩 Component Responsibilities

| Component | Description |
|----------|-------------|
| **URL Input Tool** | Accepts Shein or Temu URL from user |
| **Bot Defense Tool** | Adds randomized User-Agent headers and delay between requests |
| **Crawler Tool** | Uses Playwright to render JavaScript-heavy pages and return HTML |
| **Scraper Tool** | Parses HTML to extract product fields (title, price, images, etc.) |
| **Cleaner Tool** | Normalizes and transforms raw fields to match schema |
| **Validator Tool** | Validates cleaned data against a strict schema using Pydantic |
| **API Poster Tool** | Posts data to Boom Marketplace’s REST API |
| **Logger Tool** | Logs success, failure, and retry information to stdout or file |

---

## 📦 Data Schema (Normalized Output)

```json
{
  "title": "Elegant Lace Dress",
  "price_cents": 4299,
  "currency": "USD",
  "images": [
    "https://img.shein.com/path/to/image1.jpg",
    "https://img.shein.com/path/to/image2.jpg"
  ],
  "category": "Women's Dresses",
  "description": "A stylish lace dress with a flattering fit.",
  "source_url": "https://www.shein.com/item/123456.html",
  "vendor": "shein"
}
```

---

## ⚠️ Technical Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Bot Detection (CAPTCHA, blocks) | Randomized User-Agent + proxy support + headless Playwright |
| Dynamic JavaScript content | Rendered with Playwright (not raw HTTP requests) |
| Rate limiting | Add jittered request delay (2–10s) per domain |
| Site layout changes | Use vendor-specific scraper classes (`SheinScraper`, `TemuScraper`) for easy updates |
| Data inconsistency | Use strict schema validation (`pydantic`) before sending to API |
| API downtime | Add retries with exponential backoff; log failed payloads |
| Proxy pool exhaustion (future) | Integrate proxy rotation service (ScraperAPI, BrightData) if scale increases |

---

## 🔁 Workflow Mode

- **MVP**: One product URL at a time
- **Phase 2**: Crawl categories (pagination)
- **Phase 3**: Daily scheduled scraping via queue/agent runner

---

## 🧪 Testing & QA

| Layer | Tests |
|-------|-------|
| Scraper Tool | Unit tests for Shein & Temu HTML fixtures |
| Cleaner Tool | Tests for malformed inputs, currency normalization, etc. |
| API Poster | Mock server tests for request/response validation |
| End-to-end | Langflow graph test with simulated full run |

---

## 🚀 MVP Timeline

| Week | Deliverable |
|------|-------------|
| Week 1 | Tool specs, crawler + scraper working |
| Week 2 | Data cleaning + schema validation |
| Week 3 | Langflow integration with modular tools |
| Week 4 | Logging, retries, error handling, internal demo |
| Week 5 | Production run test with 20 URLs from each site |

---

## 🔧 Requirements

- Python 3.10+
- `playwright`, `beautifulsoup4`, `pydantic`, `httpx`, `langflow`
- RESTful API credentials for posting data

---

## ✅ Success Criteria

- Scrapes and posts at least 100 product pages from Shein/Temu with <5% error rate
- Clean JSON matches defined schema
- Scraper modular and reusable for future vendors
- Graph is importable and runnable via Langflow UI

---
