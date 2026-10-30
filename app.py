import os, sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-before-deploying")
DB = os.environ.get("DATABASE_PATH", "real_trader.db")

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL,
            symbol TEXT NOT NULL, side TEXT NOT NULL, entry REAL NOT NULL,
            exit REAL, quantity REAL NOT NULL, notes TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id))""")

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    return redirect(url_for("dashboard")) if session.get("user_id") else redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if len(username) < 3 or len(password) < 8:
            flash("Username must be 3+ characters and password 8+ characters.")
        else:
            try:
                with db() as con:
                    con.execute("INSERT INTO users(username,password_hash) VALUES(?,?)",
                                (username, generate_password_hash(password)))
                flash("Account created. Please sign in.")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("That username is already taken.")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        with db() as con:
            user = con.execute("SELECT * FROM users WHERE username=?",
                               (request.form.get("username", "").strip(),)).fetchone()
        if user and check_password_hash(user["password_hash"], request.form.get("password", "")):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        flash("Incorrect username or password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    with db() as con:
        rows = con.execute("SELECT * FROM trades WHERE user_id=? ORDER BY id DESC",
                           (session["user_id"],)).fetchall()
    closed = [r for r in rows if r["exit"] is not None]
    pnl = sum(((r["exit"]-r["entry"]) if r["side"] == "Buy" else
               (r["entry"]-r["exit"])) * r["quantity"] for r in closed)
    return render_template("dashboard.html", trades=rows, pnl=round(pnl, 2),
                           count=len(rows), closed=len(closed))

@app.route("/trades/new", methods=["GET", "POST"])
@login_required
def new_trade():
    if request.method == "POST":
        try:
            symbol = request.form["symbol"].strip().upper()
            side = request.form["side"]
            entry = float(request.form["entry"])
            exit_price = request.form.get("exit", "").strip()
            exit_price = float(exit_price) if exit_price else None
            qty = float(request.form["quantity"])
            if not symbol or side not in ("Buy", "Sell") or entry <= 0 or qty <= 0:
                raise ValueError()
            with db() as con:
                con.execute("""INSERT INTO trades(user_id,symbol,side,entry,exit,quantity,notes)
                    VALUES(?,?,?,?,?,?,?)""",
                    (session["user_id"], symbol, side, entry, exit_price, qty,
                     request.form.get("notes", "").strip()))
            return redirect(url_for("dashboard"))
        except (ValueError, KeyError):
            flash("Please enter valid trade details.")
    return render_template("new_trade.html")

@app.route("/trades/<int:trade_id>/delete", methods=["POST"])
@login_required
def delete_trade(trade_id):
    with db() as con:
        con.execute("DELETE FROM trades WHERE id=? AND user_id=?",
                    (trade_id, session["user_id"]))
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
