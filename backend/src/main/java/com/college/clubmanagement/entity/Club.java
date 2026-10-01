package com.college.clubmanagement.entity;
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
}