from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os
from datetime import date

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-before-deployment")
DB = os.path.join(os.path.dirname(__file__), "real_trader.db")

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL, display_name TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS trades(
            id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, trade_date TEXT NOT NULL,
            symbol TEXT NOT NULL, direction TEXT NOT NULL, setup TEXT DEFAULT '',
            entry REAL, exit REAL, stop_loss REAL, target REAL, quantity REAL DEFAULT 1,
            pnl REAL DEFAULT 0, fees REAL DEFAULT 0, exit_reason TEXT DEFAULT '',
            notes TEXT DEFAULT '', FOREIGN KEY(user_id) REFERENCES users(id))""")

@app.before_request
def setup():
    init_db()

def logged_in():
    return session.get("user_id") is not None

@app.route("/")
def landing():
    return redirect(url_for("dashboard")) if logged_in() else render_template("landing.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip().lower()
        password = request.form["password"]
        name = request.form["display_name"].strip()
        if len(password) < 8:
            flash("Password must be at least 8 characters.")
        else:
            try:
                with db() as c:
                    cur = c.execute("INSERT INTO users(username,password,display_name) VALUES(?,?,?)",
                        (username, generate_password_hash(password), name))
                    session["user_id"] = cur.lastrowid
                    session["name"] = name
                return redirect(url_for("dashboard"))
            except sqlite3.IntegrityError:
                flash("That username is already registered.")
    return render_template("auth.html", mode="Register")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        with db() as c:
            u = c.execute("SELECT * FROM users WHERE username=?", (request.form["username"].strip().lower(),)).fetchone()
        if u and check_password_hash(u["password"], request.form["password"]):
            session["user_id"], session["name"] = u["id"], u["display_name"]
            return redirect(url_for("dashboard"))
        flash("Username or password is incorrect.")
    return render_template("auth.html", mode="Login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))

@app.route("/dashboard")
def dashboard():
    if not logged_in(): return redirect(url_for("login"))
    with db() as c:
        trades = c.execute("SELECT * FROM trades WHERE user_id=? ORDER BY trade_date DESC,id DESC", (session["user_id"],)).fetchall()
    today = date.today().isoformat()
    todays = [t for t in trades if t["trade_date"] == today]
    pnl = sum((t["pnl"] or 0) - (t["fees"] or 0) for t in todays)
    wins = sum(1 for t in todays if (t["pnl"] or 0) - (t["fees"] or 0) > 0)
    return render_template("dashboard.html", trades=trades[:8], total=len(todays), pnl=pnl,
                           wins=wins, today=today, name=session.get("name","Trader"))

@app.route("/trades")
def trades():
    if not logged_in(): return redirect(url_for("login"))
    with db() as c:
        rows = c.execute("SELECT * FROM trades WHERE user_id=? ORDER BY trade_date DESC,id DESC", (session["user_id"],)).fetchall()
    return render_template("trades.html", trades=rows)

@app.route("/add", methods=["GET","POST"])
def add_trade():
    if not logged_in(): return redirect(url_for("login"))
    if request.method == "POST":
        f = request.form
        with db() as c:
            c.execute("""INSERT INTO trades(user_id,trade_date,symbol,direction,setup,entry,exit,stop_loss,target,quantity,pnl,fees,exit_reason,notes)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (session["user_id"], f["trade_date"], f["symbol"].upper(), f["direction"], f.get("setup",""),
                 float(f["entry"] or 0), float(f["exit"] or 0), float(f["stop_loss"] or 0),
                 float(f["target"] or 0), float(f["quantity"] or 1), float(f["pnl"] or 0),
                 float(f["fees"] or 0), f.get("exit_reason",""), f.get("notes","")))
        flash("Trade saved to your journal.")
        return redirect(url_for("trades"))
    return render_template("add_trade.html", today=date.today().isoformat())

@app.route("/delete/<int:trade_id>", methods=["POST"])
def delete_trade(trade_id):
    if not logged_in(): return redirect(url_for("login"))
    with db() as c:
        c.execute("DELETE FROM trades WHERE id=? AND user_id=?", (trade_id, session["user_id"]))
    return redirect(url_for("trades"))

@app.route("/reports")
def reports():
    if not logged_in(): return redirect(url_for("login"))
    with db() as c:
        rows = c.execute("SELECT * FROM trades WHERE user_id=?", (session["user_id"],)).fetchall()
    net = sum((r["pnl"] or 0) - (r["fees"] or 0) for r in rows)
    wins = sum(1 for r in rows if (r["pnl"] or 0) - (r["fees"] or 0) > 0)
    losses = sum(1 for r in rows if (r["pnl"] or 0) - (r["fees"] or 0) < 0)
    winrate = round(wins * 100 / len(rows), 1) if rows else 0
    return render_template("reports.html", count=len(rows), net=net, wins=wins, losses=losses, winrate=winrate)

if __name__ == "__main__":
    app.run(debug=True)
