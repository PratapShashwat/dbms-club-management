import os
import pymysql

print("Testing connection to Aiven MySQL...")

try:
    connection = pymysql.connect(
        host='mysql-2675b670-shashwatpsingh06-53ab.b.aivencloud.com',
        user='avnadmin',
        password=os.environ.get('DB_PASSWORD'),
        port=22017,
        database='defaultdb',
        ssl={'ssl': {'ssl-mode': 'REQUIRED'}}
    )
    
    with connection.cursor() as cursor:
        print("Connected! Fetching the list of tables...")
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database.")
        else:
            print("\n--- Tables in your Database ---")
            for table in tables:
                print(f"- {table[0]}")
            print("-------------------------------\n")
            
            # Let's insert a dummy Council just to prove we can write to it
            print("Testing INSERT into 'Council' table...")
            cursor.execute("INSERT INTO Council (Name, Description) VALUES ('Cultural Council', 'Manages cultural events')")
            connection.commit()
            
            # Fetch it back
            cursor.execute("SELECT * FROM Council;")
            councils = cursor.fetchall()
            print("\nData in 'Council' table:")
            for c in councils:
                print(c)
                
            # Clean up the dummy data
            cursor.execute("DELETE FROM Council WHERE Name = 'Cultural Council'")
            connection.commit()
            print("\nDummy data cleaned up successfully. Database is fully operational!")

except Exception as e:
    print(f"Error connecting or executing: {e}")
finally:
    if 'connection' in locals() and connection.open:
        connection.close()