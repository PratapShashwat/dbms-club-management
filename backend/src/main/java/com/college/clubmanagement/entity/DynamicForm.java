package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "Dynamic_Form")
public class DynamicForm {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Form_ID")
    private Integer formId;

    @ManyToOne
    @JoinColumn(name = "Club_ID")
    private Club club;

    @Column(name = "Title", nullable = false, length = 150)
    private String title;

    @Column(name = "Form_Type", nullable = false, length = 50)
    private String formType;

    @Column(name = "Target_Audience", nullable = false, length = 50)
    private String targetAudience;

    @Column(name = "Questions_JSON", columnDefinition = "JSON")
    private String questionsJson;

    @ManyToOne
    @JoinColumn(name = "Created_By")
    private Student createdBy;
}