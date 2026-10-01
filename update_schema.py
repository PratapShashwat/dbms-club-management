import os
import pymysql

print("Connecting to Aiven MySQL to update schema for Dynamic Forms...")
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
        "DROP TABLE IF EXISTS Form_Membership;",
        "DROP TABLE IF EXISTS Form_EventReg;",
        "DROP TABLE IF EXISTS Form_RoomAccess;",
        
        """CREATE TABLE Dynamic_Form (
            Form_ID INT AUTO_INCREMENT PRIMARY KEY,
            Club_ID INT,
            Title VARCHAR(150) NOT NULL,
            Form_Type VARCHAR(50) NOT NULL, 
            Target_Audience VARCHAR(50) NOT NULL,
            Questions_JSON JSON,
            FOREIGN KEY (Club_ID) REFERENCES Club(Club_ID)
        );""",
        
        """CREATE TABLE Form_Submission (
            Submission_ID INT AUTO_INCREMENT PRIMARY KEY,
            Form_ID INT,
            Roll_Number VARCHAR(20),
            Answers_JSON JSON,
            Status VARCHAR(20) DEFAULT 'Pending',
            FOREIGN KEY (Form_ID) REFERENCES Dynamic_Form(Form_ID),
            FOREIGN KEY (Roll_Number) REFERENCES Student(Roll_Number)
        );"""
    ]

    with connection.cursor() as cursor:
        for stmt in statements:
            print(f"Executing: {stmt[:30]}...")
            cursor.execute(stmt)
            
    connection.commit()
    print("Schema updated successfully! Old tables dropped, Dynamic Form engine installed.")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals() and connection.open:
        connection.close()
