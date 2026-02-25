# Toronto Hackathon Data — February 2026

Dataset for the Toronto Databricks Hackathon (February 2026). Combines real DineSafe inspection data from the City of Toronto with synthetic restaurant, order, menu, and review data.

## Quick Start

1. **Sign up** for a [Databricks free trial](https://www.databricks.com/try-databricks) if you don't have a workspace
2. **Clone this repo** into your workspace: `Workspace > Repos > Add Repo > paste the Git URL`
3. **Open** `notebooks/01_setup_data.py` and **Run All**
4. The notebook creates a `hackathon.toronto_restaurants` catalog/schema and loads all data as Delta tables

## Data Overview

Six CSV files and one PDF document covering the Toronto restaurant ecosystem:

| File | Rows | Description |
|------|-----:|-------------|
| `restaurants.csv` | 22,837 | Restaurant profiles — cuisine, location, price range, status |
| `orders.csv` | 99,996 | Customer delivery orders — timestamps, payment, totals |
| `order_items.csv` | 105,449 | Line items within each order — menu item, quantity, price |
| `menu_items.csv` | 195,674 | Full menus — item name, category, price, prep time, popularity |
| `inspections.csv` | 154,540 | Health inspection records — status, infractions, fines |
| `reviews.csv` | 30,000 | Customer reviews — ratings, text, food/delivery scores |
| `FOOD_Premises_ON.pdf` | — | Ontario food premises regulation document |

## Schema Details

### `restaurants.csv`
| Column | Type | Description |
|--------|------|-------------|
| restaurant_id | string | Unique ID (REST-XXXXX) |
| establishment_id | int | City establishment reference |
| name | string | Restaurant name |
| cuisine | string | Cuisine type (Indian, Vietnamese, Pizza, etc.) |
| establishment_type | string | Restaurant, Food Take Out, etc. |
| address | string | Street address |
| neighborhood | string | Toronto neighborhood (Scarborough, York, Etobicoke, etc.) |
| latitude / longitude | float | Geolocation |
| phone | string | Phone number |
| email | string | Contact email |
| price_range | string | `$`, `$-$$`, `$$`, `$$-$$$`, `$$$` |
| current_status | string | Latest inspection status (Pass, Conditional Pass, etc.) |
| min_inspections_per_year | int | Required annual inspections |
| average_rating | float | Average customer rating |
| total_reviews | int | Number of reviews |
| created_date | date | Date added to the system |

### `orders.csv`
| Column | Type | Description |
|--------|------|-------------|
| order_id | string | Unique ID (ORD-XXXXX) |
| customer_id | string | Customer reference (CUST-XXXXX) |
| restaurant_id | string | FK to restaurants |
| order_time | timestamp | When the order was placed |
| status | string | Order status (delivered, etc.) |
| payment_method | string | debit_card, credit_card, etc. |
| subtotal | float | Pre-tax amount |
| tax | float | Tax amount |
| tip | float | Tip amount |
| delivery_fee | float | Delivery charge |
| total_amount | float | Final total |
| delivery_address | string | Delivery destination |
| delivery_latitude / delivery_longitude | float | Delivery geolocation |
| driver_id | string | Driver reference (DRV-XXX) |
| estimated_delivery_time | int | Estimated delivery time in minutes |

### `order_items.csv`
| Column | Type | Description |
|--------|------|-------------|
| order_item_id | string | Unique ID (ITEM-XXXXX) |
| order_id | string | FK to orders |
| menu_item_id | string | FK to menu_items |
| quantity | int | Number ordered |
| unit_price | float | Price per item |
| subtotal | float | Line total |
| special_instructions | string | Customer notes (e.g., "Extra spicy") |

### `menu_items.csv`
| Column | Type | Description |
|--------|------|-------------|
| menu_item_id | string | Unique ID (MENU-XXXXX) |
| restaurant_id | string | FK to restaurants |
| item_name | string | Dish name |
| category | string | Entree, Appetizer, Dessert, etc. |
| description | string | Item description |
| price | float | Price |
| prep_time_minutes | int | Preparation time |
| popularity_score | float | Popularity rating (1-5) |
| is_available | boolean | Currently available |

### `inspections.csv`
| Column | Type | Description |
|--------|------|-------------|
| inspection_id | int | Unique inspection ID |
| restaurant_id | string | FK to restaurants |
| establishment_id | int | City establishment reference |
| inspection_date | date | Date of inspection |
| status | string | Pass, Conditional Pass, Closed |
| severity | string | Severity code (S - Significant, M - Minor, C - Crucial) |
| infraction_details | string | Description of infraction |
| action | string | Action taken (Notice to Comply, etc.) |
| outcome | string | Outcome of the action |
| amount_fined | float | Fine amount (if applicable) |
| severity_category | string | Not Applicable, Minor, Major, Critical |

### `reviews.csv`
| Column | Type | Description |
|--------|------|-------------|
| review_id | string | Unique ID (REV-XXXXX) |
| order_id | string | FK to orders |
| restaurant_id | string | FK to restaurants |
| customer_id | string | FK to customers |
| review_date | timestamp | When the review was posted |
| rating | int | Overall rating (1-5) |
| food_rating | int | Food quality rating |
| delivery_rating | int | Delivery experience rating |
| review_text | string | Free-text review |
| helpful_count | int | Number of "helpful" votes |

## Entity Relationship

```
restaurants ─┬── menu_items
             ├── inspections
             ├── reviews
             └── orders ── order_items ── menu_items
```

## Notebook

### `01_setup_data.py`

Databricks notebook that automates the full setup:

- Creates a **`hackathon`** catalog (configurable via widget)
- Creates a **`toronto_restaurants`** schema with two volumes (`dataset`, `documentation`)
- Copies all CSV and PDF files into the volumes
- Creates six Delta tables from the CSVs
- Prints a verification summary

Works on Databricks free trial — just clone the repo and run.

## Data Sources

- **`inspections.csv`** and **`FOOD_Premises_ON.pdf`** — Real data from the City of Toronto's [DineSafe](https://open.toronto.ca/dataset/dinesafe/) open data program
- All other files (restaurants, orders, order_items, menu_items, reviews) are synthetic, generated for hackathon purposes
