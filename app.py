import os
import requests
import json

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

remote_session = requests.Session()
remote_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    ownerships = db.execute(
        "SELECT symbol, shares FROM ownerships WHERE user_id = ?", session["user_id"])
    costs = db.execute(
        "SELECT symbol, SUM(price * shares) AS total_spent FROM transactions WHERE user_id = ? GROUP BY symbol", session["user_id"])
    cost_map = {row["symbol"]: row["total_spent"] for row in costs}
    total = 0
    for row in ownerships:
        stock_info = lookup(row["symbol"])
        price = stock_info["price"]
        value = row["shares"] * price
        total += value
        total_paid = cost_map.get(row["symbol"], 0)
        pl_money = value - total_paid
        pl_percent = (pl_money / total_paid) * 100
        day_change = price - stock_info["prev_close"]
        day_change_pct = (day_change / stock_info["prev_close"]) * 100
        row["name"] = stock_info["name"]
        row["price"] = price
        row["value"] = value
        row["day_change"] = day_change
        row["day_change_pct"] = day_change_pct
        row["pl_money"] = pl_money
        row["pl_percent"] = pl_percent
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
    total += cash
    chart_labels = [stock["symbol"] for stock in ownerships] + ["Cash"]
    chart_values = [stock["value"] for stock in ownerships] + [cash]
    return render_template("index.html", ownerships=ownerships, cash=cash, total=total, chart_labels=chart_labels, chart_values=chart_values)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        if not request.form.get("symbol") or lookup(request.form.get("symbol")) is None:
            return apology("invalid symbol", 400)
        elif not request.form.get("shares") or not request.form.get("shares").isdigit() or int(request.form.get("shares")) <= 0:
            return apology("invalid number of shares", 400)
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
        symbol = request.form.get("symbol").upper()
        price = lookup(request.form.get("symbol"))["price"]
        shares = int(request.form.get("shares"))
        if cash < (price * shares):
            return apology("cannot afford the number of shares at current price", 403)
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?",
                   (price * shares), session["user_id"])
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, amount) VALUES (?, ?, ?, ?, ?)",
                   session["user_id"], symbol, shares, price, price * shares)
        stock = db.execute("SELECT shares FROM ownerships WHERE user_id = ? AND symbol = ?",
                           session["user_id"], symbol)
        if len(stock) == 1:
            db.execute("UPDATE ownerships SET shares = ? WHERE user_id = ? AND symbol = ?",
                       stock[0]["shares"] + shares, session["user_id"], symbol)
        else:
            db.execute("INSERT INTO ownerships (user_id, symbol, shares) VALUES (?, ?, ?)",
                       session["user_id"], symbol, shares)
        return redirect("/")
    else:
        prefill_symbol = request.args.get("symbol", "")
        return render_template("buy.html", symbol=prefill_symbol)


@app.route("/cash", methods=["GET", "POST"])
@login_required
def cash():
    """Allow user to add or remove cash from their account."""
    if request.method == "POST":
        amount = request.form.get("amount")
        if not amount or not amount.isdigit() or int(amount) <= 0:
            return apology("must provide a positive amount", 400)
        if request.form.get("action") == "remove":
            cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
            if cash >= int(amount):
                db.execute("UPDATE users SET cash = cash - ? WHERE id = ?",
                           int(amount), session["user_id"])
                db.execute("INSERT INTO transactions (user_id, symbol, shares, price, amount) VALUES (?, ?, ?, ?, ?)",
                           session["user_id"], "WITHDRAW", "-", int(amount), int(amount))
            else:
                return apology(f"must provide amount less than {cash}", 400)
        elif request.form.get("action") == "add":
            db.execute("UPDATE users SET cash = cash + ? WHERE id = ?",
                       int(amount), session["user_id"])
            db.execute("INSERT INTO transactions (user_id, symbol, shares, price, amount) VALUES (?, ?, ?, ?, ?)",
                       session["user_id"], "DEPOSIT", "-", int(amount), int(amount))
        return redirect("/")
    else:
        return render_template("cash.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    history = db.execute(
        "SELECT symbol, shares, price, date_time FROM transactions WHERE user_id = ? ORDER BY date_time DESC LIMIT 30", session["user_id"])
    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/password_change")
@login_required
def password_change():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure new password was submitted
        elif not request.form.get("new_password"):
            return apology("must provide new password", 400)

        # Ensure new password matches in both instances
        elif not request.form.get("new_password") == request.form.get("confirmation"):
            return apology("new password repetition does not match original", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE id = ?", session["user_id"]
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Update new password
        db.execute("UPDATE users SET hash = ? WHERE id = ?",
                   generate_password_hash(request.form.get("new_password")), session["user_id"])

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("password_change.html")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        stock = lookup(request.form.get("symbol"))
        if not stock:
            return apology("invalid symbol", 400)
        return render_template("quoted.html", stock=stock, labels=json.dumps(stock["chart_labels"]), values=json.dumps(stock["chart_values"]))
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password matches in both instances
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("password repetition does not match original", 400)

        # Query database for username in use
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username does not already exists
        if len(rows) > 0:
            return apology("username already in use", 400)

        # Register user
        id = db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"),
            generate_password_hash(request.form.get("password"))
        )

        # Remember which user has logged in
        session["user_id"] = id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/search")
# @login_required  <-- Temporary comment this out just to test in your browser!
def search():
    query = request.args.get("q")
    if not query:
        return jsonify([])

    try:
        # Use our renamed 'remote_session'
        if not remote_session.cookies:
            remote_session.get("https://finance.yahoo.com", timeout=5)

        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}"
        response = remote_session.get(url, timeout=5)
        data = response.json()

        results = []
        for item in data.get("quotes", []):
            results.append({
                "symbol": item.get("symbol"),
                "name": item.get("shortname") or item.get("longname") or "Unknown",
                "exchange": item.get("exchange", "")
            })

        return jsonify(results[:10])
    except Exception as e:
        print(f"Error: {e}")
        return jsonify([])


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    rows = db.execute(
        "SELECT symbol FROM ownerships WHERE user_id = ? AND shares > 0", session["user_id"])
    symbols = [row["symbol"] for row in rows]
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = int(request.form.get("shares"))
        if symbol not in symbols:
            return apology("must select a stock you own", 403)
        stock_info = db.execute(
            "SELECT shares FROM ownerships WHERE user_id = ? AND symbol = ?", session["user_id"], symbol)
        if shares > stock_info[0]["shares"] or shares <= 0:
            return apology("too many shares", 400)
        price = lookup(symbol)["price"]
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?",
                   (price * shares), session["user_id"])
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, amount) VALUES (?, ?, ?, ?, ?)",
                   session["user_id"], symbol, -shares, price, price * shares)
        if shares < stock_info[0]["shares"]:
            db.execute("UPDATE ownerships SET shares = ? WHERE user_id = ? AND symbol = ?",
                       stock_info[0]["shares"] - shares, session["user_id"], symbol)
        else:
            db.execute("DELETE FROM ownerships WHERE user_id = ? AND symbol = ?",
                       session["user_id"], symbol)
        return redirect("/")
    else:
        prefill_symbol = request.args.get("symbol", "")
        prefill_shares = request.args.get("shares", "")
        return render_template("sell.html", stocks=symbols, symbol=prefill_symbol, shares=prefill_shares)
