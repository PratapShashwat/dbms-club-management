package com.college.clubmanagement.entity;
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

    @ManyToOne
    @JoinColumn(name = "Role_ID")
    private PorRole role;

    @Column(name = "Academic_Year", length = 10)
    private String academicYear;
}