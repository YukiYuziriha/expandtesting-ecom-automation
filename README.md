
# End-to-End E-Commerce Automation with Observability

### One-Sentence Summary
> Engineered a production-grade UI test automation framework in Python using Playwright and Pytest to validate a complete e-commerce user journey on [ExpandTesting.com](https://practice.expandtesting.com/), featuring parallel execution, cached authentication, and artifact reporting in a CI/CD pipeline.

[![CI Pipeline](https://github.com/YukiYuziriha/expandtesting-ecom-automation/actions/workflows/ci.yml/badge.svg)](https://github.com/YukiYuziriha/expandtesting-ecom-automation/actions)

---

## ► Why This Project Matters

This isn't just a collection of test scripts; it's a demonstration of a professional automation strategy designed to be **maintainable, scalable, and CI-native**. It directly addresses the core competencies required for a modern QA Automation Engineer role by proving:

* **Architectural Thinking**: A strict Page Object Model (POM) ensures the framework is maintainable and separates test logic from UI implementation.
* **CI/CD Proficiency**: The entire test suite runs in a parallelized GitHub Actions workflow on every PR, providing fast feedback with video and trace artifacts on failure.
* **Framework Resilience**: Locators are built to be "apocalypse-proof," relying on semantic and structural selectors (`role`, `data-testid`, `type=submit`) rather than brittle UI text or CSS classes.
* **Performance Optimization**: Implements a session-scoped, cached authentication fixture (`storage_state` with `FileLock`), eliminating repetitive UI logins and reducing total execution time by over 90%.

---

## ✨ Key Features & Architecture

| Feature                  | Implementation & Rationale                                                                                                                                                                                                                                                               |
| :----------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Page Object Model (POM)** | Strict separation of concerns. Tests contain workflows and assertions; Page Objects contain locators and actions. This makes tests readable and the framework easy to maintain.                                                                                                    |
| **Cached Authentication** | A session-scoped Pytest fixture logs in **once per session**, saving the state to a file. Each test then creates a new, isolated browser context from this state, achieving both **speed and 100% test isolation**.                                                                  |
| **Resilient Locators** | The locator strategy is anchored to the **most stable attributes** of the DOM—those that define an element's *purpose*, not its appearance. This means prioritizing semantic HTML (`form`, `button[type='submit']`), accessibility contracts (`aria-label`), and developer test hooks (`data-testid`) over brittle selectors like CSS classes or UI text. |
| **CI/CD Pipeline** | A GitHub Actions workflow runs on every push and PR, executing the full E2E suite in parallel across Chromium and Firefox. It includes linting (`ruff`) and type-checking (`mypy`) gates.                                                                                             |
| **Observability** | On test failure, the CI pipeline automatically uploads **video recordings**, **Playwright traces**, and **screenshots** as artifacts, enabling rapid, precise debugging without needing to re-run locally.                                                                          |
| **Ad & Tracker Blocking** | A layered defense combines network-level request blocking with DOM-level ad dismissal to create a stable, noise-free test environment.                                                                                                                                                      |

---

## 🛠️ Tech Stack

| Component         | Choice            | Why                                                                                                                            |
| :---------------- | :---------------- | :----------------------------------------------------------------------------------------------------------------------------- |
| **Language** | Python 3.12       | Industry standard for QA; readable and powerful.                                                                               |
| **Framework** | Playwright + Pytest | Modern, async-aware, with minimal flakiness and rich features like auto-waits, tracing, and a first-class test runner.         |
| **CI/CD** | GitHub Actions    | Tightly integrated with the repository, zero infrastructure overhead, and easily configurable for parallel, cross-browser execution. |
| **Linting & Formatting** | Ruff & MyPy       | Enforces code quality, consistency, and type safety, preventing common errors before they merge.                               |
| **Parallelization** | `pytest-xdist`    | Significantly reduces pipeline execution time by running tests concurrently.                                                  |

---

## 🚀 Local Setup & Execution

### **1. Prerequisites**
* Python 3.12+
* `git`

### **2. Installation**
```bash
# 1. Clone the repository
git clone [https://github.com/YOUR_USERNAME/expandtesting-ecom-automation.git](https://github.com/YOUR_USERNAME/expandtesting-ecom-automation.git)
cd expandtesting-ecom-automation

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers and system dependencies
playwright install --with-deps
````

### **3. Running Tests**

```bash
# Run all tests in parallel (headless)
pytest tests/ -v -n auto

# Run tests in a specific file (headed, for debugging)
pytest tests/test_purchase_journey.py --headed

# Run tests only in a specific browser
pytest tests/ -v --browser firefox
```

-----

## 📺 Live Demo

*[A live demo is not currently available. The test is fully observable via CI artifacts on failure.]*

```
```