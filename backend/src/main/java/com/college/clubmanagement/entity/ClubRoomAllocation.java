package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import jakarta.persistence.Version;
import lombok.Data;

@Data
@Entity
@Table(name = "Club_Room_Allocation")
public class ClubRoomAllocation {

    @Version
    @Column(name = "opt_version")
    private Long optVersion = 0L;


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

    public Long getOptVersion() { return optVersion; }
    public void setOptVersion(Long optVersion) { this.optVersion = optVersion; }

}