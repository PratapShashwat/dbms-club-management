import os

entities_dir = r"backend\src\main\java\com\college\clubmanagement\entity"
os.makedirs(entities_dir, exist_ok=True)

files = {}

files["Student.java"] = """package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "Student")
public class Student {
    @Id
    @Column(name = "Roll_Number", length = 20)
    private String rollNumber;

    @Column(name = "Name", nullable = false, length = 100)
    private String name;

    @Column(name = "Graduation_Year")
    private Integer graduationYear;

    @Column(name = "Branch", length = 50)
    private String branch;

    @Column(name = "Email", length = 100)
    private String email;
}"""

files["Council.java"] = """package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "Council")
public class Council {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Council_ID")
    private Integer councilId;

    @Column(name = "Name", nullable = false, length = 100)
    private String name;

    @Column(name = "Description", columnDefinition = "TEXT")
    private String description;
}"""

files["Club.java"] = """package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "Club")
public class Club {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Club_ID")
    private Integer clubId;

    @Column(name = "Name", nullable = false, length = 100)
    private String name;

    @ManyToOne
    @JoinColumn(name = "Council_ID")
    private Council council;

    @Column(name = "Is_Recruiting")
    private Boolean isRecruiting = false;
}"""

files["Vertical.java"] = """package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "Vertical")
public class Vertical {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Vertical_ID")
    private Integer verticalId;

    @Column(name = "Name", nullable = false, length = 50)
    private String name;

    @ManyToOne
    @JoinColumn(name = "Club_ID")
    private Club club;
}"""

files["Event.java"] = """package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDate;

@Data
@Entity
@Table(name = "Event")
public class Event {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Event_ID")
    private Integer eventId;

    @Column(name = "Name", nullable = false, length = 150)
    private String name;

    @ManyToOne
    @JoinColumn(name = "Club_ID")
    private Club club;

    @Column(name = "Event_Date")
    private LocalDate eventDate;

    @Column(name = "Academic_Year", length = 10)
    private String academicYear;
}"""

files["Room.java"] = """package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "Room")
public class Room {
    @Id
    @Column(name = "Room_ID")
    private Integer roomId;
}"""

files["ClubMembership.java"] = """package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "Club_Membership")
public class ClubMembership {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Membership_ID")
    private Integer membershipId;

    @ManyToOne
    @JoinColumn(name = "Roll_Number")
    private Student student;

    @ManyToOne
    @JoinColumn(name = "Club_ID")
    private Club club;

    @ManyToOne
    @JoinColumn(name = "Vertical_ID")
    private Vertical vertical;

    @Column(name = "POR_Title", length = 50)
    private String porTitle = "Member";

    @Column(name = "Academic_Year", length = 10)
    private String academicYear;
}"""

files["ClubRoomAllocation.java"] = """package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "Club_Room_Allocation")
public class ClubRoomAllocation {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Allocation_ID")
    private Integer allocationId;

    @ManyToOne
    @JoinColumn(name = "Club_ID")
    private Club club;

    @ManyToOne
    @JoinColumn(name = "Room_ID")
    private Room room;

    @Column(name = "Academic_Year", length = 10)
    private String academicYear;
}"""

files["EventInvolvement.java"] = """package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "Event_Involvement")
public class EventInvolvement {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Involvement_ID")
    private Integer involvementId;

    @ManyToOne
    @JoinColumn(name = "Roll_Number")
    private Student student;

    @ManyToOne
    @JoinColumn(name = "Event_ID")
    private Event event;

    @Column(name = "Role_Category", length = 50)
    private String roleCategory;

    @Column(name = "Specific_Role", length = 50)
    private String specificRole;

    @Column(name = "Result_Details", columnDefinition = "TEXT")
    private String resultDetails;
}"""

files["FormMembership.java"] = """package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "Form_Membership")
public class FormMembership {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Form_ID")
    private Integer formId;

    @ManyToOne
    @JoinColumn(name = "Roll_Number")
    private Student applicant;

    @ManyToOne
    @JoinColumn(name = "Club_ID")
    private Club club;

    @ManyToOne
    @JoinColumn(name = "Vertical_ID")
    private Vertical vertical;

    @Column(name = "Statement_Of_Purpose", columnDefinition = "TEXT")
    private String statementOfPurpose;

    @Column(name = "Status", length = 20)
    private String status = "Pending";

    @Column(name = "Academic_Year", length = 10)
    private String academicYear;
}"""

files["FormEventReg.java"] = """package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "Form_EventReg")
public class FormEventReg {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Form_ID")
    private Integer formId;

    @ManyToOne
    @JoinColumn(name = "Roll_Number")
    private Student applicant;

    @ManyToOne
    @JoinColumn(name = "Event_ID")
    private Event event;

    @Column(name = "Applied_Category", length = 50)
    private String appliedCategory;

    @Column(name = "Team_Name", length = 100)
    private String teamName;

    @Column(name = "Status", length = 20)
    private String status = "Pending";
}"""

files["FormRoomAccess.java"] = """package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "Form_RoomAccess")
public class FormRoomAccess {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Form_ID")
    private Integer formId;

    @ManyToOne
    @JoinColumn(name = "Roll_Number")
    private Student applicantSecretary;

    @ManyToOne
    @JoinColumn(name = "Club_ID")
    private Club club;

    @ManyToOne
    @JoinColumn(name = "Room_ID")
    private Room room;

    @Column(name = "Reason", columnDefinition = "TEXT")
    private String reason;

    @Column(name = "Status", length = 20)
    private String status = "Pending";
}"""

for filename, content in files.items():
    filepath = os.path.join(entities_dir, filename)
    with open(filepath, 'w') as f:
        f.write(content)

print("All 12 entities generated successfully!")

