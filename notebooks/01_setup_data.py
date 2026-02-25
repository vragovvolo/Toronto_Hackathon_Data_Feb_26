# Databricks notebook source
# MAGIC %md
# MAGIC # 01 — Upload Data & Create Tables
# MAGIC Reads CSV files and PDF from the bundle workspace files, uploads them to
# MAGIC Unity Catalog volumes, and creates Delta tables.

# COMMAND ----------

dbutils.widgets.text("catalog", "dazana_classic_ws_catalog")
dbutils.widgets.text("schema", "hackathon")

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
except Exception as e:
    print(f"Note: CREATE CATALOG skipped ({e}). Assuming catalog already exists.")

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {FQ}")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {FQ}.dataset")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {FQ}.documentation")

print("Schema and volumes ready.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Upload CSV and PDF files to volumes

# COMMAND ----------

import os, shutil, glob

bundle_root = os.path.dirname(os.path.dirname(os.path.abspath(dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get())))

# Workspace files are accessible via /Workspace prefix
ws_root = f"/Workspace{bundle_root}"
csv_dir = os.path.join(ws_root, "data", "csv")
pdf_dir = os.path.join(ws_root, "data", "pdf")

vol_dataset = f"/Volumes/{CATALOG}/{SCHEMA}/dataset"
vol_docs = f"/Volumes/{CATALOG}/{SCHEMA}/documentation"

csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
print(f"Found {len(csv_files)} CSV files in {csv_dir}")
for src in csv_files:
    fname = os.path.basename(src)
    dst = os.path.join(vol_dataset, fname)
    shutil.copy2(src, dst)
    print(f"  Copied {fname} -> {dst}")

pdf_src = os.path.join(pdf_dir, "FOOD_Premises_ON.pdf")
pdf_dst = os.path.join(vol_docs, "FOOD Premises ON.pdf")
shutil.copy2(pdf_src, pdf_dst)
print(f"  Copied PDF -> {pdf_dst}")

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
# MAGIC ## Verify

# COMMAND ----------

for table in TABLES:
    cnt = spark.table(f"{FQ}.{table}").count()
    print(f"  {FQ}.{table}: {cnt:,} rows")

dbutils.jobs.taskValues.set(key="tables_created", value=",".join(TABLES))
