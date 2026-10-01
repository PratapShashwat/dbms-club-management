package com.college.clubmanagement.entity;
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
}