# 🏗️ Sprint Plan: Product Scraper Agent (BoomScraper)

**Project Codename**: `BoomScraper`
**Duration**: 5 weeks (Agile sprints)
**Team**: 2–3 engineers (Python + Langflow experience)
**Methodology**: Agile Scrum + TDD/BDD + Langflow modular components
**Repo**: `boom-scraper` (private GitHub)

---

## 📅 Sprint Overview

| Sprint | Goal | Duration | Key Deliverables |
|--------|------|----------|------------------|
| **Sprint 1** | Scaffolding + Crawler | 1 week | Crawler Tool (Playwright), basic CLI test runner |
| **Sprint 2** | Scraper + Cleaner | 1 week | Raw HTML → Structured Data + Schema Normalizer |
| **Sprint 3** | API Poster + Validator | 1 week | Posting Tool + Pydantic Schema + Mock API coverage |
| **Sprint 4** | Langflow Integration | 1 week | Full Langflow flow + connected tools |
| **Sprint 5** | Logging, Retry, QA | 1 week | Final polish + testing + internal demo |

---

## 🧠 Sprint 1: Scaffolding + Playwright Crawler

### 🎯 Goals
- Set up Python repo
- Build `CrawlerTool` with Playwright
- Add randomized headers & delay config
- Prepare Langflow-ready base class interface

### 📝 Stories
| ID | Story | Points |
|----|-------|--------|
| BS-1 | Set up Python repo with Poetry + CI | 1 |
| BS-2 | Implement `BotDefenseTool` (headers, delay) | 2 |
| BS-3 | Create `PlaywrightCrawlerTool` to return HTML | 3 |
| BS-4 | Add `ToolInterface` base class | 1 |
| BS-5 | Write unit tests for crawler using fixture URLs | 2 |

**Total Points**: 9

---

## 🧠 Sprint 2: Scraper + Cleaner Tool

### 🎯 Goals
- Parse product fields from Shein and Temu HTML
- Normalize output to standard schema
- Handle vendor-specific quirks

### 📝 Stories
| ID | Story | Points |
|----|-------|--------|
| BS-6 | Build `SheinScraperTool` (HTML → raw fields) | 2 |
| BS-7 | Build `TemuScraperTool` (HTML → raw fields) | 2 |
| BS-8 | Create `CleanerTool` for normalization (price_cents, category) | 3 |
| BS-9 | Add test coverage for malformed HTML edge cases | 2 |

**Total Points**: 9

---

## 🧠 Sprint 3: API Poster + Validator

### 🎯 Goals
- Define output schema (Pydantic)
- Build validation layer
- Implement REST API poster tool

### 📝 Stories
| ID | Story | Points |
|----|-------|--------|
| BS-10 | Define `ProductSchema` with `pydantic` | 1 |
| BS-11 | Build `ValidatorTool` for schema validation | 2 |
| BS-12 | Build `APIPosterTool` using `httpx` | 2 |
| BS-13 | Handle auth headers, token config | 1 |
| BS-14 | Write API mock server test suite | 3 |

**Total Points**: 9

---

## 🧠 Sprint 4: Langflow Graph Assembly

### 🎯 Goals
- Import flow.json
- Wire all tools together visually
- Validate data from input → POST

### 📝 Stories
| ID | Story | Points |
|----|-------|--------|
| BS-15 | Create `flow.json` from modular nodes | 1 |
| BS-16 | Integrate all Tools into Langflow UI | 2 |
| BS-17 | Test end-to-end flow inside Langflow (single URL) | 3 |
| BS-18 | Add output logs for debugging | 2 |

**Total Points**: 8

---

## 🧠 Sprint 5: Logging, Retry Logic, QA

### 🎯 Goals
- Add logging + retry on failure
- Test batch runs
- Internal demo and feedback loop

### 📝 Stories
| ID | Story | Points |
|----|-------|--------|
| BS-19 | Build `LoggerTool` for event logs | 1 |
| BS-20 | Add retry handler to API Poster (up to 3 tries) | 2 |
| BS-21 | Create CLI runner for multi-URL scrape | 2 |
| BS-22 | Run QA tests on 20 Shein + 20 Temu URLs | 3 |
| BS-23 | Prep demo + internal walkthrough | 1 |

**Total Points**: 9

---

## 📈 Total Points Summary

| Sprint | Story Points |
|--------|--------------|
| Sprint 1 | 9 |
| Sprint 2 | 9 |
| Sprint 3 | 9 |
| Sprint 4 | 8 |
| Sprint 5 | 9 |

**Total**: **44 points** (fits 2 developers across 5 weeks)

---

## ✅ Dev Practices

- 🧪 All tools must be unit tested (TDD)
- 🧠 Follow SSCS modular file structure (`/tools`, `/flows`, `/schemas`, `/tests`)
- 🚀 Each Langflow Tool gets a test fixture + visual validation
- 📦 PRs gated by test pass + `black` formatting

---
