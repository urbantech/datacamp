# 📚 Project Rules: BoomScraper

## 🎯 Project Overview
- **Project Name**: BoomScraper
- **Purpose**: E-commerce product scraping pipeline
- **Tech Stack**: Python, Langflow, Playwright
- **Target Platforms**: Shein.com, Temu.com

## 📋 Coding Standards

### 1. File Structure
```
boom-scraper/
├── tools/                 # Langflow-compatible Python tools
│   ├── bot_defense_tool.py
│   ├── crawler_tool.py
│   ├── scraper_tool.py
│   ├── cleaner_tool.py
│   ├── validator_tool.py
│   └── api_poster_tool.py
├── flows/                # Langflow flow definitions
│   └── product_scraper_agent.flow.json
├── schemas/             # Data schemas and models
│   └── product_schema.py
├── tests/              # Test files
│   ├── test_crawler.py
│   ├── test_scraper.py
│   └── test_api.py
├── utils/              # Utility functions
│   ├── logger.py
│   └── config.py
├── docs/              # Documentation
│   ├── architecture.md
│   └── api.md
└── .env.example       # Environment variables template
```

### 2. Code Style
- Follow PEP 8 style guide
- Use black for code formatting
- Maximum line length: 100 characters
- Use type hints for all functions and classes
- Docstrings for all public functions and classes

### 3. Naming Conventions
- **Files**: snake_case.py
- **Classes**: PascalCase
- **Functions**: snake_case
- **Variables**: snake_case
- **Constants**: UPPER_SNAKE_CASE

### 4. Error Handling
- Use custom exceptions for domain-specific errors
- Implement proper logging for all errors
- Add retry logic for external service calls
- Use context managers for resource management

### 5. Testing Requirements
- Minimum test coverage: 90%
- Unit tests for all tools
- Integration tests for Langflow flows
- Mock tests for API interactions
- Test fixtures for HTML samples

### 6. Version Control
- Main branch: `main`
- Feature branches: `feature/<description>`
- Hotfix branches: `hotfix/<description>`
- Pull request template required
- Code review required for all changes

### 7. Documentation
- All tools must have docstrings
- Maintain README.md with setup instructions
- Document API endpoints and schemas
- Keep PRD and Sprint Plan up to date

### 8. Environment Management
- Use Poetry for dependency management
- Maintain pyproject.toml with all dependencies
- Use .env for configuration
- Keep .env.example up to date

### 9. Security
- Never commit API keys or sensitive data
- Use environment variables for configuration
- Implement proper input validation
- Follow secure coding practices

### 10. Performance
- Implement proper rate limiting
- Use async/await where appropriate
- Optimize memory usage
- Monitor and log performance metrics

## 📝 Commit Message Guidelines
```
<type>(<scope>): <description>

[optional body]
[optional footer(s)]
```

### Type
- feat: new feature
- fix: bug fix
- docs: documentation changes
- style: code style changes
- refactor: code refactoring
- test: adding missing tests
- chore: maintenance changes

### Scope
- tools: changes to scraping tools
- flows: changes to Langflow flows
- schemas: changes to data schemas
- tests: changes to test files
- docs: changes to documentation
- utils: changes to utility functions

## 🚀 Deployment
- All code must be reviewed before deployment
- Run full test suite before deployment
- Update documentation before deployment
- Follow semantic versioning

## 🛠️ Tool Requirements
- Python 3.10+
- Poetry for dependency management
- Langflow for pipeline orchestration
- Playwright for web scraping
- Pydantic for data validation
- pytest for testing

## 📝 Code Review Checklist
- [ ] Follows coding standards
- [ ] Proper error handling
- [ ] Adequate test coverage
- [ ] Documentation updated
- [ ] Security considerations addressed
- [ ] Performance optimized
- [ ] Logging implemented

## 🚨 Important Notes
1. All code changes must be accompanied by tests
2. Documentation must be updated with code changes
3. Security reviews required for sensitive changes
4. Performance testing required for critical paths
5. Logging must be implemented for all operations

## 📝 Change Log
- 2025-04-29: Initial project ruleset created
- [Add future updates here]
