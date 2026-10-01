package com.college.clubmanagement.entity;
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
}