import sqlite3
import pandas as pd


# -------------------------------
# Database Connection
# -------------------------------
DB_PATH = "../hospital_data.db"
OUTPUT_FILE = "../reports/validation_report.xlsx"


def get_connection():
    return sqlite3.connect(DB_PATH)


# -------------------------------
# Missing Usage
# -------------------------------
def get_missing_usage(conn):

    query = """
    SELECT i.med_id,
           i.med_name,
           i.current_inventory AS quantity,
           i.location
    FROM inventory i
    LEFT JOIN usage u
        ON i.med_id = u.med_id
    WHERE u.med_id IS NULL
    """

    return pd.read_sql(query, conn)


# -------------------------------
# Inventory vs Purchases
# -------------------------------
def get_inventory_vs_purchases(conn):

    query = """
    SELECT i.med_id,
           i.med_name,
           i.current_inventory,
           IFNULL(SUM(p.quantity),0) AS total_purchased
    FROM inventory i
    LEFT JOIN purchases p
        ON i.med_id = p.med_id
    GROUP BY i.med_id, i.med_name, i.current_inventory
    """

    return pd.read_sql(query, conn)


# -------------------------------
# Overused Medications
# -------------------------------
def get_overused_medications(conn):

    query = """
    SELECT
        i.med_id,
        i.med_name,

        -- Estimated standard limits
        CASE
            WHEN i.med_name = 'Morphine' THEN 60
            WHEN i.med_name = 'Insulin' THEN 180
            WHEN i.med_name = 'Heparin' THEN 75
            WHEN i.med_name = 'Fentanyl' THEN 50
            WHEN i.med_name = 'Oxycodone' THEN 40
            WHEN i.med_name = 'Midazolam' THEN 30
            ELSE 50
        END AS standard_daily_limit,

        ROUND(AVG(u.quantity),2) AS avg_daily_usage

    FROM inventory i
    JOIN usage u
        ON i.med_id = u.med_id

    GROUP BY i.med_id, i.med_name
    """

    df = pd.read_sql(query, conn)

    # Calculate overuse
    df["overuse_amount"] = df["avg_daily_usage"] - df["standard_daily_limit"]

    # Assign risk level
    def risk_flag(x):

        if x > 30:
            return "High"
        elif x > 15:
            return "Medium"
        elif x > 0:
            return "Low"
        else:
            return "Normal"

    df["risk_level"] = df["overuse_amount"].apply(risk_flag)

    # Only show overused meds
    df = df[df["overuse_amount"] > 0]

    return df


# -------------------------------
# Main Pipeline
# -------------------------------
def main():

    conn = get_connection()

    try:
        print("Running data validation checks...")

        missing_df = get_missing_usage(conn)
        inventory_df = get_inventory_vs_purchases(conn)
        overuse_df = get_overused_medications(conn)

        with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:

            missing_df.to_excel(
                writer,
                sheet_name="Missing Usage",
                index=False
            )

            inventory_df.to_excel(
                writer,
                sheet_name="Inventory vs Purchases",
                index=False
            )

            overuse_df.to_excel(
                writer,
                sheet_name="Overused Medications",
                index=False
            )

        print("Validation report generated:")
        print(OUTPUT_FILE)

    finally:
        conn.close()


# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    main()
import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect('../hospital_data.db')

# 1 Medications with no usage
missing_usage_query = """
SELECT 
    i.med_id,
    i.med_name,
    i.quantity,
    i.location
FROM inventory i
LEFT JOIN usage_log u
    ON i.med_id = u.med_id
WHERE u.med_id IS NULL;
"""
missing_usage = pd.read_sql_query(missing_usage_query, conn)

# 2️ Inventory vs Purchases
inventory_reconcile_query = """
SELECT
    i.med_id,
    i.med_name,
    i.quantity AS current_inventory,
    IFNULL(SUM(p.qty_purchased), 0) AS total_purchased
FROM inventory i
LEFT JOIN purchases p
    ON i.med_id = p.med_id
GROUP BY i.med_id, i.med_name, i.quantity;
"""
inventory_reconcile = pd.read_sql_query(inventory_reconcile_query, conn)

# 3️ Overused medications
overused_query = """
SELECT
    u.med_id,
    i.med_name,
    i.quantity AS inventory,
    SUM(u.used_qty) AS total_used
FROM usage_log u
JOIN inventory i
    ON u.med_id = i.med_id
GROUP BY u.med_id, i.med_name, i.quantity
HAVING total_used > inventory;
"""
overused = pd.read_sql_query(overused_query, conn)

# 4️ Write all reports to Excel
with pd.ExcelWriter('../reports/validation_report.xlsx') as writer:
    missing_usage.to_excel(writer, sheet_name='Missing Usage', index=False)
    inventory_reconcile.to_excel(writer, sheet_name='Inventory vs Purchases', index=False)
    overused.to_excel(writer, sheet_name='Overused Medications', index=False)

print(" Validation report generated in /reports/validation_report.xlsx")

# Close the connection
conn.close()

