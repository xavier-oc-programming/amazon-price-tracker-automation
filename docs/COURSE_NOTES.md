# Course Notes — Day 47: Amazon Price Tracker

## Exercise description

Build a script that:
1. Scrapes a product page on Amazon using `requests` and `BeautifulSoup`.
2. Extracts the current price from the page HTML.
3. Compares the price against a hardcoded target price.
4. Sends an email alert via `smtplib` if the price has dropped below the target.

The course used `https://appbrewery.github.io/instant_pot/` as a safe test URL
for scraping practice (no rate-limiting, static HTML). The live script uses
the real Amazon product URL with browser-spoofing headers.

## Concepts covered

- Web scraping with `requests` and `BeautifulSoup`
- Parsing HTML with CSS class selectors (`soup.find()`)
- Sending email programmatically with `smtplib` (STARTTLS, App Passwords)
- Environment variables with `python-dotenv`
- Regex for extracting and normalising price strings

## Variant files

| File | Description |
|---|---|
| `main.py` → `original/main.py` | Full course solution: real Amazon URL, browser headers, EU/US price normalisation, error handling |
| `dummy_main.py` → `old_files/` | Practice version using the static test URL; simpler price parsing (no regex), no error handling |

`dummy_main.py` was excluded from `original/` because `main.py` is strictly superior: it handles the real site, normalises both EU and US price formats, and handles errors gracefully.

## Practice files (old_files/ only)

The `Practice BeautifulSoup/` folder contains standalone BeautifulSoup exercises
unrelated to the price tracker:
- `dummy.html` — local HTML file used for scraping practice
- `practice_soup.py` — exercises: find by tag, class, id, CSS selectors
- `practice_soup_answers.py` — course solutions to the same exercises
