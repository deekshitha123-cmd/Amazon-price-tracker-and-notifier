# Amazon Product Price Tracker and Notifier Website

This is a Flask website for tracking Amazon product prices and sending an email notification when a product reaches the target price.

## Features

- Add Amazon product name, URL, target price, and notify email
- View all tracked products in a table
- Check current price from Amazon
- Manually save current price if Amazon blocks automatic checking
- Edit and delete tracked products
- Send email notification when current price is less than or equal to target price
- Store data in SQLite

## Project Files

- `website_app.py` - Flask backend, database logic, price checker, and email notifier
- `templates/base.html` - common page layout
- `templates/index.html` - home page and tracked product table
- `templates/edit.html` - edit product page
- `static/style.css` - website styling
- `requirements_web.txt` - required Python package
- `.env.example` - sample email settings
- `run_website.bat` - Windows run command

## Install

Install Python first. Then run:

```bash
pip install -r requirements_web.txt
```

## Run

```bash
python -m flask --app website_app run --debug
```

Open:

```text
http://127.0.0.1:5000
```

## Email Notification Setup

Set these environment variables before running the website:

```bash
set APP_SECRET_KEY=change-this-secret-key
set SMTP_HOST=smtp.gmail.com
set SMTP_PORT=587
set SMTP_EMAIL=your-email@gmail.com
set SMTP_PASSWORD=your-app-password
```

For Gmail, use an app password, not your normal Gmail password.

## Important Note

Amazon may block automatic price checking or change its page HTML. That is why this website also includes manual price update. The notifier still works when you save a manual current price below the target price.
