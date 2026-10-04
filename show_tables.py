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
with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES")
    for row in cursor.fetchall():
        print(row[0])
