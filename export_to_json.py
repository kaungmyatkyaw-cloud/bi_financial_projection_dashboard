import os
import json
import pandas as pd
from sshtunnel import SSHTunnelForwarder
import pymysql
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta

# 1. Load Configurations & Setup Paths
ENV_PATH = r"C:\Users\kye58\marathon-projects\data_posting.env"
SSH_KEY_PATH = r"C:\Users\kye58\.ssh\id_ed25519"

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

TARGET_TABLE = "business_financials_normalized"

SSH_HOST = "188.166.249.72"
SSH_PORT = 22
SSH_USER = "root"
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_DB = "analytic_db"
MYSQL_USER = "bi_admin"
MYSQL_PW = "kaungmyat@BI2026"

# Mapping database categories (normalized to spaces) to frontend JSON keys
CATEGORY_MAPPING = {
    "revenue": "rev",
    "cogs": "cogs",
    "gp 1": "gp1",
    "gp1": "gp1",
    "fixed cost": "fixed",
    "variable cost": "variable",
    "other income & expenses": "other",
    "other inc&exp": "other",
    "other inc &exp": "other",
    "profit or loss": "pnlDB",
    "pnl": "pnlDB",
}

def normalize_category(val: str) -> str:
    # Convert underscores to spaces, collapse multiple spaces, and lowercase
    return " ".join(str(val).replace("_", " ").split()).lower()

print("Establishing SSH Tunnel to MySQL Server...")
tunnel = SSHTunnelForwarder(
    (SSH_HOST, SSH_PORT),
    ssh_username=SSH_USER,
    ssh_pkey=SSH_KEY_PATH,
    remote_bind_address=(MYSQL_HOST, MYSQL_PORT)
)
with tunnel:
    print(f"SSH Tunnel established. Local bind port: {tunnel.local_bind_port}")

    connection = pymysql.connect(
        host='127.0.0.1',
        port=tunnel.local_bind_port,
        user=MYSQL_USER,
        password=MYSQL_PW,
        database=MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            # A. Dynamically get all distinct historical months, sorted
            cursor.execute(f"""
                SELECT DISTINCT financial_date
                FROM {TARGET_TABLE}
                ORDER BY financial_date ASC
            """)
            dates_result = cursor.fetchall()

            if not dates_result:
                raise ValueError("No data found in the database.")

            # Preserve chronological order without duplicate 'Mon-YY' labels
            months_h = []
            seen_months = set()
            for row in dates_result:
                label = pd.to_datetime(row['financial_date']).strftime('%b-%y')
                if label not in seen_months:
                    seen_months.add(label)
                    months_h.append(label)

            # B. Dynamically generate the next 6 months for MONTHS_P
            last_date = pd.to_datetime(dates_result[-1]['financial_date'])
            months_p = []
            for i in range(1, 7):
                next_month = last_date + relativedelta(months=i)
                months_p.append(next_month.strftime('%b-%y'))

            current_month_idx = len(months_h)
            print(f"Detected Historical Months ({len(months_h)}): {months_h}")
            print(f"Generated Projection Months (6): {months_p}")

            # C. Fetch all financial data
            cursor.execute(f"SELECT financial_date, category, business_unit, amount FROM {TARGET_TABLE}")
            rows = cursor.fetchall()
            df = pd.DataFrame(rows)

            if df.empty:
                raise ValueError("No rows returned from financial table.")

            # Format dates to match 'Mon-YY' and normalize text fields
            df['month_label'] = pd.to_datetime(df['financial_date']).dt.strftime('%b-%y')
            df['category_norm'] = df['category'].apply(normalize_category)
            df['business_unit'] = df['business_unit'].astype(str).str.strip()
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)
            # df['amount'] ကို numeric ပြောင်းပြီးနောက် Million MMK (1e6) သို့ ပြောင်းခြင်း
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0) / 1_000_000.0

            # Debug check: print distinct normalized categories found in DB
            print("Distinct normalized categories in DB:", sorted(df['category_norm'].unique()))

            # D. Build the RAW data structure aligned to months_h
            raw_data = {}
            for bu in sorted(df['business_unit'].unique()):
                bu_df = df[df['business_unit'] == bu]
                raw_data[bu] = {
                    "rev": [0.0] * len(months_h),
                    "cogs": [0.0] * len(months_h),
                    "gp1": [0.0] * len(months_h),
                    "fixed": [0.0] * len(months_h),
                    "variable": [0.0] * len(months_h),
                    "other": [0.0] * len(months_h),
                    "pnlDB": [0.0] * len(months_h)
                }

                for cat_norm, json_key in CATEGORY_MAPPING.items():
                    cat_df = bu_df[bu_df['category_norm'] == cat_norm]
                    if cat_df.empty:
                        continue

                    month_sums = cat_df.groupby('month_label')['amount'].sum().to_dict()
                    aligned_data = [
                        round(raw_data[bu][json_key][idx] + float(month_sums.get(month, 0.0)), 2)
                        for idx, month in enumerate(months_h)
                    ]
                    raw_data[bu][json_key] = aligned_data

            # E. Compile final JSON payload
            output_payload = {
                "months_h": months_h,
                "months_p": months_p,
                "current_month_idx": current_month_idx,
                "raw": raw_data
            }

            # F. Save to JSON file
            output_file = "data.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_payload, f, indent=2)

            print(f"✅ Successfully exported dynamic data to {output_file}")

    except Exception as e:
        print(f"❌ Error occurred during DB operation: {e}")
        raise e
    finally:
        connection.close()