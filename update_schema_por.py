import os
import pymysql

print("Connecting to Aiven MySQL to add POR_Role matrix...")
try:
    connection = pymysql.connect(
        host='mysql-2675b670-shashwatpsingh06-53ab.b.aivencloud.com',
        user='avnadmin',
        password=os.environ.get('DB_PASSWORD'),
        port=22017,
        database='defaultdb',
        ssl={'ssl': {'ssl-mode': 'REQUIRED'}}
    )
    
    statements = [
        """CREATE TABLE IF NOT EXISTS POR_Role (
            Role_ID INT AUTO_INCREMENT PRIMARY KEY,
            Council_ID INT,
            Club_ID INT NULL, 
            Title VARCHAR(100),
            Permissions_JSON JSON,
            FOREIGN KEY (Council_ID) REFERENCES Council(Council_ID),
            FOREIGN KEY (Club_ID) REFERENCES Club(Club_ID)
        );""",
        "ALTER TABLE Club_Membership ADD COLUMN Role_ID INT NULL;",
        "ALTER TABLE Club_Membership ADD FOREIGN KEY (Role_ID) REFERENCES POR_Role(Role_ID);",
        "ALTER TABLE Club_Membership DROP COLUMN POR_Title;"
    ]

    with connection.cursor() as cursor:
        for stmt in statements:
            print(f"Executing: {stmt[:30]}...")
            cursor.execute(stmt)
            
    connection.commit()
    print("POR permissions matrix successfully integrated into database!")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals() and connection.open:
        connection.close()
