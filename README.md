# End-to-End E-Commerce Automation with Observability

## 🇷🇺 Обзор (Русская версия)

### Одно предложение
> Разработана промышленная UI-автоматизация на Python с Playwright и Pytest для проверки полноценного e-commerce пути пользователя на [ExpandTesting.com](https://practice.expandtesting.com/), с параллельным выполнением, кешированной авторизацией и сбором артефактов в CI/CD.

---

## ► Почему этот проект важен

Этот репозиторий — не просто набор тестовых скриптов, а демонстрация профессиональной стратегии автоматизации, спроектированной как **поддерживаемая, масштабируемая и CI-ориентированная**. Он подтверждает ключевые компетенции современного инженера по автоматизации QA:

* **Архитектурное мышление**: строгий Page Object Model (POM) разделяет тестовую логику и реализацию UI, упрощая сопровождение.
* **Понимание CI/CD**: весь набор тестов запускается в параллельном workflow GitHub Actions для каждого PR, предоставляя быструю обратную связь с артефактами (видео, trace) при сбоях.
* **Устойчивость фреймворка**: локаторы построены на устойчивых атрибутах (`role`, `data-testid`, `type=submit`), а не на хрупких текстах или CSS-классах.
* **Оптимизация производительности**: сессионная фикстура аутентификации (`storage_state` + `FileLock`) устраняет повторные логины и сокращает время прогона более чем на 90%.

---

## ✨ Ключевые возможности и архитектура

| Возможность | Реализация и обоснование |
| :-- | :-- |
| **Page Object Model (POM)** | Строгое разделение ответственности: тесты содержат сценарии и проверки, а Page Objects — локаторы и действия. Это делает тесты читабельными и облегчает поддержку. |
| **Кешированная аутентификация** | Сессионная Pytest-фикстура выполняет вход **один раз за сессию**, сохраняет состояние в файл и создает новый контекст для каждого теста, обеспечивая скорость и **100% изоляцию**. |
| **Устойчивые локаторы** | Стратегия опирается на стабильные атрибуты DOM, описывающие назначение элемента: семантический HTML (`form`, `button[type='submit']`), контракты доступности (`aria-label`) и `data-testid`, а не текст или CSS. |
| **CI/CD Pipeline** | PR запускает полный E2E-набор в матрице браузеров (Chromium + Firefox); push — ускоренный smoke на Chromium. Все джобы загружают trace/video при сбое. Линтер (`ruff`) и типизация (`mypy`) блокируют регрессии. |
| **Наблюдаемость** | Каждый прогон pytest пишет метаданные в `data/test_results.db` (SQLite); скрипт `scripts/ci/sqlite_observability.sh` очищает файл, а CI выгружает БД и артефакты при ошибках. См. `docs/sqlite_observability.md`. |
| **Блокировка рекламы и трекеров** | Сетевое блокирование запросов + закрытие баннеров в DOM обеспечивает стабильную и «чистую» среду тестов. |
| **Наборы по маркерам** | Все тесты помечены маркерами pytest (`smoke`, `ui`, `api`, `e2e`, `bookstore`, `notes`), что позволяет CI запускать целевые срезы, а разработчикам — быстро фильтровать сценарии. |

---

## 🛠️ Технологический стек

| Компонент | Выбор | Почему |
| :-- | :-- | :-- |
| **Язык** | Python 3.12 | Отраслевой стандарт для QA: читаемый и мощный. |
| **Фреймворк** | Playwright + Pytest | Современный, устойчив к флейкам, поддерживает async, автоподстановку ожиданий и встроенный test runner. |
| **CI/CD** | GitHub Actions | Глубокая интеграция с репозиторием, нулевая инфраструктура, простая параллельная конфигурация. |
| **Линтинг и форматирование** | Ruff & MyPy | Обеспечивают качество кода, единообразие и безопасность типов, предотвращая ошибки до слияния. |
| **Параллелизация** | `pytest-xdist` | Существенно сокращает время за счет параллельного запуска тестов. |

---

## 🚀 Локальный запуск и выполнение

### 1. Предварительные требования
* Python 3.12+
* `git`

### 2. Установка
```bash
# 1. Клонируйте репозиторий
git clone https://github.com/YukiYuziriha/expandtesting-ecom-automation.git
cd expandtesting-ecom-automation

# 2. Создайте и активируйте виртуальную среду
python -m venv .venv
source .venv/bin/activate  # или .venv\\Scripts\\activate для Windows

# 3. Установите зависимости
pip install -r requirements.txt

# 4. Установите браузеры Playwright и системные зависимости
playwright install --with-deps
```

### 2.1 Добавьте тестовые учетные данные
Набор ищет креды в переменной окружения `TEST_USERS_JSON` или локальном файле `shared/test_data/test_users.json` (в `.gitignore`). Профили именуются (например, `profile1`, `profile2`); выбрать профиль можно флагом `pytest --profile=<name>`. По умолчанию используется `profile1`.

> ℹ️ Тесты Notes API обращаются к боевому сервису `https://practice.expandtesting.com/notes/api`. Убедитесь, что переданные креды валидны и есть исходящий доступ к сети. Тесты создают временные заметки и очищают их после прогона.

### 2.2 Офлайн-режим Mock API (Notes Tests)
Тесты Notes API могут работать в **офлайн-режиме** с герметичным мок-бэкендом. Полезно для:
- Запуска без внешних сетевых зависимостей
- Локальной разработки и проверки
- Герметичных CI-задач, не зависящих от внешних сервисов

**Включить офлайн-режим:**
```bash
# Запуск Notes API с моками (без сети)
export NOTES_OFFLINE=1
pytest -m "notes and api" -v

# Запуск против реального API
unset NOTES_OFFLINE
pytest -m "notes and api" -v
```

**Что дает мок:**
- In-memory хранилище заметок (CRUD)
- Проверка авторизации (логин, токен, 401 при отсутствии доступа)
- Детеминированные ответы (400/404 для отсутствующих ресурсов, 422 для неверных категорий)
- Негативные сценарии (неверные креды, невалидный payload, ресурс не найден)

Мок **включается автоматически при `NOTES_OFFLINE=1`** и влияет только на тесты с `@pytest.mark.notes`. Остальные тесты работают как обычно.

### 3. Запуск тестов

```bash
# Рекомендованный полный прогон (учет флейков)
# 1) Несеквенциальные тесты в параллели
pytest -m "not seq_only" -v -n auto

# 2) Последовательные тесты
pytest -m "seq_only" -v

# Только smoke (bookstore UI + notes API)
pytest -m "smoke"

# Фокус на конкретной поверхности
pytest -m "bookstore and ui"
pytest -m "notes and api"

# Запуск файла с UI (headed для отладки)
pytest bookstore/tests/test_purchase_journey.py --headed

# Тесты в конкретном браузере
pytest tests/ -v --browser firefox

# Переключение профиля пользователя (по умолчанию profile1)
pytest -k login --profile=profile2
```

-----

## 🧭 CI обзор

- Push (fast): только smoke
  - Bookstore UI и Notes UI на одном браузере (Chromium), параллельно, без `seq_only`.
  - Notes API smoke (без Playwright).
- Pull Request (full): полный охват
  - Bookstore UI в матрице Chromium + Firefox.
  - Notes UI: два параллельных контура — (1) параллельный для всего, кроме `seq_only`, и (2) последовательный для `seq_only` с отдельными профилями на браузер.
  - Notes Hybrid UI+API: отдельная джоба с `-m "hybrid"`, матрица Chromium + Firefox, параллельно остальному.
  - Notes API: полный набор.
- Артефакты: при любом сбое CI загружает traces, видео, скриншоты для быстрой отладки.

Зачем: быстрые push-прогоны ускоряют итерации и снижают флейки от сторонних сервисов. PR получают полный confidence с мультибраузерными матрицами. `seq_only` группирует потоки (например, logout), которые могут инвалидировать сессии; отдельные пользователи сохраняют изоляцию и сокращают время.

Подробнее: см. `docs/decisions/ci-operations.md` и `docs/decisions/notes-app-session-behavior.md`.

## 📺 Демонстрация

[![Смотреть демо](https://img.youtube.com/vi/YlflQdfF60c/0.jpg)](https://youtu.be/YlflQdfF60c)

20-секундный показ авторизованного пути покупки в локальном `--headed` режиме.

---

## 🇬🇧 English Version

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

| Feature                  | Implementation & Rationale                                                      |
| :----------------------- | :------------------------------------------------------------------------------------------------------------------- |
| **Page Object Model (POM)** | Strict separation of concerns. Tests contain workflows and assertions; Page Objects contain locators and actions. This makes tests readable and the framework easy to maintain.                                                   |
| **Cached Authentication** | A session-scoped Pytest fixture logs in **once per session**, saving the state to a file. Each test then creates a new, isolated browser context from this state, achieving both **speed and 100% test isolation**.                                                   |
| **Resilient Locators** | The locator strategy is anchored to the **most stable attributes** of the DOM—those that define an element's *purpose*, not its appearance. This means prioritizing semantic HTML (`form`, `button[type='submit']`), accessibility contracts (`aria-label`), and developer test hooks (`data-testid`) over brittle selectors like CSS classes or UI text. |
| **CI/CD Pipeline** | PRs run the full E2E suite in a two‑browser matrix (Chromium + Firefox). Pushes run a fast smoke subset on a single browser (Chromium) to keep feedback under ~6 minutes. All jobs upload trace/video artifacts on failure. Linting (`ruff`) and type‑checking (`mypy`) gate regressions. |
| **Observability** | Every pytest run logs metadata into `data/test_results.db` via SQLite; the helper script `scripts/ci/sqlite_observability.sh` keeps the file clean per run, and CI uploads the DB (plus videos/traces/screens) on failure for fast forensic analysis. See `docs/sqlite_observability.md`. |
| **Ad & Tracker Blocking** | A layered defense combines network-level request blocking with DOM-level ad dismissal to create a stable, noise-free test environment.                                                          |
| **Marker-Driven Suites** | All tests are tagged with pytest markers (`smoke`, `ui`, `api`, `e2e`, `bookstore`, `notes`) so CI can run targeted suites and developers can slice the matrix locally with a single flag. |

---

## 🛠️ Tech Stack

| Component         | Choice            | Why                                         |
| :---------------- | :---------------- | :-------------------------------------------------------------------------------- |
| **Language** | Python 3.12       | Industry standard for QA; readable and powerful.                                    |
| **Framework** | Playwright + Pytest | Modern, async-aware, with minimal flakiness and rich features like auto-waits, tracing, and a first-class test runner.         |
| **CI/CD** | GitHub Actions    | Tightly integrated with the repository, zero infrastructure overhead, and easily configurable for parallel, cross-browser execution. |
| **Linting & Formatting** | Ruff & MyPy       | Enforces code quality, consistency, and type safety, preventing common errors before they merge.                               |
| **Parallelization** | `pytest-xdist`    | Significantly reduces pipeline execution time by running tests concurrently.                                          |

---

## 🚀 Local Setup & Execution

### **1. Prerequisites**
* Python 3.12+
* `git`

### **2. Installation**
```bash
# 1. Clone the repository
git clone [https://https://github.com/YukiYuziriha/expandtesting-ecom-automation/tree/refactor-pom](https://github.com/YukiYuziriha/expandtesting-ecom-automation/tree/refactor-pom)
cd expandtesting-ecom-automation

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers and system dependencies
playwright install --with-deps
````

### **2.1 Provide Test Credentials**
The suite looks for credentials in the `TEST_USERS_JSON` environment variable or a local `shared/test_data/test_users.json` file (git-ignored). Profiles are keyed by name (e.g., `profile1`, `profile2`), and you can select one at runtime with `pytest --profile=<name>`. If no profile is specified, `profile1` is used by default.

> ℹ️ Notes API tests exercise the live service at `https://practice.expandtesting.com/notes/api`. Make sure the credentials you supply are valid for that environment and that outbound network access is available. Tests create temporary notes and the fixtures clean them up automatically after each run.

### **2.2 Offline Mock API Mode (Notes Tests)**
The Notes API tests can run in **offline mode** using a hermetic, mocked API backend. This is useful for:
- Running tests without external network dependencies
- Local development and verification
- Hermetic CI jobs that don't rely on external services

**Enable offline mode:**
```bash
# Run Notes API tests with mocked backend (no network required)
export NOTES_OFFLINE=1
pytest -m "notes and api" -v

# Run without offline mode (hit real API)
unset NOTES_OFFLINE
pytest -m "notes and api" -v
```

**What the mock provides:**
- In-memory store for notes (CRUD operations)
- Auth validation (login, token checks, 401 for unauthorized access)
- Deterministic responses (400/404 for missing resources, 422 for invalid categories)
- Negative test coverage (wrong credentials, invalid payloads, resource not found)

The mock is **automatically enabled when `NOTES_OFFLINE=1`** and only affects tests marked with `@pytest.mark.notes`. All other tests run normally.

### **3. Running Tests**

```bash
# Recommended full run (flakiness-aware)
# 1) Run non-sequential tests in parallel for speed
pytest -m "not seq_only" -v -n auto

# 2) Then run sequential-only tests (these can invalidate global session state)
pytest -m "seq_only" -v

# Run only smoke checks (bookstore UI + notes API)
pytest -m "smoke"

# Focus on a specific surface
pytest -m "bookstore and ui"
pytest -m "notes and api"

# Run tests in a specific file (headed, for debugging)
pytest bookstore/tests/test_purchase_journey.py --headed

# Run tests only in a specific browser
pytest tests/ -v --browser firefox

# Switch the active test user profile (defaults to profile1)
pytest -k login --profile=profile2
```

-----

## 🧭 CI at a Glance

- Push (fast): smoke tests only
  - Bookstore UI and Notes UI on a single browser (Chromium), parallelized, excluding `seq_only` to avoid session cross‑talk.
  - Notes API smoke (no browser dependency).
- Pull Request (full): complete coverage
  - Bookstore UI on Chromium + Firefox in parallel.
  - Notes UI runs two matrices concurrently: (1) parallel matrix for all non‑`seq_only` with `--profile profile1`, and (2) a sequential matrix for `seq_only` (Firefox → `profile2`, Chromium → `profile3`).
  - Notes Hybrid UI+API runs as a dedicated job concurrently (Chromium + Firefox), filtered with `-m "hybrid"`, using `--profile profile1`.
  - Notes API full.
- Artifacts: for any failure, CI uploads Playwright traces, videos, and screenshots for fast debugging.

Why: Short push runs keep iteration snappy and reduce exposure to third‑party flakiness. PRs get full, multi‑browser confidence. `seq_only` groups flows like logout can invalidate sessions; running them concurrently in a separate matrix with distinct user profiles preserves isolation while reducing wall‑clock time.

Details: see docs/decisions/ci-operations.md and docs/decisions/notes-app-session-behavior.md

## 📺 Live Demo

[![Watch the demo](https://img.youtube.com/vi/YlflQdfF60c/0.jpg)](https://youtu.be/YlflQdfF60c)

A 20-second walkthrough of the authenticated purchase journey running locally with `--headed` mode.
