# Task 1: Simple URL Shortener

CodeAlpha Backend Development Internship project built with **Flask (Python)** and **SQLite**.

## Features
- `POST /api/shorten` accepts a long URL and returns a unique short code
- Short codes are stored in SQLite (`urls.db`, created automatically)
- `GET /<code>` redirects to the original URL and counts the click
- Optional custom short code (for example `/my-link`)
- URL validation, duplicate handling and reserved-word protection
- Simple frontend: form, copy button and list of recent links

## Setup
```bash
cd task1_url_shortener
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000 in your browser.

## API
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/shorten` | Body: `{"url": "...", "custom_code": "optional"}` |
| GET | `/api/links` | 10 most recent links |
| GET | `/api/links/<code>` | Details and click count for one link |
| GET | `/<code>` | Redirects to the original URL |

Example:
```bash
curl -X POST http://127.0.0.1:5000/api/shorten -H "Content-Type: application/json" -d "{\"url\": \"https://www.python.org\"}"
```

## Project structure
```
task1_url_shortener/
  app.py            Flask app, routes and database logic
  requirements.txt
  templates/index.html
  static/style.css
  static/script.js
```
