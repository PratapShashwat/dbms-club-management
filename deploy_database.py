import os
import re
import ssl
import pymysql
from urllib.parse import urlparse

# Get DB connection parameters from environment or defaults
db_url = os.environ.get("DB_URL")
db_host = os.environ.get("DB_HOST", "mysql-3d3a70fb-jr-8106.e.aivencloud.com")
db_port = int(os.environ.get("DB_PORT", "21774"))
db_user = os.environ.get("DB_USERNAME") or os.environ.get("DB_USER", "avnadmin")
db_password = os.environ.get("DB_PASSWORD", "")
db_name = os.environ.get("DB_NAME", "defaultdb")
use_ssl = os.environ.get("DB_SSL", "true").lower() in ("true", "1", "yes")

if db_url:
    clean_url = db_url.replace("jdbc:", "")
    parsed = urlparse(clean_url)
    if parsed.hostname:
        db_host = parsed.hostname
    if parsed.port:
        db_port = parsed.port
    if parsed.username:
        db_user = parsed.username
    if parsed.password:
        db_password = parsed.password
    if parsed.path and len(parsed.path) > 1:
        db_name = parsed.path.lstrip("/").split("?")[0]

print(f"Connecting to MySQL server at {db_host}:{db_port} as {db_user} (Database: {db_name})...")

ssl_ctx = ssl.create_default_context() if use_ssl else None
if ssl_ctx:
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

try:
    conn = pymysql.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name,
        ssl=ssl_ctx,
        autocommit=True
    )
    
    sql_file = "dump.sql" if os.path.exists("dump.sql") else "schema_complete.sql"
    print(f"Reading SQL script from: {sql_file}")

    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    sql_clean = re.sub(r'--.*?\n', '\n', sql_content)
    statements = [stmt.strip() for stmt in sql_clean.split(';') if stmt.strip()]

    print(f"Found {len(statements)} SQL statements to execute.")

    with conn.cursor() as cursor:
        for idx, statement in enumerate(statements, 1):
            first_line = statement.split('\n')[0][:50]
            print(f"[{idx}/{len(statements)}] Executing: {first_line}...")
            cursor.execute(statement)

    print("\n[SUCCESS] Database schema and data deployed successfully to your database!")

except Exception as e:
    print(f"\n[ERROR] Error deploying schema: {e}")
finally:
    if 'conn' in locals() and conn.open:
        conn.close()
