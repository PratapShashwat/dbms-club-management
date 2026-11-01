-- =======================================================
-- Complete Schema and Massive Seed Script for Club Management System
-- Fully synced with all 13 JPA Entities and Optimistic Locking (@Version)
-- =======================================================

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS Form_Submission;
DROP TABLE IF EXISTS Dynamic_Form;
DROP TABLE IF EXISTS Event_Involvement;
DROP TABLE IF EXISTS Club_Room_Allocation;
DROP TABLE IF EXISTS Club_Membership;
DROP TABLE IF EXISTS Room;
DROP TABLE IF EXISTS Event;
DROP TABLE IF EXISTS Vertical;
DROP TABLE IF EXISTS POR_Role;
DROP TABLE IF EXISTS Club;
DROP TABLE IF EXISTS Council;
DROP TABLE IF EXISTS Student;
DROP TABLE IF EXISTS System_Log;

-- 1. Student Table
CREATE TABLE Student (
    Roll_Number VARCHAR(20) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Graduation_Year INT,
    Branch VARCHAR(50),
    Course VARCHAR(50),
    Email VARCHAR(100) NOT NULL UNIQUE,
    Phone_Number VARCHAR(15),
    Password VARCHAR(100)
);

-- 2. Council Table
CREATE TABLE Council (
    Council_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Description TEXT,
    opt_version BIGINT DEFAULT 0
);

-- 3. Club Table
CREATE TABLE Club (
    Club_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Council_ID INT,
    Is_Recruiting BOOLEAN DEFAULT FALSE,
    opt_version BIGINT DEFAULT 0,
    FOREIGN KEY (Council_ID) REFERENCES Council(Council_ID) ON DELETE SET NULL
);

-- 4. Vertical Table
CREATE TABLE Vertical (
    Vertical_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL,
    Club_ID INT,
    FOREIGN KEY (Club_ID) REFERENCES Club(Club_ID) ON DELETE CASCADE
);

-- 5. POR_Role Table
CREATE TABLE POR_Role (
    Role_ID INT AUTO_INCREMENT PRIMARY KEY,
    Council_ID INT,
    Club_ID INT NULL,
    Title VARCHAR(100) NOT NULL,
    Permissions_JSON JSON,
    FOREIGN KEY (Council_ID) REFERENCES Council(Council_ID) ON DELETE CASCADE,
    FOREIGN KEY (Club_ID) REFERENCES Club(Club_ID) ON DELETE CASCADE
);

-- 6. Club_Membership Table
CREATE TABLE Club_Membership (
    Membership_ID INT AUTO_INCREMENT PRIMARY KEY,
    Roll_Number VARCHAR(20),
    Club_ID INT,
    Vertical_ID INT NULL,
    Role_ID INT NULL,
    Academic_Year VARCHAR(10),
    opt_version BIGINT DEFAULT 0,
    FOREIGN KEY (Roll_Number) REFERENCES Student(Roll_Number) ON DELETE CASCADE,
    FOREIGN KEY (Club_ID) REFERENCES Club(Club_ID) ON DELETE CASCADE,
    FOREIGN KEY (Vertical_ID) REFERENCES Vertical(Vertical_ID) ON DELETE SET NULL,
    FOREIGN KEY (Role_ID) REFERENCES POR_Role(Role_ID) ON DELETE SET NULL
);

-- 7. Room Table
CREATE TABLE Room (
    Room_ID INT PRIMARY KEY
);

-- 8. Club_Room_Allocation Table
CREATE TABLE Club_Room_Allocation (
    Allocation_ID INT AUTO_INCREMENT PRIMARY KEY,
    Club_ID INT,
    Room_ID INT,
    Academic_Year VARCHAR(10),
    opt_version BIGINT DEFAULT 0,
    FOREIGN KEY (Club_ID) REFERENCES Club(Club_ID) ON DELETE CASCADE,
    FOREIGN KEY (Room_ID) REFERENCES Room(Room_ID) ON DELETE CASCADE
);

-- 9. Event Table
CREATE TABLE Event (
    Event_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(150) NOT NULL,
    Club_ID INT,
    Event_Date DATE,
    Academic_Year VARCHAR(10),
    FOREIGN KEY (Club_ID) REFERENCES Club(Club_ID) ON DELETE CASCADE
);

