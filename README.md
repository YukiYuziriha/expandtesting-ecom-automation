# End-to-End E-Commerce Automation with Observability

Engineered a production-grade UI test automation framework in Python using Playwright and Pytest to validate a complete e-commerce user journey on [ExpandTesting.com](https://practice.expandtesting.com/).

✅ **P0 Scenario**: Authenticated purchase flow (login → search → cart → checkout → order confirmation)  
✅ **CI**: GitHub Actions with video + HTML report on failure  
✅ **Cross-browser**: Chromium + Firefox  

## Local Setup
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
playwright install --with-deps
```

## Run Tests
```bash
pytest tests/ -v
```