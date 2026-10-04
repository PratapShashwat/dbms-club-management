package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import jakarta.persistence.Version;
import lombok.Data;

@Data
@Entity
@Table(name = "Club_Membership")
public class ClubMembership {

    @Version
    @Column(name = "opt_version")
    private Long optVersion = 0L;


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

    public Long getOptVersion() { return optVersion; }
    public void setOptVersion(Long optVersion) { this.optVersion = optVersion; }

}