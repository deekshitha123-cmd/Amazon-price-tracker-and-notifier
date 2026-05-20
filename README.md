 # Amazon Product Price Tracker and Notifier

This is a web-based Amazon Product Price Tracker and Notifier built using Python Flask. The website allows users to add Amazon product links, set a target price, check product prices, and receive notification support when the product price reaches or goes below the target price.

## Features

- Add Amazon product details
- Store product name, Amazon URL, target price, and email
- View all tracked products
- Check current product price
- Manually update price if automatic checking fails
- Edit product details
- Delete tracked products
- Show product status
- Email notification support
- SQLite database storage

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS

## Project Structure

```text
amazon price tracker and notifier
│
├── website_app.py
├── requirements_web.txt
├── run_website.bat
├── .env.example
├── README.md
│
├── templates
│   ├── base.html
│   ├── index.html
│   └── edit.html
│
└── static
    └── style.css
```

## Installation

Open the project folder in VS Code.

Then open Terminal and run:

```bash
pip install -r requirements_web.txt
```

If `pip` is not recognized, try:

```bash
python -m pip install -r requirements_web.txt
```

## How to Run

Run this command in the VS Code terminal:

```bash
python -m flask --app website_app run --debug
```

Then open this link in your browser:

```text
http://127.0.0.1:5000
```

## Email Notification Setup

To enable email notifications, set these environment variables:

```bash
set SMTP_EMAIL=your-email@gmail.com
set SMTP_PASSWORD=your-app-password
set SMTP_HOST=smtp.gmail.com
set SMTP_PORT=587
```

For Gmail, use an App Password instead of your normal Gmail password.

## Important Note

Amazon may block automatic price checking because many websites prevent scraping. If automatic checking does not work, use the Manual Price option. The notifier still works when the manually entered current price is less than or equal to the target price.

## Conclusion

This project helps users track Amazon product prices and receive notification support when prices drop to their desired target.
