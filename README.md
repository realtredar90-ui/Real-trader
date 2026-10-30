# REAL TRADER — Trading Journal

A small Flask-based **educational trade journal**. It records trades and shows a simple dashboard; it does not connect to brokers, place orders, or provide trading signals.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Run `python -m venv .venv` and activate it.
4. Run `pip install -r requirements.txt`.
5. Run `python app.py`.
6. Open http://127.0.0.1:5000 in your browser.

Set a strong `SECRET_KEY` environment variable before deployment. Use HTTPS and a production WSGI server for any hosted deployment. This starter is not a security-audited production service.
