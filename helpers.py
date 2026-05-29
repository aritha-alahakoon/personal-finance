import requests
import yfinance as yf

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def format_large_number(num):
    if num is None or isinstance(num, str):
        return "N/A"

    # Define suffixes for large denominations
    for unit in ['', 'K', 'M', 'B', 'T']:
        if abs(num) < 1000.0:
            return f"{num:3.2f}{unit}"
        num /= 1000.0
    return f"{num:.2f}P"


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""
    ticker_symbol = symbol.upper()
    # if not ticker_symbol.endswith(".LK"):
    #    ticker_symbol += ".N0000.LK"

    try:
        stock = yf.Ticker(ticker_symbol)

        # Fetch historical data (3 Month)
        history = stock.history(period="3mo")
        if history.empty:
            return None

        # Fetch company info for stats
        info = stock.info
        price = info.get("currentPrice") or info.get("regularMarketPrice")

        if price is None:
            if not history['Close'].empty:
                price = history['Close'].iloc[-1]
            else:
                return None

        return {
            "name": info.get("shortName") or info.get("longName") or ticker_symbol,
            "price": float(price),
            "symbol": ticker_symbol.split('.')[0],
            "prev_close": info.get("regularMarketPreviousClose", history['Close'].iloc[-1]),
            # Chart Data
            "chart_labels": history.index.strftime('%Y-%m-%d').tolist(),
            "chart_values": history['Close'].tolist(),
            # Key Stats
            "stats": {
                "market_cap": format_large_number(info.get("marketCap")),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "high_52w": info.get("fiftyTwoWeekHigh", "N/A"),
                "low_52w": info.get("fiftyTwoWeekLow", "N/A"),
                "volume": info.get("volume", "N/A"),
                "summary": info.get("longBusinessSummary", "No summary available.")
            }
        }
    except (ConnectionError, Timeout):
        print("Network Error: Could not connect to Yahoo Finance.")
    except Exception as e:
        print(f"Unexpected Error: {e}")
    return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
