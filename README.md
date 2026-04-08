# Amazon Price Tracker

Scrapes an Amazon product page and sends an email alert when the price drops below a target threshold.

Point the script at any Amazon product URL, set a target price, and run it manually or on a daily schedule. When the live price dips below your threshold, you receive an email instantly — subject line "Amazon Price Alert!" with the current price and a direct link to buy.

There are two builds. The **original** build is a single flat script that follows the course exercise exactly: it fetches the page, pulls the price with BeautifulSoup, and fires off an email via `smtplib` — all in one file, top to bottom. The **advanced** build reorganises the same logic into three clean modules (`scraper.py`, `notifier.py`, `config.py`) with all magic numbers extracted into constants, credentials loaded from `.env`, and a `main.py` orchestrator that wires them together. Both builds produce identical behaviour; the difference is structure and maintainability.

This project uses two external services. **Amazon** provides the product page that is scraped for the live price. **Gmail SMTP** (via Google App Passwords) is used to send the alert email without exposing your main account password.

---

## Table of Contents

- [0. Prerequisites](#0-prerequisites)
- [1. Quick start](#1-quick-start)
- [2. Builds comparison](#2-builds-comparison)
- [3. Usage](#3-usage)
- [4. Data flow](#4-data-flow)
- [5. Features](#5-features)
- [6. Navigation flow](#6-navigation-flow)
- [7. Architecture](#7-architecture)
- [8. Module reference](#8-module-reference)
- [9. Configuration reference](#9-configuration-reference)
- [10. Data schema](#10-data-schema)
- [11. Environment variables](#11-environment-variables)
- [12. Design decisions](#12-design-decisions)
- [13. Course context](#13-course-context)
- [14. Dependencies](#14-dependencies)

---

## 0. Prerequisites

### Gmail App Password

An App Password lets the script authenticate to Gmail without using your real account password. Two-Factor Authentication must be enabled on your Google account first.

**Creating an App Password:**
- Go to myaccount.google.com → Security → How you sign in to Google
- → 2-Step Verification → App passwords (at the bottom of the page)
- → Select app: Mail → Select device: Other → Generate
- Copy the 16-character password shown (spaces are ignored).

| .env variable | Where to find it |
|---|---|
| `SMTP_ADDRESS` | Always: `smtp.gmail.com` |
| `EMAIL_ADDRESS` | Your full Gmail address (e.g. you@gmail.com) |
| `EMAIL_PASSWORD` | The 16-character App Password generated above |
| `TARGET_EMAIL` | The email address that should receive the alert |

**Gotcha:** App Passwords only appear if 2FA is enabled on the account.  
**Gotcha:** Gmail limits to ~500 emails/day on free accounts.

---

## 1. Quick start

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your Gmail credentials
python menu.py         # select 1 (original) or 2 (advanced)
```

Or run a build directly:

```bash
python original/main.py
python advanced/main.py
```

---

## 2. Builds comparison

| Feature | Original | Advanced |
|---|---|---|
| File structure | Single flat script | Separate modules |
| Config | Hardcoded constants in script | `config.py` — single source of truth |
| Scraping | Inline `requests` + BeautifulSoup | `AmazonScraper` class |
| Email | Inline `smtplib` call | `EmailNotifier` class |
| Credentials | Loaded from `.env` via `dotenv` | Loaded from `.env` via `dotenv` |
| Price parsing | Regex helper function | `AmazonScraper._parse_price()` static method |
| EU/US price formats | Supported | Supported |
| Error handling | try/except around SMTP | Raises exceptions; `main.py` catches them |
| GitHub Actions | — | Daily schedule included |
| Entry point | `original/main.py` | `advanced/main.py` |

---

## 3. Usage

```
python menu.py
```

```
   ___
  / _ \  _ __ ___    __ _  ____   |  _ \ _ __(_) ___ ___
 ...

1. Original build  (course version)
2. Advanced build  (OOP, config.py, modular)
q. Quit

Select an option:
```

Select `1` or `2` to run a build. Press Enter to return to the menu when done.

**Example output (price above target):**

```
Current price: $129.99
No alert — price ($129.99) is above target ($100.00).
```

**Example output (price below target):**

```
Current price: $89.99
Price is below target ($100.00). Sending alert...
Alert sent successfully.
```

---

## 4. Data flow

```
Input (config)
  └─ PRODUCT_URL, BROWSER_HEADERS, TARGET_PRICE, SMTP credentials

Fetch
  └─ requests.get(url, headers=browser_headers)
  └─ Response: raw HTML string

Parse
  └─ BeautifulSoup finds <span class="aok-offscreen">
  └─ Regex extracts price string (handles $, €, £, EU/US decimals)
  └─ Output: float (e.g. 129.99)

Decide
  └─ price < TARGET_PRICE?
     ├─ Yes → send email alert
     └─ No  → print "No alert" and exit

Output
  └─ smtplib sends email via Gmail SMTP (port 587, STARTTLS)
  └─ Subject: "Amazon Price Alert!"
  └─ Body: current price, target price, product URL
```

---

## 5. Features

**Browser-spoofing headers** — The scraper sends a full set of browser headers (User-Agent, Accept, Sec-Fetch-*) so Amazon serves a real product page rather than a bot-detection wall.

**EU and US price format support** — The price parser uses regex to handle both comma-decimal (€59,99) and dot-decimal ($129.99) formats, including thousands separators (€1.299,99 → 1299.99).

**STARTTLS email** — Email is sent over an encrypted STARTTLS connection on port 587, never plain text. Credentials are loaded from `.env` and never hardcoded.

**Advanced-only: modular OOP design** — `AmazonScraper` and `EmailNotifier` are independent classes. Each can be instantiated, tested, or swapped without touching the other.

**Advanced-only: GitHub Actions daily schedule** — The workflow runs `advanced/main.py` every day at 07:00 Madrid time (CET). Secrets are injected from the GitHub repository settings.

**Advanced-only: clean error propagation** — Modules raise typed exceptions (`ValueError`, `RuntimeError`). `main.py` catches them and prints a clean message — the script never crashes silently.

---

## 6. Navigation flow

### a) Terminal menu tree

```
python menu.py
│
├─ 1 ──► original/main.py  (course build)
│         └─ returns → Press Enter → menu redraws
│
├─ 2 ──► advanced/main.py  (OOP build)
│         └─ returns → Press Enter → menu redraws
│
└─ q ──► exit
```

### b) Execution flow

```
Start
  │
  ▼
Load .env credentials
  │
  ▼
requests.get(PRODUCT_URL, headers=BROWSER_HEADERS)
  │
  ├─ HTTP error → raise HTTPError → caught in main → print error → exit
  │
  ▼
BeautifulSoup.find("span", class_="aok-offscreen")
  │
  ├─ element not found → raise ValueError → caught in main → print error → exit
  │
  ▼
_parse_price(text)
  │
  ├─ regex no match → raise ValueError → caught in main → print error → exit
  │
  ▼
price < TARGET_PRICE?
  │
  ├─ No  → print "No alert" → exit cleanly
  │
  └─ Yes → smtplib.SMTP(SMTP_ADDRESS, 587)
              │
              ├─ Auth error → raise ValueError → caught in main → print error → exit
              ├─ SMTP error → raise RuntimeError → caught in main → print error → exit
              │
              └─ Success → print "Alert sent" → exit cleanly
```

---

## 7. Architecture

```
day47-amazon-price-tracker/
│
├── menu.py                    # entry point — draws menu, launches builds
├── art.py                     # LOGO constant for menu display
├── requirements.txt           # pip dependencies + Python version note
├── .gitignore
├── .env.example               # template for required environment variables
├── README.md
│
├── original/
│   └── main.py                # verbatim course script
│
├── advanced/
│   ├── config.py              # all constants (URL, headers, threshold, SMTP port)
│   ├── scraper.py             # AmazonScraper — fetch + parse price
│   ├── notifier.py            # EmailNotifier — send SMTP alert
│   └── main.py                # orchestrator — wires modules together
│
├── docs/
│   └── COURSE_NOTES.md        # original exercise description and variant notes
│
└── .github/
    └── workflows/
        └── amazon-price-tracker.yml   # daily GitHub Actions schedule
```

---

## 8. Module reference

### `advanced/scraper.py` — `AmazonScraper`

| Method | Returns | Description |
|---|---|---|
| `__init__(url, headers)` | — | Initialises with product URL and browser headers from `config.py`. Both parameters are optional and default to config values. |
| `get_price()` | `float` | Fetches the product page and returns the current price. Raises `requests.HTTPError` on bad response, `ValueError` if the price element or a parseable price string is not found. |
| `_parse_price(text)` *(static)* | `float` | Extracts and normalises a price string. Handles $, €, £ symbols and both EU/US decimal formats. Raises `ValueError` if no valid price pattern is found. |

### `advanced/notifier.py` — `EmailNotifier`

| Method | Returns | Description |
|---|---|---|
| `__init__(smtp_address, sender, password, recipient)` | — | Stores SMTP credentials. No connection is opened at init time. |
| `send_alert(current_price)` | `bool` | Sends the price-drop email via STARTTLS SMTP. Returns `True` on success. Raises `ValueError` on auth failure, `RuntimeError` on other SMTP errors. |

---

## 9. Configuration reference

| Constant | Default | Description |
|---|---|---|
| `PRODUCT_URL` | Amazon Instant Pot URL | The product page to scrape |
| `BROWSER_HEADERS` | Firefox 143 on macOS | Headers sent with every request to avoid bot detection |
| `PRICE_CSS_CLASS` | `"aok-offscreen"` | CSS class of the `<span>` containing the price |
| `TARGET_PRICE` | `100.00` | USD threshold — alert fires when price drops below this |
| `SMTP_PORT` | `587` | STARTTLS port for Gmail SMTP |
| `ROOT_DIR` | `Path(__file__).parent.parent` | Absolute path to repo root, used by `main.py` to locate `.env` |

---

## 10. Data schema

### Page price element (scraped HTML)

```html
<span class="aok-offscreen">$129.99</span>
```

The regex pattern handles all of these:

| Raw string | Parsed float |
|---|---|
| `$129.99` | `129.99` |
| `$1,299.99` | `1299.99` |
| `€59,99` | `59.99` |
| `€1.299,99` | `1299.99` |

### Email alert

```
Subject: Amazon Price Alert!

The Instant Pot is now $89.99 — below your target of $100.00!
Check it here: https://www.amazon.com/dp/B075CYMYK6?...
```

---

## 11. Environment variables

Copy `.env.example` to `.env` and fill in values.

| Variable | Required | Description |
|---|---|---|
| `SMTP_ADDRESS` | Yes | SMTP server hostname (e.g. `smtp.gmail.com`) |
| `EMAIL_ADDRESS` | Yes | Gmail address used to send the alert |
| `EMAIL_PASSWORD` | Yes | 16-character Gmail App Password |
| `TARGET_EMAIL` | Yes | Recipient address for the alert email |

---

## 12. Design decisions

**`config.py` — zero magic numbers** — Every constant (URL, price threshold, SMTP port, browser headers) lives in one file. Changing the monitored product or target price requires editing exactly one line.

**Separate `scraper.py` and `notifier.py`** — Fetching and notifying are independent concerns. Each class can be tested or swapped in isolation (e.g. switch from SMTP to SendGrid in `notifier.py` without touching the scraper).

**Credentials via `.env`, never hardcoded** — The real `.env` is gitignored. `.env.example` is committed to document required variables without leaking secrets.

**`Path(__file__).parent` for all paths** — The `.env` file is always resolved relative to the script's location, so both `python menu.py` and `python advanced/main.py` find it correctly from any working directory.

**Pure-logic modules raise exceptions instead of `sys.exit()`** — `AmazonScraper` and `EmailNotifier` have no awareness of how the caller handles errors. `main.py` catches all exceptions and prints clean messages, keeping business logic separate from error UX.

**`sys.path.insert` pattern** — `advanced/main.py` inserts its own directory at the front of `sys.path` so sibling imports (`from config import ...`) resolve correctly whether the script is launched via `menu.py` (using `subprocess.run` + `cwd=`) or directly.

**`subprocess.run` + `cwd=`** — `menu.py` sets `cwd` to the build's directory. This means relative imports inside each build resolve against that directory, not the repo root.

**`while True` in `menu.py`, no recursion** — The menu loop never calls itself. Stack depth stays constant regardless of how many times the user navigates back from a build.

**Console cleared before every menu render** — The `clear` flag is `True` after any valid action and `False` after invalid input, so error messages stay visible without an extra re-draw.

**Browser-spoofing headers** — Amazon aggressively blocks headless requests. Sending a realistic User-Agent and the full set of Sec-Fetch-* headers is the minimum required to get a real product page back.

**No `data/`, `input/`, or `output/` directories** — The script reads from the web and writes to email. Nothing is persisted between runs and no files ship with the project, so none of these directories are needed.

---

## 13. Course context

Built as Day 47 of 100 Days of Code by Dr. Angela Yu.

**Concepts covered in the original build:**
- Web scraping with `requests` and `BeautifulSoup`
- Locating elements with CSS class selectors
- Sending email with `smtplib` (STARTTLS, App Passwords)
- Loading credentials from `.env` with `python-dotenv`
- Regex for price extraction and normalisation

**The advanced build extends into:**
- Object-oriented design (classes, single-responsibility modules)
- Configuration centralisation (`config.py`)
- Clean exception propagation (raise vs sys.exit)
- CI/CD with GitHub Actions (daily cron schedule, secrets injection)

See [docs/COURSE_NOTES.md](docs/COURSE_NOTES.md) for the full concept breakdown.

---

## 14. Dependencies

| Module | Used in | Purpose |
|---|---|---|
| `requests` | `original/main.py`, `advanced/scraper.py` | HTTP GET to fetch the Amazon product page |
| `beautifulsoup4` | `original/main.py`, `advanced/scraper.py` | Parse HTML and locate the price element |
| `python-dotenv` | `original/main.py`, `advanced/main.py` | Load credentials from `.env` |
| `smtplib` | `original/main.py`, `advanced/notifier.py` | Send alert email via STARTTLS SMTP (standard library) |
| `re` | `original/main.py`, `advanced/scraper.py` | Regex price extraction and normalisation (standard library) |
| `os` | `original/main.py`, `advanced/main.py` | `os.getenv()` to read environment variables (standard library) |
| `pathlib` | `advanced/config.py`, `advanced/main.py`, `menu.py` | Path resolution relative to script location (standard library) |
| `subprocess` | `menu.py` | Launch build scripts as child processes (standard library) |
| `sys` | `menu.py`, `advanced/main.py` | `sys.executable`, `sys.path.insert` (standard library) |