-- 10. Event_Involvement Table
CREATE TABLE Event_Involvement (
    Involvement_ID INT AUTO_INCREMENT PRIMARY KEY,
    Roll_Number VARCHAR(20),
    Event_ID INT,
    Role_Category VARCHAR(50),
    Specific_Role VARCHAR(50),
    Result_Details TEXT,
    FOREIGN KEY (Roll_Number) REFERENCES Student(Roll_Number) ON DELETE CASCADE,
    FOREIGN KEY (Event_ID) REFERENCES Event(Event_ID) ON DELETE CASCADE
);

-- 11. Dynamic_Form Table
CREATE TABLE Dynamic_Form (
    Form_ID INT AUTO_INCREMENT PRIMARY KEY,
    Club_ID INT,
    Title VARCHAR(150) NOT NULL,
    Form_Type VARCHAR(50) NOT NULL,
    Target_Audience VARCHAR(50) NOT NULL,
    Questions_JSON JSON,
    Created_By VARCHAR(20),
    opt_version BIGINT DEFAULT 0,
    FOREIGN KEY (Club_ID) REFERENCES Club(Club_ID) ON DELETE CASCADE,
    FOREIGN KEY (Created_By) REFERENCES Student(Roll_Number) ON DELETE SET NULL
);

-- 12. Form_Submission Table
CREATE TABLE Form_Submission (
    Submission_ID INT AUTO_INCREMENT PRIMARY KEY,
    Form_ID INT,
    Roll_Number VARCHAR(20),
    Answers_JSON JSON,
    Status VARCHAR(20) DEFAULT 'Pending',
    FOREIGN KEY (Form_ID) REFERENCES Dynamic_Form(Form_ID) ON DELETE CASCADE,
    FOREIGN KEY (Roll_Number) REFERENCES Student(Roll_Number) ON DELETE CASCADE
);

-- 13. System_Log Table
CREATE TABLE System_Log (
    logId INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    actor VARCHAR(255),
    action VARCHAR(255),
    details VARCHAR(1000)
);

SET FOREIGN_KEY_CHECKS = 1;

-- =======================================================
-- MASSIVE SEED DATA
-- =======================================================

-- 1. Students (SuperAdmin + Students 101-107 + Students 200-219 + Core Members)
INSERT INTO Student (Roll_Number, Name, Graduation_Year, Branch, Course, Email, Phone_Number, Password) VALUES
('0', 'Super Admin', 2025, 'ADMIN', 'ADMIN', 'admin@college.edu', '9999999999', 'superadmin'),
('24075002', 'Abhinav Anand', 2028, 'CSE', 'B.Tech', 'abhinav@college.edu', '9876543210', '24075002'),
('24075080', 'Shashwat Pratap Singh', 2028, 'CSE', 'B.Tech', 'shashwat@college.edu', '9876543211', '24075080'),
('101', 'Alice (GenSec - SciTech)', 2025, 'CSE', 'B.Tech', 'alice@itbhu.ac.in', '9876543212', '101'),
('102', 'Bob (Jt. GenSec - SciTech)', 2026, 'ECE', 'B.Tech', 'bob@itbhu.ac.in', '9876543213', '102'),
('103', 'Charlie (Secretary - Programming)', 2026, 'CSE', 'B.Tech', 'charlie@itbhu.ac.in', '9876543214', '103'),
('104', 'Diana (Jt. Secy - Programming)', 2027, 'ME', 'B.Tech', 'diana@itbhu.ac.in', '9876543215', '104'),
('105', 'Eve (Vertical Head - Backend)', 2027, 'CSE', 'B.Tech', 'eve@itbhu.ac.in', '9876543216', '105'),
('106', 'Frank (Mentor - Programming)', 2025, 'CSE', 'B.Tech', 'frank@itbhu.ac.in', '9876543217', '106'),
('107', 'Grace (Member - Programming)', 2028, 'MNC', 'B.Tech', 'grace@itbhu.ac.in', '9876543218', '107'),
('200', 'Student 200 (SciTech GenSec)', 2026, 'CSE', 'B.Tech', 'user200@itbhu.ac.in', '9999999200', '200'),
('201', 'Student 201 (Cultural GenSec)', 2026, 'ECE', 'B.Tech', 'user201@itbhu.ac.in', '9999999201', '201'),
('202', 'Student 202 (Prog Secretary)', 2026, 'CSE', 'B.Tech', 'user202@itbhu.ac.in', '9999999202', '202'),
('203', 'Student 203 (Dance Secretary)', 2026, 'MECH', 'B.Tech', 'user203@itbhu.ac.in', '9999999203', '203'),
('204', 'Student 204', 2026, 'CSE', 'B.Tech', 'user204@itbhu.ac.in', '9999999204', '204'),
('205', 'Student 205', 2026, 'ECE', 'B.Tech', 'user205@itbhu.ac.in', '9999999205', '205'),
('206', 'Student 206', 2026, 'EEE', 'B.Tech', 'user206@itbhu.ac.in', '9999999206', '206'),
('207', 'Student 207', 2026, 'MECH', 'B.Tech', 'user207@itbhu.ac.in', '9999999207', '207'),
('208', 'Student 208', 2026, 'CIVIL', 'B.Tech', 'user208@itbhu.ac.in', '9999999208', '208'),
('209', 'Student 209', 2026, 'CHEM', 'B.Tech', 'user209@itbhu.ac.in', '9999999209', '209'),
('210', 'Student 210', 2026, 'CSE', 'B.Tech', 'user210@itbhu.ac.in', '9999999210', '210'),
('211', 'Student 211', 2026, 'ECE', 'B.Tech', 'user211@itbhu.ac.in', '9999999211', '211'),
('212', 'Student 212', 2026, 'META', 'B.Tech', 'user212@itbhu.ac.in', '9999999212', '212'),
('213', 'Student 213', 2026, 'ARCH', 'B.Arch', 'user213@itbhu.ac.in', '9999999213', '213'),
('214', 'Student 214', 2026, 'CSE', 'B.Tech', 'user214@itbhu.ac.in', '9999999214', '214'),
('215', 'Student 215', 2026, 'EEE', 'B.Tech', 'user215@itbhu.ac.in', '9999999215', '215'),
('216', 'Student 216', 2026, 'MECH', 'B.Tech', 'user216@itbhu.ac.in', '9999999216', '216'),
('217', 'Student 217', 2026, 'CIVIL', 'B.Tech', 'user217@itbhu.ac.in', '9999999217', '217'),
('218', 'Student 218', 2026, 'CHEM', 'B.Tech', 'user218@itbhu.ac.in', '9999999218', '218'),
('219', 'Student 219', 2026, 'META', 'B.Tech', 'user219@itbhu.ac.in', '9999999219', '219');

