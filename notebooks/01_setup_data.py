# Databricks notebook source
# MAGIC %md
# MAGIC # 01 — Setup: Create Catalog, Upload Data & Create Tables
# MAGIC
# MAGIC This notebook sets up everything you need for the hackathon:
# MAGIC 1. Creates a **`hackathon`** catalog and schema in Unity Catalog
# MAGIC 2. Creates volumes for dataset and documentation storage
# MAGIC 3. Uploads CSV and PDF files from the repo into the volumes
# MAGIC 4. Creates Delta tables from the CSV files
# MAGIC
# MAGIC **Prerequisites:**
# MAGIC - Databricks workspace (free trial works)
# MAGIC - Clone or upload this repo into your Databricks workspace via **Repos**
# MAGIC   (`Workspace > Repos > Add > Git URL`)
# MAGIC - Run this notebook on any cluster with Unity Catalog access

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration
# MAGIC
# MAGIC Change the catalog and schema names below if needed.
# MAGIC By default this creates `hackathon.toronto_restaurants`.

# COMMAND ----------

dbutils.widgets.text("catalog", "hackathon")
dbutils.widgets.text("schema", "toronto_restaurants")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
FQ = f"{CATALOG}.{SCHEMA}"

print(f"Target: {FQ}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create catalog, schema, and volumes

# COMMAND ----------

try:
    spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
    print(f"Catalog '{CATALOG}' is ready.")
except Exception as e:
    print(f"Note: Could not create catalog ({e}).")
    print("If you're on a free trial, try using your default catalog instead.")
    print("Update the 'catalog' widget above and re-run.")

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {FQ}")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {FQ}.dataset")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {FQ}.documentation")

print(f"Schema '{FQ}' and volumes are ready.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Grant access to all workspace users

# COMMAND ----------

try:
    spark.sql(f"GRANT ALL PRIVILEGES ON CATALOG {CATALOG} TO `account users`")
    spark.sql(f"GRANT ALL PRIVILEGES ON SCHEMA {FQ} TO `account users`")
    spark.sql(f"GRANT ALL PRIVILEGES ON VOLUME {FQ}.dataset TO `account users`")
    spark.sql(f"GRANT ALL PRIVILEGES ON VOLUME {FQ}.documentation TO `account users`")
    print("Granted full access to all workspace users (account users).")
except Exception as e:
    print(f"Note: Could not grant permissions ({e}).")
    print("You may need to be a catalog owner or admin to grant access.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Locate repo data files
# MAGIC
# MAGIC Automatically detects the repo root whether you cloned via Repos or
# MAGIC imported the notebook manually.

# COMMAND ----------

import os, shutil, glob

# Determine repo root from this notebook's location
try:
    nb_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
    repo_root = f"/Workspace{os.path.dirname(os.path.dirname(nb_path))}"
except Exception:
    # Fallback: prompt the user
    raise RuntimeError(
        "Could not auto-detect repo root. "
        "Make sure you cloned this repo via Workspace > Repos > Add > Git URL "
        "and are running the notebook from within the repo."
    )

csv_dir = os.path.join(repo_root, "data", "csv")
pdf_dir = os.path.join(repo_root, "data", "pdf")

print(f"Repo root : {repo_root}")
print(f"CSV dir   : {csv_dir}")
print(f"PDF dir   : {pdf_dir}")

# Quick sanity check
assert os.path.isdir(csv_dir), f"CSV directory not found at {csv_dir}"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Upload CSV and PDF files to volumes

# COMMAND ----------

vol_dataset = f"/Volumes/{CATALOG}/{SCHEMA}/dataset"
vol_docs = f"/Volumes/{CATALOG}/{SCHEMA}/documentation"

csv_files = sorted(glob.glob(os.path.join(csv_dir, "*.csv")))
print(f"Found {len(csv_files)} CSV files")

for src in csv_files:
    fname = os.path.basename(src)
    dst = os.path.join(vol_dataset, fname)
    shutil.copy2(src, dst)
    print(f"  Copied {fname} -> {dst}")

pdf_src = os.path.join(pdf_dir, "FOOD_Premises_ON.pdf")
if os.path.exists(pdf_src):
    pdf_dst = os.path.join(vol_docs, "FOOD_Premises_ON.pdf")
    shutil.copy2(pdf_src, pdf_dst)
    print(f"  Copied PDF -> {pdf_dst}")
else:
    print("  PDF not found, skipping.")

print("\nAll files uploaded to volumes.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Delta tables from CSVs

# COMMAND ----------

TABLES = ["restaurants", "inspections", "menu_items", "orders", "order_items", "reviews"]

for table in TABLES:
    csv_path = f"/Volumes/{CATALOG}/{SCHEMA}/dataset/{table}.csv"
    print(f"Creating {FQ}.{table} from {csv_path} ...")
    df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .option("multiLine", "true")
        .option("escape", '"')
        .csv(csv_path)
    )
    df.write.mode("overwrite").saveAsTable(f"{FQ}.{table}")
    cnt = spark.table(f"{FQ}.{table}").count()
    print(f"  {table}: {cnt:,} rows")

print("\nAll tables created successfully!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify tables

# COMMAND ----------

print(f"{'Table':<40} {'Rows':>10}")
print("-" * 52)
for table in TABLES:
    cnt = spark.table(f"{FQ}.{table}").count()
    print(f"  {FQ}.{table:<30} {cnt:>10,}")

print(f"\nDone! Your data is ready at catalog: {CATALOG}")
