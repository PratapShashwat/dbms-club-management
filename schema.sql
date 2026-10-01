CREATE DATABASE IF NOT EXISTS club_management;
USE club_management;

CREATE TABLE Student (
    Roll_Number VARCHAR(20) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Graduation_Year INT,
    Branch VARCHAR(50),
    Email VARCHAR(100)
);

CREATE TABLE Council (
    Council_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Description TEXT
);

CREATE TABLE Club (
    Club_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Council_ID INT,
    Is_Recruiting BOOLEAN DEFAULT FALSE, /* Added based on discussion */
    FOREIGN KEY (Council_ID) REFERENCES Council(Council_ID)
);

CREATE TABLE Vertical (
    Vertical_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL,
    Club_ID INT,
    FOREIGN KEY (Club_ID) REFERENCES Club(Club_ID)
);

CREATE TABLE Event (
    Event_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(150) NOT NULL,
    Club_ID INT,
    Event_Date DATE,
    Academic_Year VARCHAR(10),
    FOREIGN KEY (Club_ID) REFERENCES Club(Club_ID)
);

CREATE TABLE Room (
    Room_ID INT PRIMARY KEY
);

CREATE TABLE Club_Membership (
    Membership_ID INT AUTO_INCREMENT PRIMARY KEY,
    Roll_Number VARCHAR(20),
    Club_ID INT,
    Vertical_ID INT NULL,
    POR_Title VARCHAR(50) DEFAULT 'Member', /* Titles like Secretary, Vertical Head updated later */
    Academic_Year VARCHAR(10),
    FOREIGN KEY (Roll_Number) REFERENCES Student(Roll_Number),
    FOREIGN KEY (Club_ID) REFERENCES Club(Club_ID),
    FOREIGN KEY (Vertical_ID) REFERENCES Vertical(Vertical_ID)
);

CREATE TABLE Club_Room_Allocation (
    Allocation_ID INT AUTO_INCREMENT PRIMARY KEY,
    Club_ID INT,
    Room_ID INT,
    Academic_Year VARCHAR(10),
    FOREIGN KEY (Club_ID) REFERENCES Club(Club_ID),
    FOREIGN KEY (Room_ID) REFERENCES Room(Room_ID)
);

CREATE TABLE Event_Involvement (
    Involvement_ID INT AUTO_INCREMENT PRIMARY KEY,
    Roll_Number VARCHAR(20),
    Event_ID INT,
    Role_Category VARCHAR(50),
    Specific_Role VARCHAR(50), /* Mentor, Coordinator, Team, etc. */
    Result_Details TEXT,
    FOREIGN KEY (Roll_Number) REFERENCES Student(Roll_Number),
    FOREIGN KEY (Event_ID) REFERENCES Event(Event_ID)
);

CREATE TABLE Form_Membership (
    Form_ID INT AUTO_INCREMENT PRIMARY KEY,
    Roll_Number VARCHAR(20),
    Club_ID INT,
    Vertical_ID INT NULL,
    Statement_Of_Purpose TEXT,
    Status VARCHAR(20) DEFAULT 'Pending',
    Academic_Year VARCHAR(10),
    FOREIGN KEY (Roll_Number) REFERENCES Student(Roll_Number),
    FOREIGN KEY (Club_ID) REFERENCES Club(Club_ID),
    FOREIGN KEY (Vertical_ID) REFERENCES Vertical(Vertical_ID)
);

CREATE TABLE Form_EventReg (
    Form_ID INT AUTO_INCREMENT PRIMARY KEY,
    Roll_Number VARCHAR(20),
    Event_ID INT,
    Applied_Category VARCHAR(50),
    Team_Name VARCHAR(100) NULL,
    Status VARCHAR(20) DEFAULT 'Pending',
    FOREIGN KEY (Roll_Number) REFERENCES Student(Roll_Number),
    FOREIGN KEY (Event_ID) REFERENCES Event(Event_ID)
);

CREATE TABLE Form_RoomAccess (
    Form_ID INT AUTO_INCREMENT PRIMARY KEY,
    Roll_Number VARCHAR(20), /* The Secretary making the request */
    Club_ID INT,             /* Added so we know WHICH club is getting the room */
    Room_ID INT,
    Reason TEXT,
    Status VARCHAR(20) DEFAULT 'Pending',
    FOREIGN KEY (Roll_Number) REFERENCES Student(Roll_Number),
    FOREIGN KEY (Club_ID) REFERENCES Club(Club_ID),
    FOREIGN KEY (Room_ID) REFERENCES Room(Room_ID)
);