-- 2. Councils
INSERT INTO Council (Council_ID, Name, Description, opt_version) VALUES
(1, 'Science & Tech Council', 'Manages all technical clubs, innovation hubs, and technical fests.', 0),
(2, 'Cultural Council', 'Manages cultural clubs, arts, music, dance, and annual fests.', 0);

-- 3. Clubs
INSERT INTO Club (Club_ID, Name, Council_ID, Is_Recruiting, opt_version) VALUES
(1, 'Programming Club', 1, TRUE, 0),
(2, 'Robotics Club', 1, FALSE, 0),
(3, 'Dance Club', 2, TRUE, 0),
(4, 'Music Club', 2, TRUE, 0),
(5, 'Fine Arts Club', 2, TRUE, 0),
(6, 'Drama Club', 2, FALSE, 0);

-- 4. Verticals
INSERT INTO Vertical (Vertical_ID, Name, Club_ID) VALUES
(1, 'Frontend Development', 1),
(2, 'Backend Development', 1),
(3, 'Competitive Programming', 1),
(4, 'Hardware & Microcontrollers', 2),
(5, 'Classical Dance', 3),
(6, 'Western Dance', 3),
(7, 'Charcoal Sketching', 5);

-- 5. Rooms
INSERT INTO Room (Room_ID) VALUES (101), (102), (201), (202), (301);

-- 6. Room Allocations
INSERT INTO Club_Room_Allocation (Club_ID, Room_ID, Academic_Year, opt_version) VALUES
(1, 101, '2026-2027', 0),
(2, 102, '2026-2027', 0),
(3, 201, '2026-2027', 0);

-- 7. Events
INSERT INTO Event (Event_ID, Name, Club_ID, Event_Date, Academic_Year) VALUES
(1, 'Code Wars 2026', 1, '2026-11-15', '2026-2027'),
(2, 'RoboWars Grand Prix', 2, '2026-12-01', '2026-2027'),
(3, 'Rhythm Night Dance Fest', 3, '2026-11-20', '2026-2027');

