package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import jakarta.persistence.Version;
import lombok.Data;

@Data
@Entity
@Table(name = "Council")
public class Council {

    @Version
    @Column(name = "opt_version")
    private Long optVersion = 0L;


    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Council_ID")
    private Integer councilId;

    @Column(name = "Name", nullable = false, length = 100)
    private String name;

    @Column(name = "Description", columnDefinition = "TEXT")
    private String description;

    public Long getOptVersion() { return optVersion; }
    public void setOptVersion(Long optVersion) { this.optVersion = optVersion; }

}