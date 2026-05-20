# Database Details

This project uses SQLite as the database.

## Database File

When you run the website, this file is created automatically:

```text
amazon_tracker_website.db
```

## Table Name

```text
products
```

## Columns

- `id` - product ID
- `product_name` - product name
- `product_url` - Amazon product URL
- `target_price` - desired price
- `current_price` - latest checked price
- `notify_email` - email address for notification
- `last_checked` - date and time when price was last checked
- `status` - product price status
- `notified` - whether email notification was already sent

## Important

You do not need to create the database manually. The website creates the database and table automatically when you run:

```bash
python -m flask --app website_app run --debug
```

The SQL table structure is also saved in:

```text
database.sql
```
