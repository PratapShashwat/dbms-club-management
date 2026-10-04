import pymysql
import os

print("Connecting to Aiven MySQL...")
try:
    connection = pymysql.connect(
        host='mysql-2675b670-shashwatpsingh06-53ab.b.aivencloud.com',
        user='avnadmin',
        password=os.environ.get('DB_PASSWORD'),
        port=22017,
        database='defaultdb',
        ssl={'ssl': {'ssl-mode': 'REQUIRED'}}
    )
    
    with open('s""" ch """ema.sql', 'r') as f:
        sql_script = f.read()

    # Split script into individual statements
    statements = [s.strip() for s in sql_script.split(';') if s.strip()]

    with connection.cursor() as cursor:
        for statement in statements:
            # Skip comments if they are the only thing in the statement
            if statement.startswith('/*') and statement.endswith('*/'):
                continue
            print(f"Executing statement starting with: {statement[:30]}...")
            cursor.execute(statement)
            
    connection.commit()
    print("\n✅ Schema deployed successfully to Aiven!")
finally:
    if 'connection' in locals() and connection.open:
        connection.close()

