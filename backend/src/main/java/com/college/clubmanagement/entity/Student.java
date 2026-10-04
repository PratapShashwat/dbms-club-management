package com.college.clubmanagement.entity;
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

    @Column(name = "Course", length = 50)
    private String course;

    @Column(name = "Email", nullable = false, unique = true, length = 100)
    private String email;
    
    @Column(name = "Phone_Number", length = 15)
    private String phoneNumber;
    
    @Column(name = "Password", length = 100)
    private String password;
}