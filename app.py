from flask import Flask, flash, session, render_template, Response, redirect, url_for, request
import os, datetime
import time
from cs50 import SQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import cv2

from helpers import apology, login_required, lookup, usd

app = Flask(__name__)

app.jinja_env.filters["usd"] = usd
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///finance.db")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["POST","GET"])
def home():
    cap.release()
    return render_template("home.html")

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)
def detect_faces(frame):
    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # Draw rectangles around detected faces and add face numbers
    face_number = 0
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (36, 255, 12), 2)
        face_number += 1
        cv2.putText(frame, f'Face {face_number}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    # Add the total number of faces detected to the frame
    cv2.putText(frame, f'Total Faces: {face_number}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    cv2.putText(frame, f'Press Q to return to Home Page', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    return frame

def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = detect_faces(frame)

        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


            
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera_feed')
def camera_feed():
    cap = cv2.VideoCapture(0)
    time.sleep(3)
    return render_template("video_feed.html")

@app.route("/trade")
@login_required
def trade():
    owned_stocks = db.execute("SELECT * FROM purchases WHERE user_ID=?", session["user_id"])

    return render_template("index.html", owned_stocks=owned_stocks)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        stock_symbol = request.form.get("symbol")
        stock = lookup(stock_symbol)
        shares = round(int(request.form.get("shares")))

        if not stock_symbol:
            return apology("Enter a stock symbol!")
        if not stock:
            return apology("Enter a valid stock symbol")
        if shares < 0:
            return apology("Cannot buy negative stocks! Enter a positive number")

        available_balance = db.execute("SELECT cash FROM users WHERE id=?", session["user_id"])
        total_price = stock["price"] * shares

        if available_balance[0]["cash"] < total_price:
            return apology("Not enough funds to purchase shares")

        remaining_balance = available_balance[0]["cash"] - total_price
        db.execute("UPDATE users SET cash = ? WHERE id = ?", remaining_balance, session["user_id"])

        existing_stock = db.execute("SELECT * FROM purchases WHERE user_id=? AND share_name=?",
                                    session["user_id"], stock["symbol"])

        date = datetime.datetime.now()
        if existing_stock:
            new_shares = shares + int(existing_stock[0]["number_of_shares"])
            db.execute("UPDATE purchases SET number_of_shares=? WHERE id=?",
                       new_shares, existing_stock[0]["ID"])
        else:
            db.execute("INSERT INTO purchases \
                   (user_ID, share_name, number_of_shares, total_price, date_of_purchase)\
                    VALUES (?, ?, ?, ?, ?)",
                       session["user_id"], stock["symbol"], shares, total_price, date)

        db.execute("INSERT INTO transaction_history \
                        (transaction_type, name_of_stock ,number_of_shares, unit_price, total_price, date_of_transaction, user_ID)\
                        VALUES (?,?,?,?,?,?,?)",
                   "BOUGHT", stock["symbol"], shares, stock["price"],  stock["price"]*shares, date, session["user_id"])

        flash("Stock purchased!")

        return redirect("/trade")
    else:
        return render_template("buy.html", active_tab = 'buy')


@app.route("/history")
@login_required
def history():
    history = db.execute("SELECT * FROM transaction_history WHERE user_ID = ?", session["user_id"])
    return render_template("history.html", history=history, active_tab = 'history')


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
        session["username"] = db.execute(
            "SELECT username FROM users WHERE id = ?", session["user_id"]
        )[0]["username"]
        session["cash"] = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"]
        )[0]["cash"]

        flash(f"Logged in as {rows[0]['username']}!")

        # Redirect user to home page
        return redirect("/trade")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/trade")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        stock_symbol = request.form.get("symbol")
        if not stock_symbol:
            return apology("Enter a stock symbol!")

        stock = lookup(stock_symbol)
        if not stock:
            return apology("Enter a valid stock symbol")

        name = stock["symbol"]
        price = usd(stock["price"])
        return render_template("quoted.html", name=name, price=price, active_tab = 'quote')

    else:
        return render_template("quote.html", active_tab = 'quote')


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("Enter a username to register")
        if not password:
            return apology("Enter password to register")
        if not confirmation:
            return apology("Confirm password to register")
        if password != confirmation:
            return apology("Passwords do not match")

        hashed_password = generate_password_hash(password=password)
        try:
            user = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
                              username, hashed_password)
        except:
            return apology("Username already exists")

        session["user_id"] = user
        flash("Registered!")

        return redirect("/trade")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":
        stock_symbol = request.form.get("symbol")
        stock = lookup(stock_symbol)
        try:
            number_of_shares = int(request.form.get("shares"))
        except ValueError:
            return apology("Enter a value")

        if not stock:
            return apology("Enter a valid stock symbol")
        if not number_of_shares:
            return apology("Enter the number of stocks to sell")
        if number_of_shares < 0:
            return apology("Cannot sell negative stocks! Enter a positive number")

        availble_shares = db.execute(
            "SELECT share_name, number_of_shares FROM purchases WHERE share_name = ? AND user_id = ?", stock_symbol, session["user_id"])
        if availble_shares[0]["number_of_shares"] < number_of_shares:
            flash(f"{stock_symbol} sold successfully for {stock['price']}")

        remaining_shares = availble_shares[0]["number_of_shares"] - number_of_shares

        existing_stock = db.execute("SELECT * FROM purchases WHERE user_id=? AND share_name=?",
                                    session["user_id"], stock["symbol"])
        db.execute("UPDATE purchases SET number_of_shares=? WHERE id=?",
                   remaining_shares, existing_stock[0]["ID"])

        available_balance = db.execute("SELECT cash FROM users WHERE id=?", session["user_id"])

        remaining_balance = available_balance[0]["cash"] + \
            (existing_stock[0]["total_price"] * number_of_shares)

        db.execute("UPDATE users SET cash = ? WHERE id = ?", remaining_balance, session["user_id"])

        date = datetime.datetime.now()
        db.execute("INSERT INTO transaction_history\
                (transaction_type, name_of_stock ,number_of_shares, unit_price, total_price, date_of_transaction, user_ID)\
                VALUES (?,?,?,?,?,?,?)",
                   "SOLD", stock["symbol"], number_of_shares, stock["price"],  stock["price"]*number_of_shares, date, session["user_id"])

        flash(f"{stock_symbol} sold successfully for {stock['price']}")
        return redirect("/trade")
    else:
        owned_stocks = db.execute("SELECT * FROM purchases WHERE user_id=?", session["user_id"])
        return render_template("sell.html", owned_stocks=owned_stocks, active_tab = 'sell')


if __name__ == "__main__":
    app.run(debug=True)  

