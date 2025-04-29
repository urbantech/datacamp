# 🛍️ BoomScraper: Langflow-Powered Product Scraper Agent

BoomScraper is a modular, AI-orchestrated data ingestion pipeline for scraping e-commerce products from **Shein.com** and **Temu.com**, cleaning the data, and submitting it to the **Boom Marketplace API**.  
Built with **Langflow**, **Python**, and **Playwright**, this system is designed for fast deployment, robust scraping, and simple agent orchestration.

---

## 🚀 Features

- ✅ Scrape full product metadata (title, price, images, description, category)
- ✅ Dynamic rendering with Playwright (for JS-heavy sites)
- ✅ Modular tools: Crawler, Scraper, Cleaner, Validator, API Poster
- ✅ Bot defense: randomized headers, delays, and optional proxy rotation
- ✅ Fully orchestrated using Langflow visual pipelines
- ✅ Ready to scale to category-level ingestion

---

## 🧱 Architecture

```
[URL Input] 
   ↓
[Bot Defense Tool]
   ↓
[Playwright Crawler Tool]
   ↓
[Vendor-Specific Scraper Tool]
   ↓
[Cleaner Tool]
   ↓
[Validator Tool]
   ↓
[API Poster Tool]
   ↓
[Logger Tool]
```

Each component is written in Python and exposed to Langflow as a tool for modular composition.

---

## 🗃️ Data Schema

```json
{
  "title": "Elegant Lace Dress",
  "price_cents": 4299,
  "currency": "USD",
  "images": [
    "https://img.shein.com/path/to/image1.jpg"
  ],
  "category": "Women's Dresses",
  "description": "A stylish lace dress with a flattering fit.",
  "source_url": "https://shein.com/item/123456.html",
  "vendor": "shein"
}
```

---

## 🛠️ Setup Instructions

### 1. Clone & Install

```bash
git clone https://github.com/YOUR-USERNAME/boom-scraper.git
cd boom-scraper
poetry install
```

> You’ll need Python 3.10+ and Playwright dependencies installed:
```bash
poetry run playwright install
```

---

### 2. Run a Tool Locally

```bash
poetry run python tools/crawler_tool.py --url "https://www.shein.com/item/123456.html"
```

---

### 3. Launch Langflow and Import Flow

- Start Langflow:
```bash
langflow run
```

- Import the included flow file:
  `flows/product_scraper_agent.flow.json`

---

## 🚀 Project Overview

BoomScraper is a modular, AI-orchestrated data ingestion pipeline for scraping e-commerce products from Shein.com and Temu.com, cleaning the data, and submitting it to the Boom Marketplace API.

## 🌟 Features

- Dynamic web scraping with Playwright
- Modular, Langflow-compatible architecture
- Bot defense mechanisms
- Comprehensive data validation
- Extensible to multiple e-commerce platforms

## 🛠️ Technology Stack

- **Language**: Python 3.10+
- **Web Scraping**: Playwright
- **Data Validation**: Pydantic
- **API Interaction**: httpx
- **Workflow Orchestration**: Langflow

## 📦 Installation

### Prerequisites
- Python 3.10+
- Poetry

### Setup
```bash
# Clone the repository
git clone https://github.com/your-org/boom-scraper.git
cd boom-scraper

# Install dependencies
poetry install

# Install Playwright browsers
poetry run playwright install
```

## 🧪 Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=tools
```

## 🚀 Usage

### Scraping a Single Product
```bash
poetry run python -m tools.main --url https://www.shein.com/product-page
```

### Langflow Integration
1. Start Langflow
2. Import `flows/product_scraper_agent.flow.json`

## 🔑 Environment Variables

Create a `.env` file in the root directory:

```env
API_URL=https://api.boommarketplace.com/products
API_KEY=your-api-key-here
```

---

## 🧪 Testing

```bash
poetry run pytest tests/
```

All tools are covered with unit tests and end-to-end tests using real and mocked HTML pages.

---

## 🧠 Langflow Integration

All tools are fully Langflow-compatible. You can connect:
- `URL Input → Crawler → Scraper → Cleaner → Validator → API Poster`

> Use `flow.json` in the `flows/` directory to import the full working agent graph.

---

## 📦 File Structure

```
boom-scraper/
├── tools/                 # Langflow-compatible Python tools
│   ├── bot_defense_tool.py
│   ├── crawler_tool.py
│   ├── scraper_tool.py
│   ├── cleaner_tool.py
│   ├── validator_tool.py
│   └── api_poster_tool.py
├── flows/
│   └── product_scraper_agent.flow.json
├── schemas/
│   └── product_schema.py
├── tests/
│   └── test_scraper.py
├── .env.example
├── README.md
└── pyproject.toml
```

---

## 📈 Roadmap

- [ ] Add pagination support for category-level scraping  
- [ ] Integrate proxy rotation pool  
- [ ] Extend to additional e-commerce platforms (AliExpress, Amazon)  
- [ ] Deploy scheduled agent scraping via Celery or Airflow  

---

## 📄 License

MIT License. See [`LICENSE`](./LICENSE) for details.

---

## 🙌 Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 🔒 Security

See our [SECURITY.md](SECURITY.md) for our responsible disclosure policy.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙌 Acknowledgments

- Semantic Seed Engineering Team
- Langflow Community
- Open Source Contributors
