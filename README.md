# REAL TRADER — Trading Journal MVP

A starter web app built with Python Flask, SQLite, HTML, CSS and JavaScript.

## Run locally
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Run `python -m venv .venv`
4. Activate it:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
5. Run `pip install -r requirements.txt`
6. Run `python app.py`
7. Open http://127.0.0.1:5000

Register a user, then add trades. Each account sees only its own journal entries.

## Included
- Landing page, language selector UI (English/Hindi/Marathi labels are a starter control)
- Registration and login with hashed passwords
- Dashboard with today's trade count, net P&L and recent trades
- Trade journal: symbol, buy/sell, setup/strategy, entry, exit, stop loss, target,
  quantity, P&L, fees, exit reason and notes
- Reports with win rate, wins/losses and net P&L
- SQLite database

## Important before public deployment
This is an MVP, not a production-hardened financial service. Change `SECRET_KEY`, use HTTPS,
add CSRF protection, rate limiting, secure cookie settings, database backups and proper hosting.
Do not enter broker passwords, API secrets, or other sensitive credentials. P&L is entered manually;
this version does not connect to a broker or verify trades. The app is a record-keeping tool,
not financial advice.
