package com.college.clubmanagement.entity;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
@Table(name = "Form_Submission")
public class FormSubmission {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Submission_ID")
    private Integer submissionId;

    @ManyToOne
    @JoinColumn(name = "Form_ID")
    private DynamicForm dynamicForm;

    @ManyToOne
    @JoinColumn(name = "Roll_Number")
    private Student student;

    @Column(name = "Answers_JSON", columnDefinition = "JSON")
    private String answersJson;

    @Column(name = "Status", length = 20)
    private String status = "Pending";
}