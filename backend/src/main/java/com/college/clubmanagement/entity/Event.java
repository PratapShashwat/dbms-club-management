package com.college.clubmanagement.entity;
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
}