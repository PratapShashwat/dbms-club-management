import os
import pymysql
import json
import random

print("Connecting to Aiven MySQL for massive DB seeding & schema update...")
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
        # 1. Update Student Table
        try:
            cursor.execute("ALTER TABLE Student ADD COLUMN Phone_Number VARCHAR(15);")
            cursor.execute("ALTER TABLE Student ADD COLUMN Course VARCHAR(50);")
        except Exception as e:
            print(f"Schema update skipped/already applied: {e}")

        # 2. Add Councils & Clubs (Ensuring we have multiple)
        cursor.execute("INSERT IGNORE INTO Council (Council_ID, Name, Description) VALUES (1, 'Science & Tech Council', 'Tech clubs');")
        cursor.execute("INSERT IGNORE INTO Council (Council_ID, Name, Description) VALUES (2, 'Cultural Council', 'Art and culture');")
        
        clubs = [
            (1, 1, 'Programming Club', True),
            (2, 1, 'Robotics Club', False),
            (3, 2, 'Dance Club', True),
            (4, 2, 'Music Club', True)
        ]
        for c in clubs:
            cursor.execute("INSERT IGNORE INTO Club (Club_ID, Council_ID, Name, Is_Recruiting) VALUES (%s, %s, %s, %s)", c)

        # 3. Add Massive amount of Students
        students = []
        for i in range(200, 220):
            students.append((str(i), f"Student {i}", 2026, "CSE", f"B.Tech", f"user{i}@itbhu.ac.in", f"9999999{i}"))
        for s in students:
            cursor.execute("INSERT IGNORE INTO Student (Roll_Number, Name, Graduation_Year, Branch, Course, Email, Phone_Number) VALUES (%s, %s, %s, %s, %s, %s, %s)", s)

        # 4. Add POR Roles with new Privacy Toggles
        roles = [
            (10, 1, 1, 'SciTech GenSec', json.dumps(["MANAGE_CLUBS", "MANAGE_CLUB_PORS", "MANAGE_ROOMS", "CREATE_FORMS", "VIEW_EMAIL", "VIEW_PHONE"])),
            (11, 2, 3, 'Cultural GenSec', json.dumps(["MANAGE_CLUBS", "MANAGE_CLUB_PORS", "MANAGE_ROOMS", "CREATE_FORMS", "VIEW_EMAIL", "VIEW_PHONE"])),
            (12, 1, 1, 'Prog Secretary', json.dumps(["MANAGE_MEMBERS", "MANAGE_PORS", "CREATE_FORMS", "VIEW_EMAIL", "VIEW_PHONE"])),
            (13, 2, 3, 'Dance Secretary', json.dumps(["MANAGE_MEMBERS", "MANAGE_PORS", "CREATE_FORMS", "VIEW_EMAIL"])),
            (14, 1, 1, 'Prog Events Head', json.dumps(["VIEW_MEMBERS", "CREATE_FORMS"])),
        ]
        for r in roles:
            cursor.execute("INSERT IGNORE INTO POR_Role (Role_ID, Council_ID, Club_ID, Title, Permissions_JSON) VALUES (%s, %s, %s, %s, %s)", r)

        # 5. Add Memberships (Ensuring GenSec is in a club)
        cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        # GenSecs
        cursor.execute("INSERT IGNORE INTO Club_Membership (Membership_ID, Roll_Number, Club_ID, Role_ID, Academic_Year) VALUES (100, '200', 1, 10, '2026-2027')")
        cursor.execute("INSERT IGNORE INTO Club_Membership (Membership_ID, Roll_Number, Club_ID, Role_ID, Academic_Year) VALUES (101, '201', 3, 11, '2026-2027')")
        # Secys
        cursor.execute("INSERT IGNORE INTO Club_Membership (Membership_ID, Roll_Number, Club_ID, Role_ID, Academic_Year) VALUES (102, '202', 1, 12, '2026-2027')")
        cursor.execute("INSERT IGNORE INTO Club_Membership (Membership_ID, Roll_Number, Club_ID, Role_ID, Academic_Year) VALUES (103, '203', 3, 13, '2026-2027')")
        
        # General Members
        for i in range(204, 210):
            cursor.execute("INSERT IGNORE INTO Club_Membership (Roll_Number, Club_ID, Academic_Year) VALUES (%s, 1, '2026-2027')", (str(i),))
        for i in range(210, 215):
            cursor.execute("INSERT IGNORE INTO Club_Membership (Roll_Number, Club_ID, Academic_Year) VALUES (%s, 3, '2026-2027')", (str(i),))
        
        cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
        
    connection.commit()
    print("Massive DB seeded successfully with new Privacy schema!")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals() and connection.open:
        connection.close()
