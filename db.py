import psycopg2

# Connection string
conn = psycopg2.connect(
    dbname="neondb",
    user="neondb_owner",
    password="npg_Ufl1F3KzSZjT",
    host="ep-winter-meadow-a2idq0fp.eu-central-1.aws.neon.tech",
    port="5432",
    sslmode="require"
)

cur = conn.cursor()

# Get all tables
cur.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema='public'
""")
tables = cur.fetchall()

for table in tables:
    print(f"\n=== Table: {table[0]} ===")
    cur.execute(f"""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema='public' AND table_name='{table[0]}'
    """)
    columns = cur.fetchall()
    for col in columns:
        print(col)

cur.close()
conn.close()
