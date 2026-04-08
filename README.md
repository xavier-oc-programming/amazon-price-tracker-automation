# Amazon Price Tracker

Scrapes an Amazon product page and sends an email alert when the price drops below a target threshold.

Point the script at any Amazon product URL, set a target price, and run it manually or schedule it to check automatically every day. When the live price dips below your threshold, you receive an email with the current price and a direct link to buy.

There are two builds. The **original** build is a single flat script that follows the course exercise exactly: it fetches the page, pulls the price with BeautifulSoup, and fires off an email via `smtplib` — all in one file, top to bottom. The **advanced** build reorganises the same logic into three clean modules (`scraper.py`, `notifier.py`, `config.py`) with all magic numbers extracted into constants, credentials loaded from `.env`, and a `main.py` orchestrator that wires them together. Both builds produce identical alert behaviour; the difference is structure, error handling, and maintainability.

This project uses two external services. **Amazon** (amazon.es) provides the product page that is scraped for the live price. **Gmail SMTP** (via Google App Passwords) is used to send the alert email without exposing your main account password.

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
python menu.py         # interactive menu — see all options
```

Or run a build directly without the menu:

```bash
python original/main.py
python advanced/main.py
```

### Scheduling (recommended: local cron)

GitHub Actions is **not recommended** for scraping Amazon — their Azure datacenter IPs are flagged by Amazon's bot detection regardless of headers. Running from your local machine works because your home ISP IP looks identical to a real browser visit.

All cron management is available directly from `menu.py` (options 3–5). You can also run the scripts directly from the project root:

| Script | What it does |
|---|---|
| `bash setup_cron.sh` | Installs daily cron job at 08:00, sends confirmation email |
| `bash check_cron.sh` | Shows whether cron is active + last 5 log entries |
| `bash remove_cron.sh` | Removes the cron job, sends confirmation email |

**One-time macOS setup required before any cron script will work:**

System Settings → Privacy & Security → Full Disk Access → enable Terminal

Without Full Disk Access, macOS silently blocks `crontab` writes.

Your Mac must be awake at 08:00 for the job to run — if it is asleep, the job is skipped until the next day.

---

## 2. Builds comparison

| Feature | Original | Advanced |
|---|---|---|
| File structure | Single flat script | Separate modules |
| Config | Constants defined inline | `config.py` — single source of truth |
| Scraping | Inline `requests` + BeautifulSoup | `AmazonScraper` class |
| Email | Inline `smtplib` call | `EmailNotifier` class |
| Credentials | Loaded from `.env` via `dotenv` | Loaded from `.env` via `dotenv` |
| Price parsing | Regex helper function | `AmazonScraper._parse_price()` static method |
| EUR/USD/GBP format support | Yes | Yes |
| Error handling | `try/except` around SMTP only | Every stage raises typed exceptions; `main.py` catches all |
| Cron-safe | No — bare tracebacks on failure | Yes — always exits cleanly |
| Notification emails | Price alert only | Price alert + cron install/remove confirmations |
| Entry point | `original/main.py` | `advanced/main.py` |

---

## 3. Usage

```bash
python menu.py
```

```
   _____                                       __________        .__
  /  _  \   _____ _____  ____________   ____   \______   \_______|__| ____  ____
 /  /_\  \ /     \\__  \ \___   /  _ \ /    \   |     ___/\_  __ \  |/ ___\/ __ \