-- 8. POR Roles
INSERT INTO POR_Role (Role_ID, Council_ID, Club_ID, Title, Permissions_JSON) VALUES
(1, 1, NULL, 'GenSec', '["MANAGE_MEMBERS", "MANAGE_PORS", "CREATE_FORMS"]'),
(2, 1, NULL, 'Jt. GenSec', '["MANAGE_MEMBERS", "MANAGE_PORS", "CREATE_FORMS"]'),
(3, 1, 1, 'Secretary', '["MANAGE_MEMBERS", "CREATE_FORMS"]'),
(4, 1, 1, 'Jt. Secretary', '["MANAGE_MEMBERS", "CREATE_FORMS"]'),
(5, 1, 1, 'Backend Head', '["MANAGE_MEMBERS"]'),
(6, 1, 1, 'Mentor', '[]'),
(7, 2, NULL, 'GenSec', '["MANAGE_MEMBERS", "MANAGE_PORS", "CREATE_FORMS"]'),
(10, 1, 1, 'SciTech GenSec', '["MANAGE_MEMBERS", "MANAGE_PORS", "CREATE_FORMS"]'),
(11, 2, 3, 'Cultural GenSec', '["MANAGE_MEMBERS", "MANAGE_PORS", "CREATE_FORMS"]'),
(12, 1, 1, 'Prog Secretary', '["MANAGE_MEMBERS", "MANAGE_PORS", "CREATE_FORMS"]'),
(13, 2, 3, 'Dance Secretary', '["MANAGE_MEMBERS", "MANAGE_PORS", "CREATE_FORMS"]'),
(14, 1, 1, 'Prog Events Head', '["MANAGE_MEMBERS", "CREATE_FORMS"]');

-- 9. Club Memberships
INSERT INTO Club_Membership (Membership_ID, Roll_Number, Club_ID, Vertical_ID, Role_ID, Academic_Year, opt_version) VALUES
(1, '101', 1, NULL, 1, '2026-2027', 0),
(2, '102', 2, NULL, 2, '2026-2027', 0),
(3, '103', 1, NULL, 3, '2026-2027', 0),
(4, '104', 1, NULL, 4, '2026-2027', 0),
(5, '105', 1, 2, 5, '2026-2027', 0),
(6, '106', 1, NULL, 6, '2026-2027', 0),
(7, '107', 1, NULL, NULL, '2026-2027', 0),
(8, '24075080', 1, 1, NULL, '2026-2027', 0),
(100, '200', 1, NULL, 10, '2026-2027', 0),
(101, '201', 3, NULL, 11, '2026-2027', 0),
(102, '202', 1, NULL, 12, '2026-2027', 0),
(103, '203', 3, NULL, 13, '2026-2027', 0),
(104, '204', 1, 1, NULL, '2026-2027', 0),
(105, '205', 1, 1, NULL, '2026-2027', 0),
(106, '206', 1, 2, NULL, '2026-2027', 0),
(107, '207', 1, 2, NULL, '2026-2027', 0),
(108, '208', 1, 3, NULL, '2026-2027', 0),
(109, '209', 1, 3, NULL, '2026-2027', 0),
(110, '210', 3, 5, NULL, '2026-2027', 0),
(111, '211', 3, 5, NULL, '2026-2027', 0),
(112, '212', 3, 6, NULL, '2026-2027', 0),
(113, '213', 3, 6, NULL, '2026-2027', 0),
(114, '214', 3, NULL, NULL, '2026-2027', 0);

-- 10. Dynamic Form
INSERT INTO Dynamic_Form (Form_ID, Club_ID, Title, Form_Type, Target_Audience, Questions_JSON, Created_By, opt_version) VALUES
(1, 1, 'Programming Club Recruitment 2026', 'Recruitment', 'ALL', '["Why do you want to join Programming Club?", "What is your primary tech stack or programming language?", "GitHub / Portfolio link (if any)"]', '103', 0),
(2, 3, 'Dance Club Auditions 2026', 'Audition', 'ALL', '["Years of dance experience?", "Preferred dance style (Classical / Western / Contemporary)?"]', '203', 0);

-- 11. Form Submissions
INSERT INTO Form_Submission (Submission_ID, Form_ID, Roll_Number, Answers_JSON, Status) VALUES
(1, 1, '24075002', '{"Why do you want to join?": "Passionate about full-stack web and systems engineering", "Tech stack": "Java, Spring Boot, MySQL", "GitHub": "https://github.com/AbhinavAnand"}', 'Pending'),
(2, 1, '214', '{"Why do you want to join?": "I want to learn backend architectures and cloud deployment", "Tech stack": "Python, C++", "GitHub": "https://github.com/student214"}', 'Pending');

-- 12. System Audit Log
INSERT INTO System_Log (timestamp, actor, action, details) VALUES
(NOW(), '0', 'SYSTEM_INIT', 'Massive database initialization and seed data loaded successfully.');
