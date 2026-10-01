package com.college.clubmanagement.entity;
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
}