import pymysql
import os

connection = pymysql.connect(
    host='mysql-2675b670-shashwatpsingh06-53ab.b.aivencloud.com',
    user='avnadmin',
    password=os.environ.get('DB_PASSWORD'),
    port=22017,
    database='defaultdb',
    ssl={'ssl': {'ssl-mode': 'REQUIRED'}}
)

tables = ['Club', 'Council', 'Dynamic_Form', 'Club_Membership', 'Club_Room_Allocation']
with connection.cursor() as cursor:
    for table in tables:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN opt_version BIGINT DEFAULT 0")
            print(f"Added opt_version to {table}")
        except Exception as e:
            print(f"Error on {table}: {e}")
connection.commit()
connection.close()
