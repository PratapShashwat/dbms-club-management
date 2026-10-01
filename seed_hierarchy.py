import os
import pymysql
import json

print("Connecting to Aiven MySQL to seed hierarchy...")
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
        # 1. Insert more students
        students = [
            ("101", "Alice (GenSec - SciTech)", 2025, "CSE", "alice@itbhu.ac.in"),
            ("102", "Bob (Jt. GenSec - SciTech)", 2026, "ECE", "bob@itbhu.ac.in"),
            ("103", "Charlie (Secretary - Programming)", 2026, "CSE", "charlie@itbhu.ac.in"),
            ("104", "Diana (Jt. Secy - Programming)", 2027, "ME", "diana@itbhu.ac.in"),
            ("105", "Eve (Vertical Head - Backend)", 2027, "CSE", "eve@itbhu.ac.in"),
            ("106", "Frank (Mentor - Programming)", 2025, "CSE", "frank@itbhu.ac.in"),
            ("107", "Grace (Normal Member - Programming)", 2028, "MNC", "grace@itbhu.ac.in"),
        ]
        for s in students:
            cursor.execute("INSERT IGNORE INTO Student (Roll_Number, Name, Graduation_Year, Branch, Email) VALUES (%s, %s, %s, %s, %s)", s)

        # 2. Insert POR Roles
        # Council Level
        gensec_perm = json.dumps(["MANAGE_CLUBS", "MANAGE_CLUB_PORS", "MANAGE_ROOMS"])
        cursor.execute("INSERT IGNORE INTO POR_Role (Role_ID, Council_ID, Club_ID, Title, Permissions_JSON) VALUES (1, 1, NULL, 'General Secretary', %s)", (gensec_perm,))
        cursor.execute("INSERT IGNORE INTO POR_Role (Role_ID, Council_ID, Club_ID, Title, Permissions_JSON) VALUES (2, 1, NULL, 'Jt. General Secretary', %s)", (gensec_perm,))
        
        # Club Level (Programming Club = ID 1)
        secy_perm = json.dumps(["MANAGE_MEMBERS", "MANAGE_EVENTS", "CREATE_FORMS"])
        cursor.execute("INSERT IGNORE INTO POR_Role (Role_ID, Council_ID, Club_ID, Title, Permissions_JSON) VALUES (3, 1, 1, 'Secretary', %s)", (secy_perm,))
        cursor.execute("INSERT IGNORE INTO POR_Role (Role_ID, Council_ID, Club_ID, Title, Permissions_JSON) VALUES (4, 1, 1, 'Jt. Secretary', %s)", (secy_perm,))
        
        vert_perm = json.dumps(["VIEW_MEMBERS", "MANAGE_VERTICAL_EVENTS"])
        cursor.execute("INSERT IGNORE INTO POR_Role (Role_ID, Council_ID, Club_ID, Title, Permissions_JSON) VALUES (5, 1, 1, 'Backend Head', %s)", (vert_perm,))
        
        mentor_perm = json.dumps(["VIEW_ALL"])
        cursor.execute("INSERT IGNORE INTO POR_Role (Role_ID, Council_ID, Club_ID, Title, Permissions_JSON) VALUES (6, 1, 1, 'Mentor', %s)", (mentor_perm,))

        # 3. Assign Roles via Club_Membership (Wait, Council-level roles need to be linked to Council. Currently Club_Membership only links to Club_ID. 
        # For GenSec, we can leave Club_ID NULL or map them to a "Council HQ" dummy club. Since our schema maps Student->Club, let's map them to Club 1 but with Role 1 for now, or just let Club_ID be NULL if schema allows).
        # Our Club_Membership has Club_ID. Let's map GenSecs with Club_ID = NULL if allowed.
        # Check if Club_ID is nullable in Club_Membership. Yes, it was NOT NULL in my creation, but let's check.
        # Actually, GenSec is a council POR. They shouldn't be restricted to a single club. We might need to insert them with NULL Club_ID.
        
        memberships = [
            # Roll, Club_ID, Role_ID, Acad_Year
            ("101", None, 1, "2026-2027"), # Alice: GenSec
            ("102", None, 2, "2026-2027"), # Bob: Jt GenSec
            ("103", 1, 3, "2026-2027"),    # Charlie: Secy Programming
            ("104", 1, 4, "2026-2027"),    # Diana: Jt Secy
            ("105", 1, 5, "2026-2027"),    # Eve: Vertical Head
            ("106", 1, 6, "2026-2027"),    # Frank: Mentor
            ("107", 1, None, "2026-2027"), # Grace: Normal Member
        ]
        
        for m in memberships:
            # Need to disable foreign key checks temporarily if Club_ID is not nullable, but it should be fine.
            cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
            cursor.execute("INSERT IGNORE INTO Club_Membership (Roll_Number, Club_ID, Role_ID, Academic_Year) VALUES (%s, %s, %s, %s)", m)
            cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
            
    connection.commit()
    print("Hierarchy data successfully seeded!")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals() and connection.open:
        connection.close()
