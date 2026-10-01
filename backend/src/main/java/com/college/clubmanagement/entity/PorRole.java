package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "POR_Role")
public class PorRole {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Role_ID")
    private Integer roleId;

    @ManyToOne
    @JoinColumn(name = "Council_ID")
    private Council council;

    @ManyToOne
    @JoinColumn(name = "Club_ID")
    private Club club;

    @Column(name = "Title", length = 100)
    private String title;

    @Column(name = "Permissions_JSON", columnDefinition = "JSON")
    private String permissionsJson;
}