/    |    \  Y Y  \/ __ \_/    (  <_> )   |  \  |    |     |  | \/  \  \__\  ___/
\____|__  /__|_|  (____  /_____ \____/|___|  /  |____|     |__|  |__|\___  >___  >
        \/      \/     \/      \/          \/                            \/    \/

 ████████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗
╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
   ██║   ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
   ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
   ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝

              Amazon Price Alert — Day 47 of 100 Days of Code

1. Run original build       (course version)
2. Run advanced build       (OOP, config.py, modular)
─────────────────────────────────────────────
3. Schedule daily check     (install cron job)
4. Check cron status        (is it active?)
5. Remove cron job          (stop daily checks)
─────────────────────────────────────────────
q. Quit

Select an option:
```

Select `1` or `2` to run a build. The script runs once and returns to the menu. Press Enter when ready to redraw.

**Option 3 — Schedule daily check:**

Runs `setup_cron.sh` using the same Python interpreter that launched `menu.py`. Verifies `.env` and packages before installing. On success, sends a confirmation email with the current price and schedule details.

**Option 4 — Check cron status:**

Runs `check_cron.sh`. Shows whether the cron job is installed, the exact cron entry, and the last 5 lines of `tracker.log` so you can see the most recent run without leaving the menu.

**Option 5 — Remove cron job:**

Runs `remove_cron.sh`. Deletes the cron entry and sends a confirmation email with the current price at time of removal.

**Example terminal output (price above target):**

```
Current price: 149.99
No alert — price (149.99) is above target (190.00).
```

**Example terminal output (price below target):**

```
Current price: 149.99
Price is below target (190.00). Sending alert...
Alert sent successfully.
```

**Example confirmation email on cron install:**

```
Subject: Amazon Price Tracker — Daily Check Activated

Your Amazon price tracker is now running automatically.

Product : Kobo Libra Color Ereader
Link    : https://www.amazon.es/dp/B0CZXWGK79
Target  : 190.00 EUR
Current price: 149.99 EUR (BELOW target — alert would fire today!)
Schedule: every day at 08:00

You will receive an alert if the price drops below your target.
To manage the schedule, open menu.py and use options 4 or 5.
```

**Example confirmation email on cron removal:**

```
Subject: Amazon Price Tracker — Daily Check Deactivated

Your Amazon price tracker cron job has been removed.

Product : Kobo Libra Color Ereader
Link    : https://www.amazon.es/dp/B0CZXWGK79
Target  : 190.00 EUR
Current price: 149.99 EUR (BELOW target — alert would fire today!)

The script will no longer run automatically.
To re-enable it, open menu.py and select option 3.
```

---

## 4. Data flow

```
Input (config)
  └─ PRODUCT_URL, BROWSER_HEADERS, TARGET_PRICE, SMTP credentials from .env

Fetch
  └─ requests.get(PRODUCT_URL, headers=BROWSER_HEADERS)
  └─ Response: raw HTML string

Parse
  └─ BeautifulSoup finds <span class="aok-offscreen">
  └─ Regex extracts price string
     — handles €/$/£ symbols and EUR/USD/GBP text prefixes
     — handles non-breaking spaces (\xa0) between currency and number
     — handles EU comma-decimal and US dot-decimal formats
  └─ Output: float (e.g. 149.99)

Decide
  └─ price < TARGET_PRICE?
     ├─ Yes → send price alert email
     └─ No  → print "No alert" and exit

Output
  └─ smtplib sends email via Gmail SMTP (port 587, STARTTLS)
  └─ Subject: "Amazon Price Alert!"
  └─ Body: current price, target price, product URL
```

---

## 5. Features

**Browser-spoofing headers** — The scraper sends a full set of browser headers (User-Agent, Accept, Sec-Fetch-\*) matching a real Firefox session on macOS. Amazon serves bot-detection pages to bare `requests` calls; these headers bypass that.

**Multi-format price parsing** — The regex handles every format Amazon uses: `€59,99`, `€1.299,99`, `$129.99`, `EUR\xa068.30`. Currency symbols, currency codes, and non-breaking spaces are all stripped before normalisation.

**STARTTLS email** — Email is sent over an encrypted STARTTLS connection on port 587. Credentials are loaded from `.env` and never hardcoded.

**Advanced-only: modular OOP design** — `AmazonScraper` and `EmailNotifier` are independent classes. Each can be instantiated, tested, or swapped without touching the other. Changing from Gmail SMTP to SendGrid means only touching `notifier.py`.

**Advanced-only: cron management from the menu** — Options 3, 4, and 5 in `menu.py` cover the full lifecycle of the cron job: install, status check with live log tail, and removal. All three shell scripts (`setup_cron.sh`, `check_cron.sh`, `remove_cron.sh`) can also be run directly from the project root.

**Advanced-only: confirmation emails with live price** — When the cron is installed or removed, the script fetches the current price at that moment and includes it in the confirmation email, along with whether the price is currently above or below the target.

**Advanced-only: clean error propagation** — Modules raise typed exceptions (`ValueError`, `RuntimeError`). `main.py` catches them and prints a clean message. The script never crashes with a bare traceback — important for cron jobs where output goes to a log file.

**Advanced-only: cron-safe Python path** — `setup_cron.sh` receives `sys.executable` from `menu.py`, so the cron job always uses the exact same Python interpreter and virtual environment that the user ran the menu with. No package mismatch between interactive and scheduled runs.

---

## 6. Navigation flow

### a) Terminal menu tree

```
python menu.py
│
├─ 1 ──► original/main.py       (course build — single-run)
│         └─ returns → Press Enter → menu redraws
│
├─ 2 ──► advanced/main.py       (OOP build — single-run)
│         └─ returns → Press Enter → menu redraws
│
├─ 3 ──► setup_cron.sh          (install cron job)
│         └─ returns → Press Enter → menu redraws
│
├─ 4 ──► check_cron.sh          (show status + last 5 log lines)
│         └─ returns → Press Enter → menu redraws
│
├─ 5 ──► remove_cron.sh         (delete cron job)
│         └─ returns → Press Enter → menu redraws
│
└─ q ──► exit
```

### b) Price check execution flow

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
  ├─ no regex match → raise ValueError → caught in main → print error → exit
  │
  ▼
price < TARGET_PRICE?
  │
  ├─ No  → print "No alert" → exit cleanly
  │
  └─ Yes → smtplib.SMTP(SMTP_ADDRESS, 587)
              │
              ├─ auth error  → raise ValueError  → caught in main → print error → exit
              ├─ SMTP error  → raise RuntimeError → caught in main → print error → exit
              │
              └─ success → print "Alert sent" → exit cleanly
```

### c) Cron install flow (option 3)

```
menu.py option 3
  │
  ▼
setup_cron.sh (receives sys.executable from menu.py)
  │
  ├─ .env missing?       → print error + instructions → exit
  ├─ packages missing?   → print error + instructions → exit
  ├─ cron already set?   → print existing entry → exit (no duplicate)
  │
  ▼
crontab install (0 8 * * *)
  │
  ├─ write failed (Full Disk Access not granted)?
  │     → print error + System Settings instructions → exit
  │
  └─ success
        │
        ▼
        send_notification.py setup
          │
          ├─ fetch current price from amazon.es
          ├─ compare to TARGET_PRICE
          └─ send confirmation email with price + status
```

---

## 7. Architecture

```
day47-amazon-price-tracker/
│
├── menu.py                      # interactive menu — launches builds and cron scripts
├── art.py                       # LOGO constant printed by menu.py
├── requirements.txt             # pip dependencies + Python version note
├── setup_cron.sh                # install daily 08:00 cron job (menu option 3)
├── check_cron.sh                # show cron status + last 5 log lines (menu option 4)
├── remove_cron.sh               # remove cron job (menu option 5)
├── .gitignore
├── .env.example                 # credential template — committed, never the real .env
├── README.md
│
├── original/
│   └── main.py                  # verbatim course script — single flat file
│
├── advanced/
│   ├── config.py                # all constants: URL, headers, threshold, SMTP port
│   ├── scraper.py               # AmazonScraper — fetches page and extracts price
│   ├── notifier.py              # EmailNotifier — sends SMTP alert
│   ├── send_notification.py     # sends cron install/remove confirmation emails
│   └── main.py                  # orchestrator — wires scraper + notifier together
│
├── docs/
│   └── COURSE_NOTES.md          # original exercise description and variant file notes
│
└── .github/
    └── workflows/
        └── amazon-price-tracker.yml   # GitHub Actions reference (not recommended — see below)
```

---

## 8. Module reference

### `advanced/scraper.py` — `AmazonScraper`

| Method | Returns | Description |
|---|---|---|
| `__init__(url, headers)` | — | Initialises with product URL and browser headers. Both parameters are optional — defaults come from `config.py`. |
| `get_price()` | `float` | Fetches the product page, locates the price element, and returns the current price. Raises `requests.HTTPError` on a bad HTTP response. Raises `ValueError` if the price element is missing or no parseable price string is found. |
| `_parse_price(text)` *(static)* | `float` | Extracts and normalises a price string. Handles `€`, `$`, `£` symbols and `EUR`, `USD`, `GBP` text prefixes with optional non-breaking spaces. Handles EU comma-decimal and US dot-decimal formats. Raises `ValueError` if no valid price pattern is found. |

### `advanced/notifier.py` — `EmailNotifier`

| Method | Returns | Description |
|---|---|---|
| `__init__(smtp_address, sender, password, recipient)` | — | Stores SMTP credentials. No connection is opened at init time. |
| `send_alert(current_price)` | `bool` | Sends the price-drop alert email via STARTTLS SMTP on port 587. Returns `True` on success. Raises `ValueError` on authentication failure. Raises `RuntimeError` on any other SMTP error. |

### `advanced/send_notification.py` — standalone script

Called by `setup_cron.sh` and `remove_cron.sh` after a successful cron install or removal.

| Argument | Effect |
|---|---|
| `setup` | Sends "Daily Check Activated" email with current price and schedule |
| `remove` | Sends "Daily Check Deactivated" email with current price |

Fetches the live price at the moment of execution. If the fetch fails, falls back to `"could not fetch"` and still sends the email.

---

## 9. Configuration reference

All constants are in [advanced/config.py](advanced/config.py). Edit this file to change the product, target price, or any other setting.

| Constant | Default | Description |
|---|---|---|
| `PRODUCT_NAME` | `"Kobo Libra Color Ereader"` | Human-readable product name shown in all emails. |
| `PRODUCT_URL` | `https://www.amazon.es/dp/B0CZXWGK79` | The product page to scrape. Replace with any Amazon product URL. |
| `BROWSER_HEADERS` | Firefox 143 on macOS | Full set of headers sent with every request to avoid bot detection. |
| `PRICE_CSS_CLASS` | `"aok-offscreen"` | CSS class of the `<span>` containing the price on Amazon product pages. |
| `TARGET_PRICE` | `190.00` | EUR threshold — alert email fires when the live price drops below this. |
| `SMTP_PORT` | `587` | STARTTLS port for Gmail SMTP. |
| `ROOT_DIR` | `Path(__file__).parent.parent` | Absolute path to the repo root, used to locate `.env`. |

---

## 10. Data schema

### Scraped HTML price element

Amazon embeds the price in a screen-reader span:

```html
<span class="aok-offscreen">EUR 149,99</span>
```

The regex pattern handles all formats Amazon uses by region:

| Raw string from page | Parsed float |
|---|---|
| `$129.99` | `129.99` |
| `$1,299.99` | `1299.99` |
| `€59,99` | `59.99` |
| `€1.299,99` | `1299.99` |
| `EUR\xa068.30` | `68.30` |
| `EUR\xa01.299,99` | `1299.99` |

### Price alert email

```
Subject: Amazon Price Alert!

Price dropped to 149.99 EUR — below your target of 190.00 EUR!

Product : Kobo Libra Color Ereader
Link    : https://www.amazon.es/dp/B0CZXWGK79
```

### Cron install confirmation email

```
Subject: Amazon Price Tracker — Daily Check Activated

Your Amazon price tracker is now running automatically.

Product : Kobo Libra Color Ereader
Link    : https://www.amazon.es/dp/B0CZXWGK79
Target  : 190.00 EUR
Current price: 149.99 EUR (BELOW target — alert would fire today!)
Schedule: every day at 08:00

You will receive an alert if the price drops below your target.
To manage the schedule, open menu.py and use options 4 or 5.
```

### Cron removal confirmation email

```
Subject: Amazon Price Tracker — Daily Check Deactivated

Your Amazon price tracker cron job has been removed.

Product : Kobo Libra Color Ereader
Link    : https://www.amazon.es/dp/B0CZXWGK79
Target  : 190.00 EUR
Current price: 149.99 EUR (BELOW target — alert would fire today!)

The script will no longer run automatically.
To re-enable it, open menu.py and select option 3.
```

### tracker.log (cron output)

Each daily run appends its stdout and stderr to `tracker.log` in the project root:

```
Current price: 149.99
No alert — price (149.99) is above target (190.00).
```

or on alert:

```
Current price: 149.99
Price is below target (190.00). Sending alert...
Alert sent successfully.
```

---

## 11. Environment variables

Copy `.env.example` to `.env` and fill in values. The `.env` file is gitignored and never committed.

| Variable | Required | Description |
|---|---|---|
| `SMTP_ADDRESS` | Yes | SMTP server hostname — always `smtp.gmail.com` for Gmail |
| `EMAIL_ADDRESS` | Yes | Gmail address used to send all emails (alerts and confirmations) |
| `EMAIL_PASSWORD` | Yes | 16-character Gmail App Password — not your normal Gmail password |
| `TARGET_EMAIL` | Yes | Recipient address for alert and confirmation emails |

`TARGET_EMAIL` can be the same as `EMAIL_ADDRESS` to send to yourself, or a different address to notify someone else.

---

## 12. Design decisions

**`config.py` — zero magic numbers** — Every constant (URL, price threshold, SMTP port, browser headers, CSS class) lives in one file. Changing the monitored product or target price requires editing exactly one line with no risk of missing a duplicate elsewhere.

**Separate `scraper.py` and `notifier.py`** — Fetching and notifying are independent concerns. Each class can be tested or replaced in isolation. Switching from Gmail SMTP to SendGrid means only touching `notifier.py`; the scraper is unaffected.

**Credentials via `.env`, never hardcoded** — The real `.env` is gitignored. `.env.example` is committed to document required variables without leaking secrets. Anyone cloning the repo immediately knows what credentials they need.

**`Path(__file__).parent` for all paths** — The `.env` file is always resolved relative to each script's own location, so both `python menu.py` and `python advanced/main.py` (and the cron job) find it correctly regardless of what directory they are launched from.

**Pure-logic modules raise exceptions instead of `sys.exit()`** — `AmazonScraper` and `EmailNotifier` have no awareness of how the caller handles errors. `main.py` catches all exceptions and prints clean messages. This keeps business logic separate from error UX and makes the advanced build safe for unattended cron runs — a bare traceback in `tracker.log` would be unreadable.

**`sys.path.insert` pattern** — `advanced/main.py` inserts its own directory at the front of `sys.path` so sibling imports (`from config import ...`) resolve correctly whether launched via `menu.py`, run directly, or executed by cron.

**`subprocess.run` + `cwd=`** — `menu.py` sets `cwd` to the build's directory when launching each script. This means relative imports inside each build resolve against their own directory, not the repo root.

**`sys.executable` passed to cron scripts** — `menu.py` passes `sys.executable` to `setup_cron.sh` and `remove_cron.sh` so the cron job uses the exact Python interpreter that ran the menu — same virtual environment, same installed packages. Using `which python3` would silently pick up the system Python which may lack `requests`, `bs4`, or `dotenv`.

**All three cron scripts in root** — `setup_cron.sh`, `check_cron.sh`, and `remove_cron.sh` are all at the repo root alongside `menu.py`. They can be run directly (`bash setup_cron.sh`) or via menu options 3–5. Keeping them at root makes them discoverable and consistent — no reason to bury them in a subdirectory.

**`while True` in `menu.py`, no recursion** — The menu loop never calls itself. Stack depth stays constant regardless of how many times the user navigates back from a build or cron action.

**Console cleared before every menu render, not after errors** — The `clear` flag is `True` after any valid action and `False` after invalid input, so error messages stay visible on screen before the menu redraws.

**Confirmation emails fetch the live price** — When the cron is installed or removed, `send_notification.py` fetches the current price at that moment and includes it alongside the target. This gives the user immediate context — they can see whether the tracker would have fired today.

**Local cron over GitHub Actions** — The `.github/workflows/` file is included for reference, but GitHub Actions runs on Microsoft Azure datacenter IPs. Amazon identifies these ranges and returns bot-detection pages regardless of browser headers. A local cron job runs from a home ISP IP, which is indistinguishable from a real browser. No proxy, no workaround, no extra cost.

**No `data/`, `input/`, or `output/` directories** — The script reads from the web and writes to email. Nothing is persisted between runs and no curated files ship with the project, so none of these directories are needed.

---

## 13. Course context

Built as Day 47 of 100 Days of Code by Dr. Angela Yu.

**Concepts covered in the original build:**
- Web scraping with `requests` and `BeautifulSoup`
- Locating elements with CSS class selectors (`soup.find()`)
- Sending email programmatically with `smtplib` (STARTTLS, port 587)
- Using Gmail App Passwords instead of account passwords
- Loading credentials from `.env` with `python-dotenv`
- Regex for price string extraction and normalisation

**The advanced build extends into:**
- Object-oriented design (classes, single-responsibility modules)
- Configuration centralisation (`config.py` — single source of truth)
- Clean exception propagation (raise in modules, catch in orchestrator)
- Shell scripting for cron management (`setup_cron.sh`, `check_cron.sh`, `remove_cron.sh`)
- Scheduled automation via macOS cron with full lifecycle management from a menu

See [docs/COURSE_NOTES.md](docs/COURSE_NOTES.md) for the full concept breakdown and notes on variant files.

---

## 14. Dependencies

| Module | Used in | Purpose |
|---|---|---|
| `requests` | `original/main.py`, `advanced/scraper.py` | HTTP GET to fetch the Amazon product page with browser headers |
| `beautifulsoup4` | `original/main.py`, `advanced/scraper.py` | Parse response HTML and locate the price `<span>` element |
| `python-dotenv` | `original/main.py`, `advanced/main.py`, `advanced/send_notification.py` | Load credentials from `.env` at runtime |
| `smtplib` | `original/main.py`, `advanced/notifier.py`, `advanced/send_notification.py` | Send emails via STARTTLS SMTP — standard library |
| `re` | `original/main.py`, `advanced/scraper.py` | Regex price extraction and multi-format normalisation — standard library |
| `os` | `original/main.py`, `advanced/main.py`, `advanced/send_notification.py` | `os.getenv()` to read environment variables — standard library |
| `pathlib` | `advanced/config.py`, `advanced/main.py`, `advanced/send_notification.py`, `menu.py` | Path resolution relative to each script's location — standard library |
| `subprocess` | `menu.py` | Launch build scripts and cron shell scripts as child processes — standard library |
| `sys` | `menu.py`, `advanced/main.py`, `advanced/send_notification.py` | `sys.executable`, `sys.path.insert`, `sys.argv` — standard library |
