package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "Room")
public class Room {
    @Id
    @Column(name = "Room_ID")
    private Integer roomId;
}