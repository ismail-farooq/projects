import csv
import datetime
import pytz
import requests
import urllib
import uuid
import yfinance as yf
from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime, timedelta


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
    symbol = symbol.upper()
    try:
        # Fetch historical data for the past week
        stock_data = yf.download(symbol, period="1w", interval="1d", auto_adjust=True)
        if not stock_data.empty:
            last_price = stock_data["Close"].iloc[-1]
            return {"price": round(last_price, 2), "symbol": symbol}
        else:
            print(f"No data found for symbol {symbol}")
            return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

def _weather(location):
    APIKEY = 'c4986010e7bf7418c5afa912f8a8aadb'
    weather_data = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?q={location}&units=imperial&APPID={APIKEY}"
    )

    if weather_data.status_code == 404:
        return 404
    else: 
        weather_data = weather_data.json()
        temperature_F = round(weather_data['main']['temp'], 0)
        temperature_C = round((temperature_F - 32) * (5/9), 0)
        main = weather_data['weather'][0]['main']
        description = weather_data['weather'][0]['description']
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']
        location = weather_data['name']


        weather_details = [temperature_F, temperature_C, main, description, humidity, wind_speed, location]
        return weather_details
    
