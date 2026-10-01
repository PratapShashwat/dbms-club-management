package com.college.clubmanagement.entity;
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
}