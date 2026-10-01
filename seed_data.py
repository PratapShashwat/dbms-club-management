import os
import pymysql

print("Connecting to Aiven MySQL to insert dummy data...")
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
        "INSERT IGNORE INTO Student (Roll_Number, Name, Graduation_Year, Branch, Email) VALUES ('24075002', 'Abhinav Anand', 2028, 'CSE', 'abhinav@college.edu');",
        "INSERT IGNORE INTO Student (Roll_Number, Name, Graduation_Year, Branch, Email) VALUES ('24075080', 'Shashwat Pratap Singh', 2028, 'CSE', 'shashwat@college.edu');",
        
        "INSERT IGNORE INTO Council (Council_ID, Name, Description) VALUES (1, 'Science & Tech Council', 'Manages all technical clubs and events');",
        "INSERT IGNORE INTO Council (Council_ID, Name, Description) VALUES (2, 'Cultural Council', 'Manages cultural and arts clubs');",
        
        "INSERT IGNORE INTO Club (Club_ID, Name, Council_ID, Is_Recruiting) VALUES (1, 'Programming Club', 1, TRUE);",
        "INSERT IGNORE INTO Club (Club_ID, Name, Council_ID, Is_Recruiting) VALUES (2, 'Robotics Club', 1, FALSE);",
        "INSERT IGNORE INTO Club (Club_ID, Name, Council_ID, Is_Recruiting) VALUES (3, 'Fine Arts Club', 2, TRUE);",
        "INSERT IGNORE INTO Club (Club_ID, Name, Council_ID, Is_Recruiting) VALUES (4, 'Drama Club', 2, FALSE);",
        
        "INSERT IGNORE INTO Vertical (Vertical_ID, Name, Club_ID) VALUES (1, 'Frontend Development', 1);",
        "INSERT IGNORE INTO Vertical (Vertical_ID, Name, Club_ID) VALUES (2, 'Backend Development', 1);",
        "INSERT IGNORE INTO Vertical (Vertical_ID, Name, Club_ID) VALUES (3, 'Charcoal Sketching', 3);",
        
        "INSERT IGNORE INTO Room (Room_ID) VALUES (101);",
        "INSERT IGNORE INTO Room (Room_ID) VALUES (102);",
        "INSERT IGNORE INTO Room (Room_ID) VALUES (201);"
    ]

    with connection.cursor() as cursor:
        for stmt in statements:
            cursor.execute(stmt)
            
    connection.commit()
    print("Dummy data successfully inserted!")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals() and connection.open:
        connection.close()

