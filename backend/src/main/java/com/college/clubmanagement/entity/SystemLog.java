package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;
@Data
@Entity
@Table(name = "System_Log")
public class SystemLog {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer logId;
    private LocalDateTime timestamp;
    private String actor;
    private String action;
    @Column(length = 1000)
    private String details;
}