import os
import re
import smtplib
import sqlite3
from datetime import datetime
from email.message import EmailMessage
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Flask, flash, redirect, render_template, request, url_for


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "amazon_tracker_website.db")

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY", "change-this-secret-key")


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                product_url TEXT UNIQUE NOT NULL,
                target_price REAL NOT NULL,
                current_price REAL DEFAULT 0,
                notify_email TEXT,
                last_checked TEXT,
                status TEXT DEFAULT 'Not checked',
                notified INTEGER DEFAULT 0
            )
            """
        )


def get_all_products():
    with get_connection() as connection:
        return connection.execute(
            "SELECT * FROM products ORDER BY id DESC"
        ).fetchall()


def get_product(product_id):
    with get_connection() as connection:
        return connection.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()


def add_product(product_name, product_url, target_price, notify_email):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO products
            (product_name, product_url, target_price, notify_email, last_checked, status)
            VALUES (?, ?, ?, ?, '', 'Not checked')
            """,
            (product_name, product_url, target_price, notify_email),
        )


def update_product(product_id, product_name, product_url, target_price, notify_email):
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE products
            SET product_name = ?, product_url = ?, target_price = ?, notify_email = ?, notified = 0
            WHERE id = ?
            """,
            (product_name, product_url, target_price, notify_email, product_id),
        )


def delete_product(product_id):
    with get_connection() as connection:
        connection.execute("DELETE FROM products WHERE id = ?", (product_id,))


def save_price_result(product, current_price):
    last_checked = datetime.now().strftime("%Y-%m-%d %H:%M")
    target_reached = current_price <= product["target_price"]
    status = "Target reached" if target_reached else "Waiting for price drop"
    notified = product["notified"]

    if target_reached and product["notify_email"] and not product["notified"]:
        try:
            send_price_email(product, current_price)
            notified = 1
        except ValueError:
            status = "Target reached - email not configured"

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE products
            SET current_price = ?, last_checked = ?, status = ?, notified = ?
            WHERE id = ?
            """,
            (current_price, last_checked, status, notified, product["id"]),
        )
    return status


def fetch_amazon_price(product_url):
    req = Request(
        product_url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
            ),
            "Accept-Language": "en-IN,en;q=0.9",
        },
    )

    try:
        with urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8", errors="ignore")
    except (HTTPError, URLError, TimeoutError) as error:
        raise ValueError(f"Could not open Amazon page: {error}") from error

    patterns = [
        r'<span[^>]*class="[^"]*a-price-whole[^"]*"[^>]*>(.*?)</span>',
        r'<span[^>]*class="[^"]*a-offscreen[^"]*"[^>]*>(.*?)</span>',
        r'<span[^>]*id="priceblock_ourprice"[^>]*>(.*?)</span>',
        r'<span[^>]*id="priceblock_dealprice"[^>]*>(.*?)</span>',
    ]

    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        if match:
            price_text = clean_price(match.group(1))
            if price_text:
                return float(price_text)

    raise ValueError("Price not found. Amazon may have blocked automatic checking.")


def clean_price(value):
    text = re.sub(r"<[^>]+>", "", value)
    text = unescape(text)
    text = text.replace(",", "")
    match = re.search(r"([0-9]+(?:\.[0-9]{1,2})?)", text)
    return match.group(1) if match else ""


def send_price_email(product, current_price):
    sender = os.environ.get("SMTP_EMAIL")
    password = os.environ.get("SMTP_PASSWORD")
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "587"))

    if not sender or not password:
        raise ValueError("Email notification is not configured.")

    message = EmailMessage()
    message["Subject"] = "Amazon price target reached"
    message["From"] = sender
    message["To"] = product["notify_email"]
    message.set_content(
        f"Good news!\n\n"
        f"{product['product_name']} reached your target price.\n"
        f"Current price: {current_price}\n"
        f"Target price: {product['target_price']}\n\n"
        f"Product link:\n{product['product_url']}"
    )

    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(sender, password)
        smtp.send_message(message)


def validate_product_form(form):
    product_name = form.get("product_name", "").strip()
    product_url = form.get("product_url", "").strip()
    notify_email = form.get("notify_email", "").strip()
    target_price_text = form.get("target_price", "").strip()

    if not product_name or not product_url or not target_price_text:
        raise ValueError("Product name, Amazon URL, and target price are required.")

    if not product_url.startswith(("http://", "https://")):
        raise ValueError("Amazon URL must start with http:// or https://.")

    try:
        target_price = float(target_price_text)
    except ValueError as error:
        raise ValueError("Target price must be a number.") from error

    if target_price <= 0:
        raise ValueError("Target price must be greater than zero.")

    return product_name, product_url, target_price, notify_email


@app.route("/")
def index():
    return render_template("index.html", products=get_all_products())


@app.route("/add", methods=["POST"])
def add():
    try:
        product_name, product_url, target_price, notify_email = validate_product_form(request.form)
        add_product(product_name, product_url, target_price, notify_email)
        flash("Product added successfully.", "success")
    except sqlite3.IntegrityError:
        flash("This Amazon URL is already tracked.", "error")
    except ValueError as error:
        flash(str(error), "error")
    return redirect(url_for("index"))


@app.route("/edit/<int:product_id>", methods=["GET", "POST"])
def edit(product_id):
    product = get_product(product_id)
    if product is None:
        flash("Product not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        try:
            product_name, product_url, target_price, notify_email = validate_product_form(request.form)
            update_product(product_id, product_name, product_url, target_price, notify_email)
            flash("Product updated successfully.", "success")
            return redirect(url_for("index"))
        except sqlite3.IntegrityError:
            flash("Another product already uses this URL.", "error")
        except ValueError as error:
            flash(str(error), "error")

    return render_template("edit.html", product=product)


@app.route("/delete/<int:product_id>", methods=["POST"])
def delete(product_id):
    delete_product(product_id)
    flash("Product deleted successfully.", "success")
    return redirect(url_for("index"))


@app.route("/check/<int:product_id>", methods=["POST"])
def check_price(product_id):
    product = get_product(product_id)
    if product is None:
        flash("Product not found.", "error")
        return redirect(url_for("index"))

    try:
        current_price = fetch_amazon_price(product["product_url"])
        status = save_price_result(product, current_price)
        flash(f"{status}. Current price: {current_price}", "success")
    except ValueError as error:
        flash(f"{error} You can update the price manually.", "error")

    return redirect(url_for("index"))


@app.route("/manual-price/<int:product_id>", methods=["POST"])
def manual_price(product_id):
    product = get_product(product_id)
    if product is None:
        flash("Product not found.", "error")
        return redirect(url_for("index"))

    try:
        current_price = float(request.form.get("current_price", ""))
        status = save_price_result(product, current_price)
        flash(f"{status}. Current price: {current_price}", "success")
    except ValueError as error:
        flash(str(error), "error")

    return redirect(url_for("index"))


initialize_database()


if __name__ == "__main__":
    app.run(debug=True)
